#!/usr/bin/env python3
"""
Thread It - Discord Bot

A Discord bot that automatically converts message replies into organized public threads.
This keeps main channel feeds clean and ensures follow-up discussions are neatly contained.
"""

import os
import io
import logging
import asyncio
from typing import Optional
import discord
from discord.ext import commands
from dotenv import load_dotenv
from config import Config

# Load environment variables
load_dotenv()

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

        super().__init__(intents=intents)

        # Configure logging
        self.setup_logging()

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

        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for replies to convert to threads"
        )
        await self.change_presence(activity=activity)

    async def on_guild_join(self, guild):
        """Called when the bot joins a new guild."""
        self.logger.info(f'Joined guild: {guild.name} (ID: {guild.id})')

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
            has_perms, missing_perms = self.validate_permissions(message.channel)
            if not has_perms:
                self.logger.error(
                    f"Missing required permissions in #{message.channel.name}: {', '.join(missing_perms)}"
                )
                return

            # Gather information from the reply message as specified in design doc
            reply_info = await self.gather_reply_information(message)

            if reply_info is None:
                await self.log_operation_metrics("gather_reply_info", False, error="Failed to gather info")
                return

            # Create or retrieve thread and repost content
            if reply_info['parent_message'].thread is not None:
                thread = reply_info['parent_message'].thread
            else:
                thread = await self.create_thread_from_reply(reply_info)

            if thread is None:
                self.logger.warning(f"Failed to create thread for reply {reply_info['message_id']}")
                return

            # Repost the reply content in the thread
            repost_success = await self.repost_reply_in_thread(thread, reply_info)

            if not repost_success:
                self.logger.warning(f"Failed to repost content in thread {thread.id}")
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

            # Prepare files for attachments
            files = []
            if reply_info['attachments']:
                for attachment in reply_info['attachments']:
                    try:
                        # Download and re-upload the attachment
                        file_data = await attachment.read()
                        discord_file = discord.File(
                            fp=io.BytesIO(file_data),
                            filename=attachment.filename,
                            description=attachment.description
                        )
                        files.append(discord_file)
                    except Exception as e:
                        self.logger.warning(f"Failed to process attachment {attachment.filename}: {e}")

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
                f"original_embeds={len(reply_info['embeds'])}, "
                f"total_embeds={len(all_embeds)}"
            )

            return True

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
        1. Delete the original reply message
        2. Send a temporary notification to guide the user to the thread

        The notification message mentions the user and directs them to continue
        their conversation in the thread, then automatically deletes after 8 seconds.

        Note: System thread creation messages are handled automatically
        in the on_message event handler for better reliability.

        Args:
            reply_info: Dictionary containing reply information
        """
        # Delete the original reply message
        deletion_successful = await self.delete_original_reply(reply_info)

        # Send temporary notification only if deletion was successful
        if deletion_successful:
            await self.send_temporary_notification(thread, reply_info)

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

    async def send_temporary_notification(self, thread, reply_info):
        """
        Send a temporary notification message directing the user to continue in the thread.
        The notification automatically deletes after 8 seconds.

        Args:
            reply_info: Dictionary containing reply information
        """
        try:
            channel = reply_info['channel']
            user = reply_info['author']

            notification_content = f"{user.mention}, please continue your conversation in {thread.mention}."

            # Send the notification message
            notification_message = await channel.send(notification_content)

            self.logger.debug(
                f"Sent temporary notification to {user} in #{channel.name}, "
                f"message will auto-delete in 8 seconds"
            )

            # Schedule automatic deletion after 8 seconds
            await asyncio.sleep(8)
            await notification_message.delete()

            self.logger.debug(f"Auto-deleted notification message {notification_message.id} in #{channel.name}")

        except discord.Forbidden:
            self.logger.warning(
                f"Missing permissions to send notification message in #{reply_info['channel'].name}"
            )
        except discord.HTTPException as e:
            self.logger.error(f"HTTP error sending notification message: {e}")
        except Exception as e:
            self.logger.exception(f"Unexpected error sending temporary notification: {e}")

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

    def validate_permissions(self, channel):
        """
        Validate that the bot has necessary permissions in the channel.

        Args:
            channel: The channel to check permissions for

        Returns:
            tuple: (has_permissions, missing_permissions)
        """
        if not channel.guild:
            return False, ["Not a guild channel"]

        bot_member = channel.guild.get_member(self.user.id)
        if not bot_member:
            return False, ["Bot not in guild"]

        permissions = channel.permissions_for(bot_member)
        missing = []

        required_permissions = [
            ('view_channel', 'View Channels'),
            ('send_messages', 'Send Messages'),
            ('send_messages_in_threads', 'Send Messages in Threads'),
            ('create_public_threads', 'Create Public Threads'),
            ('manage_messages', 'Manage Messages'),
            ('read_message_history', 'Read Message History')
        ]

        for perm_name, perm_display in required_permissions:
            if not getattr(permissions, perm_name, False):
                missing.append(perm_display)

        return len(missing) == 0, missing

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
