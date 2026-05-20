#!/usr/bin/env python3
"""
Thread It - Discord Bot

A Discord bot that automatically converts message replies into organized public threads.
This keeps main channel feeds clean and ensures follow-up discussions are neatly contained.
"""

import asyncio
import io
import logging
import time

import discord

from config import Config

# Default invite URL client_id used in static error text before login.
# At runtime we prefer self.user.id so self-hosters get a link pointing at
# their own bot, not the upstream deployment.
DEFAULT_CLIENT_ID = "1386888801229734018"


def invite_url(client_id) -> str:
    return f"https://discord.com/oauth2/authorize?client_id={client_id}"


class ThreadItBot(discord.Client):
    """
    Main bot class that handles the core functionality of converting replies to threads.
    """

    def __init__(self):
        # Configure required intents
        intents = discord.Intents.default()
        intents.message_content = True  # Required to read message content
        intents.guilds = True          # Required for guild events
        intents.guild_messages = True  # Required for message events

        # Default to no mentions on any bot-authored send. Specific
        # notifications opt back in to a narrow allow-list.
        super().__init__(
            intents=intents,
            allowed_mentions=discord.AllowedMentions.none(),
        )

        # Per-parent-message locks serialize thread creation when multiple
        # replies arrive for the same parent in quick succession.
        # Value is [lock, waiter_count]; popped when waiter_count drops to 0
        # to avoid an unbounded dict over the bot's lifetime.
        self._parent_locks = {}

        # Per-channel cooldown for in-channel permission warnings, to avoid
        # spamming a misconfigured server on every reply.
        self._permission_warning_sent_at = {}

        # Strong references to fire-and-forget background tasks so the
        # event loop doesn't GC them mid-await ("Task was destroyed but
        # it is pending"). Tasks remove themselves on completion.
        self._background_tasks = set()

        # Configure logging
        self.setup_logging()

    def _client_id(self):
        """Return our bot's client_id once logged in, falling back to default."""
        return str(self.user.id) if self.user else DEFAULT_CLIENT_ID

    def setup_logging(self):
        """Configure logging based on environment variables."""
        # Configure console handler with simpler format for readability
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)

        # Configure root logger
        logging.basicConfig(
            level=Config.LOG_LEVEL,
            handlers=[console_handler]
        )

        # Set discord.py logging to WARNING to reduce noise
        discord_logger = logging.getLogger('discord')
        discord_logger.setLevel(logging.WARNING)

        # Log startup information
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging configured - Level: {Config.LOG_LEVEL}")
        self.logger.info(f"Bot starting up - discord.py version: {discord.__version__}")

    async def on_ready(self):
        """Called when the bot has successfully connected to Discord."""
        self.logger.info(f'Bot logged in as {self.user} (ID: {self.user.id})')
        self.logger.info(f'Connected to {len(self.guilds)} guilds')

        # Log permission status for each guild
        self.logger.info("Checking permissions across all guilds...")
        for guild in self.guilds:
            self.log_guild_permissions(guild)

        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for replies to convert to threads"
        )
        await self.change_presence(activity=activity)

    async def on_guild_join(self, guild):
        """Called when the bot joins a new guild."""
        self.logger.info(f'Joined guild: {guild.name} (ID: {guild.id})')

        # Log permission status for the new guild
        self.log_guild_permissions(guild)

    async def on_guild_remove(self, guild):
        """Called when the bot is removed from a guild."""
        self.logger.info(f'Removed from guild: {guild.name} (ID: {guild.id})')

    async def on_error(self, event, *args, **kwargs):
        """Global error handler for unhandled exceptions."""
        self.logger.exception(f'Unhandled exception in event {event}')

    async def on_message(self, message):
        """
        Main event handler for message creation.
        This is where the core reply-to-thread conversion logic will be implemented.
        """
        # Handle system thread creation messages first (if enabled)
        if (message.type == discord.MessageType.thread_created and
            message.author == self.user):
            await self.delete_system_thread_message(message)
            return

        # Initial validation checks as specified in the design document

        # 1. Ignore messages sent by bots (including ourselves) to prevent loops
        if message.author.bot:
            return

        # Handle help command
        if message.content.lower().startswith("!thread-it"):
            help_message = (
                "Hi there! I'm Thread It. My purpose is to keep your Discord channels clean "
                "by automatically converting message replies into organized public threads.\n\n"
                "**How I work:**\n"
                "1. When someone replies to a message in a channel, I detect it.\n"
                "2. I then create a new public thread based on the original message.\n"
                "3. The reply (and any subsequent replies to it) will be moved into this new thread.\n"
                "4. I'll also delete the original reply from the main channel and send a temporary "
                "notification to guide users to the new thread.\n\n"
                "**No commands are needed for my core function!** Just reply to a message, and I'll do the rest."
            )

            # In a DM the bot has no per-channel permission state to surface,
            # so skip the permission block entirely.
            if message.guild is not None:
                has_required_perms, missing_required, missing_optional = self.validate_permissions(message.channel)

                # Add permission status information
                if not has_required_perms:
                    permission_list = "\n".join(f"• {perm}" for perm in missing_required)
                    help_message += (
                        f"\n\n⚠️ **Permission Setup Required**\n"
                        f"I'm currently missing some required permissions in this channel:\n\n"
                        f"{permission_list}\n\n"
                        "**To fix this:**\n"
                        "1. Go to Server Settings → Roles\n"
                        "2. Find the 'Thread It' role (or @Thread It)\n"
                        "3. Enable the missing permissions listed above\n"
                        f"4. Or re-invite me with the correct permissions: {invite_url(self._client_id())}"
                    )
                elif missing_optional:
                    help_message += (
                        "\n\n📝 **Optional Enhancement**\n"
                        "For the best experience, consider granting the 'Manage Messages' permission. "
                        "This allows me to clean up the original reply messages after moving them to threads. "
                        "Without this permission, I'll still create threads but won't delete the original replies."
                    )
                else:
                    help_message += (
                        "\n\n✅ **All permissions are correctly set up!** I'm ready to organize your conversations."
                    )

            await message.reply(help_message)
            return

        # 2. Ignore messages that are not replies (message.reference is null)
        if message.reference is None:
            return

        # 3. Ignore messages that are already inside a thread
        if isinstance(message.channel, discord.Thread):
            return

        # 4. Only process messages in guild channels (not DMs)
        if message.guild is None:
            return

        # Log that we're processing a valid reply
        self.logger.debug(
            f"Processing reply from {message.author} (ID: {message.author.id}) "
            f"in guild {message.guild.name} (ID: {message.guild.id}), "
            f"channel #{message.channel.name} (ID: {message.channel.id})"
        )

        # Process the reply-to-thread conversion
        await self.process_reply_to_thread(message)

    async def process_reply_to_thread(self, message):
        """
        Process a valid reply message and convert it to a thread.

        Args:
            message: The reply message to process
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # Additional edge case checks
            if not self.validate_processing_conditions(message):
                return

            # Check permissions before proceeding
            has_attachments = bool(message.attachments)
            has_required_perms, missing_required, missing_optional = self.validate_permissions(
                message.channel, has_attachments=has_attachments
            )
            if not has_required_perms:
                self.logger.error(
                    f"Missing required permissions in #{message.channel.name}: {', '.join(missing_required)}"
                )
                # Try to send error message to users if we can
                await self.send_permission_error_message(message.channel, missing_required)
                return

            # Log missing optional permissions for information (but don't stop processing)
            if missing_optional:
                self.logger.info(
                    f"Missing optional permissions in #{message.channel.name}: {', '.join(missing_optional)} "
                    f"(bot will continue with reduced functionality)"
                )

            # Gather information from the reply message as specified in design doc
            reply_info = await self.gather_reply_information(message)

            if reply_info is None:
                await self.log_operation_metrics("gather_reply_info", False, error="Failed to gather info")
                return

            # Serialize per-parent-message so concurrent replies don't race
            # the "thread exists?" check and end up creating duplicates / dropping replies.
            parent_id = reply_info['parent_message'].id
            entry = self._parent_locks.setdefault(parent_id, [asyncio.Lock(), 0])
            entry[1] += 1
            thread = None
            try:
                async with entry[0]:
                    # Re-fetch the parent inside the lock so we pick up a thread
                    # that another coroutine just created.
                    try:
                        parent = await reply_info['channel'].fetch_message(parent_id)
                        reply_info['parent_message'] = parent
                    except discord.NotFound:
                        self.logger.info(
                            f"Parent message {parent_id} deleted before thread creation; skipping"
                        )
                        return
                    except (discord.Forbidden, discord.HTTPException) as e:
                        # Transient or permission issue on re-fetch — proceed with
                        # the parent we already loaded in gather_reply_information.
                        self.logger.warning(
                            f"Re-fetch of parent {parent_id} failed ({e}); using cached copy"
                        )

                    if reply_info['parent_message'].thread is not None:
                        thread = reply_info['parent_message'].thread
                    else:
                        thread = await self.create_thread_from_reply(reply_info)
            finally:
                entry[1] -= 1
                if entry[1] == 0:
                    # Safe pop: under asyncio's single-threaded loop, a zero
                    # waiter count means no other coroutine currently holds a
                    # reference via setdefault, so dropping the entry cannot
                    # race a peer's lock acquisition.
                    self._parent_locks.pop(parent_id, None)

            if thread is None:
                self.logger.warning(f"Failed to create thread for reply {reply_info['message_id']}")
                return

            # Repost the reply content in the thread
            repost_success = await self.repost_reply_in_thread(thread, reply_info)

            if not repost_success:
                # Repost failed (including partial attachment loss). Do NOT
                # delete the original message; the user's content is still
                # only safely available in the source channel.
                self.logger.warning(
                    f"Repost incomplete for reply {reply_info['message_id']}; "
                    f"leaving original message intact to avoid data loss"
                )
                return

            # Clean up messages as specified in design document
            await self.cleanup_messages(thread, reply_info)

            # Log successful completion with metrics
            duration = asyncio.get_event_loop().time() - start_time
            await self.log_operation_metrics("process_reply_to_thread", True, duration)

            self.logger.info(
                f"Successfully processed reply: created thread '{thread.name}', reposted content, "
                f"and cleaned up messages for reply from {reply_info['author']}"
            )

        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            await self.log_operation_metrics("process_reply_to_thread", False, duration, str(e))

            self.logger.exception(
                f"Error processing reply to thread for message {message.id} "
                f"in guild {message.guild.id}: {e}"
            )

    async def gather_reply_information(self, message):
        """
        Gather all necessary information from the reply message.

        Args:
            message: The reply message

        Returns:
            dict: Dictionary containing all reply information, or None if failed
        """
        try:
            # Get the parent message that was replied to
            parent_message = None
            if message.reference and message.reference.message_id:
                try:
                    parent_message = await message.channel.fetch_message(message.reference.message_id)
                except discord.NotFound:
                    self.logger.warning(
                        f"Parent message {message.reference.message_id} not found "
                        f"for reply {message.id}"
                    )
                    return None
                except discord.Forbidden:
                    self.logger.warning(
                        f"No permission to fetch parent message {message.reference.message_id} "
                        f"for reply {message.id}"
                    )
                    return None

            if parent_message is None:
                self.logger.warning(f"Could not retrieve parent message for reply {message.id}")
                return None

            # Gather all the information as specified in the design document
            reply_info = {
                'content': message.content,
                'author': message.author,
                'attachments': list(message.attachments),  # Create a copy of the list
                'embeds': list(message.embeds),  # Create a copy of the list
                'channel': message.channel,
                'parent_message': parent_message,
                'message_id': message.id,
                'created_at': message.created_at
            }

            self.logger.debug(
                f"Gathered reply info: content_length={len(reply_info['content'])}, "
                f"attachments={len(reply_info['attachments'])}, "
                f"embeds={len(reply_info['embeds'])}, "
                f"parent_author={reply_info['parent_message'].author}"
            )

            return reply_info

        except Exception as e:
            self.logger.exception(f"Error gathering reply information for message {message.id}: {e}")
            return None

    async def create_thread_from_reply(self, reply_info):
        """
        Create a public thread from the parent message.

        Args:
            reply_info: Dictionary containing reply information

        Returns:
            discord.Thread: The created thread, or None if failed
        """
        try:
            parent_message = reply_info['parent_message']

            # Generate thread name from parent message content
            thread_name = Config.get_thread_name(parent_message.content)

            # Create public thread on the parent message
            # Using auto_archive_duration from config (24 hours = 1440 minutes)
            thread = await parent_message.create_thread(
                name=thread_name,
                auto_archive_duration=Config.DEFAULT_AUTO_ARCHIVE_DURATION
            )

            self.logger.debug(
                f"Created thread '{thread.name}' (ID: {thread.id}) "
                f"on message {parent_message.id} in channel #{parent_message.channel.name}"
            )

            return thread

        except discord.Forbidden:
            self.logger.error(
                f"Missing permissions to create thread on message {reply_info['parent_message'].id} "
                f"in guild {reply_info['parent_message'].guild.id}"
            )
            return None
        except discord.HTTPException as e:
            self.logger.error(
                f"HTTP error creating thread on message {reply_info['parent_message'].id}: {e}"
            )
            return None
        except Exception as e:
            self.logger.exception(
                f"Unexpected error creating thread on message {reply_info['parent_message'].id}: {e}"
            )
            return None

    async def _build_attachment_files(self, attachments):
        """
        Download attachments and convert them into discord.File objects,
        enforcing the per-attachment size cap so a malicious or unlucky
        upload can't OOM a small host.

        Returns:
            (files, all_succeeded) - all_succeeded is False if any attachment
            was skipped (oversize) or failed to download.
        """
        files = []
        all_succeeded = True
        max_bytes = Config.MAX_ATTACHMENT_BYTES

        for attachment in attachments:
            if attachment.size and attachment.size > max_bytes:
                self.logger.warning(
                    f"Skipping oversize attachment {attachment.filename} "
                    f"({attachment.size} bytes > {max_bytes} byte limit)"
                )
                all_succeeded = False
                continue

            try:
                file_data = await attachment.read()
                files.append(discord.File(
                    fp=io.BytesIO(file_data),
                    filename=attachment.filename,
                    description=attachment.description,
                ))
            except Exception as e:
                self.logger.warning(f"Failed to process attachment {attachment.filename}: {e}")
                all_succeeded = False

        return files, all_succeeded

    async def repost_reply_in_thread(self, thread, reply_info):
        """
        Repost the original reply content in the newly created thread.

        Args:
            thread: The thread to post in
            reply_info: Dictionary containing reply information

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Format the message with attribution as specified in design doc
            author = reply_info['author']
            content = reply_info['content']

            # Create a Discord embed for better visual attribution
            embed = discord.Embed(
                description=content if content else "",
                color=0x5865F2  # Discord's blurple color
            )

            # Set author information with avatar
            embed.set_author(
                name=author.display_name,
                icon_url=author.display_avatar.url
            )

            # Add timestamp
            embed.timestamp = reply_info['created_at']

            # Prepare files for attachments. attachments_ok is False if any
            # attachment was skipped (oversize) or failed to download; the
            # caller uses this to avoid deleting the original message.
            files, attachments_ok = await self._build_attachment_files(reply_info['attachments'])

            # Combine the new embed with any existing embeds from the original message
            all_embeds = [embed] + reply_info['embeds']

            # Send the message with embed, existing embeds, and files
            await thread.send(
                embeds=all_embeds,
                files=files if files else None
            )

            # Add the original message author as a participant to the thread
            try:
                await thread.add_user(author)
                self.logger.debug(f"Added {author.display_name} as participant to thread {thread.id}")
            except discord.Forbidden:
                self.logger.warning(f"Missing permissions to add {author.display_name} to thread {thread.id}")
            except discord.HTTPException as e:
                self.logger.warning(f"HTTP error adding {author.display_name} to thread {thread.id}: {e}")
            except Exception as e:
                self.logger.warning(f"Unexpected error adding {author.display_name} to thread {thread.id}: {e}")

            self.logger.debug(
                f"Reposted reply content in thread {thread.id} with embed attribution: "
                f"content_length={len(content)}, "
                f"attachments={len(reply_info['attachments'])}, "
                f"attachments_reposted={len(files)}, "
                f"original_embeds={len(reply_info['embeds'])}, "
                f"total_embeds={len(all_embeds)}"
            )

            return attachments_ok

        except discord.Forbidden:
            self.logger.error(f"Missing permissions to send message in thread {thread.id}")
            return False
        except discord.HTTPException as e:
            self.logger.error(f"HTTP error sending message to thread {thread.id}: {e}")
            return False
        except Exception as e:
            self.logger.exception(f"Unexpected error reposting in thread {thread.id}: {e}")
            return False

    async def cleanup_messages(self, thread, reply_info):
        """
        Clean up messages as specified in the design document:
        1. Delete the original reply message (if we have manage_messages permission)
        2. Send a temporary notification to guide the user to the thread

        The notification message mentions the user and directs them to continue
        their conversation in the thread, then automatically deletes after 8 seconds.

        Note: System thread creation messages are handled automatically
        in the on_message event handler for better reliability.

        Args:
            thread: The thread that was created
            reply_info: Dictionary containing reply information
        """
        # Check if we have permission to delete messages
        can_delete = self.check_specific_permission(reply_info['channel'], 'manage_messages')

        deletion_successful = False
        if can_delete:
            # Delete the original reply message
            deletion_successful = await self.delete_original_reply(reply_info)
        else:
            self.logger.info(
                f"Skipping message deletion in #{reply_info['channel'].name} - "
                f"missing manage_messages permission (this is optional)"
            )

        # Send temporary notification regardless of deletion success
        # This helps users find the thread even if we couldn't delete the original message
        await self.send_temporary_notification(thread, reply_info, deletion_successful)

    async def delete_original_reply(self, reply_info):
        """
        Delete the original reply message from the main channel.

        Args:
            reply_info: Dictionary containing reply information

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # Get the original message from the channel
            channel = reply_info['channel']
            message_id = reply_info['message_id']

            # Fetch and delete the message
            original_message = await channel.fetch_message(message_id)
            await original_message.delete()

            self.logger.debug(f"Deleted original reply message {message_id} from #{channel.name}")
            return True

        except discord.NotFound:
            # Message was already deleted or doesn't exist
            self.logger.debug(f"Original reply message {reply_info['message_id']} not found (already deleted?)")
            return False
        except discord.Forbidden:
            self.logger.warning(
                f"Missing permissions to delete original reply message {reply_info['message_id']} "
                f"in #{reply_info['channel'].name}"
            )
            return False
        except discord.HTTPException as e:
            self.logger.error(f"HTTP error deleting original reply message {reply_info['message_id']}: {e}")
            return False
        except Exception as e:
            self.logger.exception(f"Unexpected error deleting original reply message {reply_info['message_id']}: {e}")
            return False

    async def send_temporary_notification(self, thread, reply_info, deletion_successful=True):
        """
        Send a temporary notification message directing the user to continue in the thread.
        The notification automatically deletes after 8 seconds.

        Args:
            thread: The thread that was created
            reply_info: Dictionary containing reply information
            deletion_successful: Whether the original message was successfully deleted
        """
        try:
            channel = reply_info['channel']
            user = reply_info['author']

            if deletion_successful:
                notification_content = f"{user.mention}, please continue your conversation in {thread.mention}."
            else:
                notification_content = (
                    f"{user.mention}, I've created a thread for your reply: {thread.mention}. "
                    f"Please continue your conversation there!"
                )

            # Allow mentioning only the addressed user; suppress @everyone /
            # @here / role mentions in case any sneak through the embed.
            allowed = discord.AllowedMentions(
                users=[user], roles=False, everyone=False, replied_user=False
            )

            # Send the notification message
            notification_message = await channel.send(
                notification_content, allowed_mentions=allowed
            )

            # Schedule automatic deletion after 8 seconds (if we have permission)
            if deletion_successful:
                self.logger.debug(
                    f"Sent temporary notification to {user} in #{channel.name}, "
                    f"message will auto-delete in 8 seconds"
                )
                # Defer the auto-delete so the main flow returns promptly and
                # we don't hold the process_reply task open for 8 seconds.
                # Keep a strong reference so the event loop doesn't GC the
                # task mid-await; remove it when done.
                task = asyncio.create_task(self._delete_after(notification_message, 8))
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
            else:
                self.logger.debug(
                    f"Sent notification message {notification_message.id} in #{channel.name} - "
                    f"will not auto delete due to missing manage_messages permission"
                )

        except discord.Forbidden:
            self.logger.warning(
                f"Missing permissions to send notification message in #{reply_info['channel'].name}"
            )
        except discord.HTTPException as e:
            self.logger.error(f"HTTP error sending notification message: {e}")
        except Exception as e:
            self.logger.exception(f"Unexpected error sending temporary notification: {e}")

    async def _delete_after(self, message, delay_seconds):
        """Best-effort deletion of a temporary message after a delay."""
        try:
            await asyncio.sleep(delay_seconds)
            await message.delete()
            self.logger.debug(
                f"Auto-deleted notification message {message.id} in #{getattr(message.channel, 'name', '?')}"
            )
        except discord.NotFound:
            pass
        except discord.Forbidden:
            self.logger.warning(
                f"Lost manage_messages permission before auto-deleting notification {message.id}"
            )
        except discord.HTTPException as e:
            self.logger.warning(f"HTTP error auto-deleting notification {message.id}: {e}")
        except asyncio.CancelledError:
            raise
        except Exception as e:
            self.logger.warning(f"Unexpected error auto-deleting notification {message.id}: {e}")

    async def delete_system_thread_message(self, message):
        """
        Handle system thread creation messages by deleting them immediately.
        This is called from on_message when a system thread creation message is detected.

        Args:
            message: The system thread creation message
        """
        try:
            await message.delete()
            self.logger.debug(f"Deleted system thread creation message {message.id} in #{message.channel.name}")
        except discord.Forbidden:
            self.logger.warning(
                f"Missing permissions to delete system messages in #{message.channel.name}"
            )
        except discord.HTTPException as e:
            self.logger.error(f"HTTP error deleting system thread message {message.id}: {e}")
        except Exception as e:
            self.logger.exception(f"Unexpected error deleting system thread message {message.id}: {e}")

    def validate_permissions(self, channel, has_attachments: bool = False):
        """
        Validate that the bot has necessary permissions in the channel.
        Separates required permissions (bot fails gracefully if missing) from
        optional permissions (bot works without them).

        Args:
            channel: The channel to check permissions for
            has_attachments: When True, attach_files is also required.

        Returns:
            tuple: (has_required_permissions, missing_required_permissions, missing_optional_permissions)
        """
        if not getattr(channel, 'guild', None):
            return False, ["Not a guild channel"], []

        if self.user is None:
            return False, ["Bot not yet ready"], []

        bot_member = channel.guild.get_member(self.user.id)
        if not bot_member:
            return False, ["Bot not in guild"], []

        permissions = channel.permissions_for(bot_member)
        missing_required = []
        missing_optional = []

        # Required permissions - bot cannot function without these.
        # embed_links is needed because we always post via discord.Embed;
        # attach_files is added below only when the reply has attachments.
        required_permissions = [
            ('view_channel', 'View Channels'),
            ('send_messages', 'Send Messages'),
            ('send_messages_in_threads', 'Send Messages in Threads'),
            ('create_public_threads', 'Create Public Threads'),
            ('read_message_history', 'Read Message History'),
            ('embed_links', 'Embed Links'),
        ]

        if has_attachments:
            required_permissions.append(('attach_files', 'Attach Files'))

        # Optional permissions - bot can work without these but with reduced functionality
        optional_permissions = [
            ('manage_messages', 'Manage Messages')
        ]

        for perm_name, perm_display in required_permissions:
            if not getattr(permissions, perm_name, False):
                missing_required.append(perm_display)

        for perm_name, perm_display in optional_permissions:
            if not getattr(permissions, perm_name, False):
                missing_optional.append(perm_display)

        return len(missing_required) == 0, missing_required, missing_optional

    def check_specific_permission(self, channel, permission_name):
        """
        Check if the bot has a specific permission in the channel.

        Args:
            channel: The channel to check permissions for
            permission_name: The permission attribute name (e.g., 'send_messages')

        Returns:
            bool: True if the bot has the permission, False otherwise
        """
        if not getattr(channel, 'guild', None):
            return False

        if self.user is None:
            return False

        bot_member = channel.guild.get_member(self.user.id)
        if not bot_member:
            return False

        permissions = channel.permissions_for(bot_member)
        return getattr(permissions, permission_name, False)

    async def send_permission_error_message(self, channel, missing_required_permissions):
        """
        Send a user-friendly error message about missing permissions.

        Args:
            channel: The channel to send the message to
            missing_required_permissions: List of missing required permission names
        """
        if not self.check_specific_permission(channel, 'send_messages'):
            # Can't send error message if we don't have send_messages permission
            self.logger.error(
                f"Cannot send permission error message in #{channel.name} - missing Send Messages permission"
            )
            return

        # Rate-limit per channel so a misconfigured server doesn't get spammed
        # with the same warning on every reply. Use None (not 0.0) as the
        # "never sent" sentinel: time.monotonic() can be small (< cooldown)
        # on a freshly-booted host, which would otherwise suppress the very
        # first warning.
        now = time.monotonic()
        last_sent = self._permission_warning_sent_at.get(channel.id)
        if last_sent is not None and now - last_sent < Config.PERMISSION_WARNING_COOLDOWN_SECONDS:
            self.logger.debug(
                f"Suppressing duplicate permission warning in #{channel.name} "
                f"(cooldown {Config.PERMISSION_WARNING_COOLDOWN_SECONDS}s)"
            )
            return

        try:
            permission_list = "\n".join(f"• {perm}" for perm in missing_required_permissions)
            error_message = (
                "⚠️ **Thread It Permission Error**\n\n"
                f"I'm missing some required permissions in this channel to function properly:\n\n"
                f"{permission_list}\n\n"
                "**To fix this:**\n"
                "1. Go to Server Settings → Roles\n"
                "2. Find the 'Thread It' role (or @Thread It)\n"
                "3. Enable the missing permissions listed above\n"
                f"4. Or re-invite me with the correct permissions: {invite_url(self._client_id())}\n\n"
            )

            await channel.send(error_message)
            self._permission_warning_sent_at[channel.id] = now
            self.logger.info(f"Sent permission error message to #{channel.name}")

        except discord.Forbidden:
            self.logger.error(f"Failed to send permission error message in #{channel.name} - forbidden")
        except discord.HTTPException as e:
            self.logger.error(f"HTTP error sending permission error message in #{channel.name}: {e}")
        except Exception as e:
            self.logger.exception(f"Unexpected error sending permission error message in #{channel.name}: {e}")

    def log_guild_permissions(self, guild):
        """
        Log the permission status for a guild and its channels.

        Args:
            guild: The guild to check permissions for
        """
        try:
            if self.user is None:
                self.logger.warning(f"Skipping permission log for {guild.name}: bot not yet ready")
                return
            bot_member = guild.get_member(self.user.id)
            if not bot_member:
                self.logger.warning(f"Bot not found as member in guild {guild.name} (ID: {guild.id})")
                return

            # Check guild-level permissions
            guild_permissions = bot_member.guild_permissions
            self.logger.info(f"Guild {guild.name} (ID: {guild.id}) - Bot permissions status:")

            # Log key permissions that might affect bot functionality
            key_guild_permissions = [
                ('view_channel', 'View Channels'),
                ('send_messages', 'Send Messages'),
                ('create_public_threads', 'Create Public Threads'),
                ('embed_links', 'Embed Links'),
                ('attach_files', 'Attach Files'),
                ('manage_messages', 'Manage Messages'),
                ('read_message_history', 'Read Message History')
            ]

            guild_perm_status = []
            for perm_name, perm_display in key_guild_permissions:
                has_perm = getattr(guild_permissions, perm_name, False)
                status = "✓" if has_perm else "✗"
                guild_perm_status.append(f"{status} {perm_display}")

            self.logger.info(f"  Guild-level permissions: {', '.join(guild_perm_status)}")

            # Log text channels where bot might have issues
            problematic_channels = []
            for channel in guild.text_channels:
                has_required, missing_required, _ = self.validate_permissions(channel)
                if not has_required:
                    problematic_channels.append(f"#{channel.name} (missing: {', '.join(missing_required)})")

            if problematic_channels:
                self.logger.warning(f"  Channels with permission issues: {'; '.join(problematic_channels)}")
            else:
                self.logger.info("  All text channels have required permissions ✓")

        except Exception as e:
            self.logger.exception(f"Error logging permissions for guild {guild.name} (ID: {guild.id}): {e}")

    async def log_operation_metrics(self, operation, success, duration=None, error=None):
        """
        Log metrics for monitoring and debugging.

        Args:
            operation: Name of the operation
            success: Whether the operation succeeded
            duration: How long the operation took
            error: Error message if failed
        """
        status = "SUCCESS" if success else "FAILED"
        duration_str = f" ({duration:.2f}s)" if duration else ""

        if success:
            self.logger.info(f"METRICS: {operation} {status}{duration_str}")
        else:
            error_str = f" - {error}" if error else ""
            self.logger.warning(f"METRICS: {operation} {status}{duration_str}{error_str}")

    def validate_processing_conditions(self, message):
        """
        Validate additional edge cases and processing conditions.

        Args:
            message: The message to validate

        Returns:
            bool: True if processing should continue, False otherwise
        """
        # Check if the parent message still exists and is accessible
        if not message.reference or not message.reference.message_id:
            self.logger.debug(f"Message {message.id} has no valid reference")
            return False

        # Check if we're in a valid guild
        if not message.guild:
            self.logger.debug(f"Message {message.id} is not in a guild")
            return False

        # Check if the channel supports threads
        if not hasattr(message.channel, 'create_thread'):
            self.logger.debug(f"Channel #{message.channel.name} does not support thread creation")
            return False

        # Additional validation can be added here for specific edge cases
        return True

def main():
    """Main entry point for the bot."""
    try:
        # Validate configuration
        Config.validate()

        # Create and run the bot
        bot = ThreadItBot()
        bot.run(Config.DISCORD_TOKEN)

    except ValueError as e:
        print(f"Configuration error: {e}")
    except discord.LoginFailure:
        print("Error: Invalid Discord token!")
    except discord.HTTPException as e:
        print(f"HTTP error occurred: {e}")
    except KeyboardInterrupt:
        print("Bot shutdown requested by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == '__main__':
    main()
