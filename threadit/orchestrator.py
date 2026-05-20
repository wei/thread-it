"""Reply-to-thread orchestration: gather, lock, create, repost, cleanup."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import replace

import discord

from config import Config

from .attachments import build_attachment_files
from .permissions import PermissionsService
from .types import ReplyInfo


class ThreadingOrchestrator:
    """
    The bulk of the reply→thread flow. Holds the per-parent serialization
    locks and the background-task set for fire-and-forget auto-deletion.
    """

    def __init__(
        self,
        *,
        permissions: PermissionsService,
        logger: logging.Logger,
    ) -> None:
        self.permissions = permissions
        self.logger = logger
        # See _with_parent_lock for invariants.
        self._parent_locks: dict[int, list] = {}
        # Strong references to fire-and-forget background tasks so the event
        # loop doesn't GC them mid-await ("Task was destroyed but it is
        # pending"). Tasks remove themselves on completion.
        self._background_tasks: set[asyncio.Task] = set()

    # ------------------------------------------------------------------ #
    # Per-parent serialization
    # ------------------------------------------------------------------ #

    @asynccontextmanager
    async def _with_parent_lock(self, parent_id: int):
        """
        Serialize concurrent work on the same parent message and pop the
        dict entry when the last waiter releases.

        Single-threaded event loop invariant: when waiter_count hits zero
        inside the finally, no other coroutine currently holds a reference
        to the lock via setdefault, so removing the entry cannot race a
        peer's acquisition.
        """
        entry = self._parent_locks.setdefault(parent_id, [asyncio.Lock(), 0])
        entry[1] += 1
        try:
            async with entry[0]:
                yield
        finally:
            entry[1] -= 1
            if entry[1] == 0:
                self._parent_locks.pop(parent_id, None)

    # ------------------------------------------------------------------ #
    # Top-level entry
    # ------------------------------------------------------------------ #

    async def process(self, message: discord.Message) -> None:
        """Convert a valid reply message into a thread, or do nothing."""
        start_time = asyncio.get_event_loop().time()

        try:
            if not self._validate_processing_conditions(message):
                return

            # _validate_processing_conditions confirmed the channel has
            # `create_thread` and message is in a guild — narrow the type
            # so the rest of the flow doesn't need a cascade of ignores.
            assert isinstance(
                message.channel,
                discord.TextChannel | discord.VoiceChannel | discord.StageChannel,
            ), f"unexpected channel type for guild reply: {type(message.channel).__name__}"
            channel = message.channel

            has_attachments = bool(message.attachments)
            has_required_perms, missing_required, missing_optional = (
                self.permissions.validate_permissions(
                    channel, has_attachments=has_attachments
                )
            )
            if not has_required_perms:
                self.logger.error(
                    f"Missing required permissions in #{channel.name}: "
                    f"{', '.join(missing_required)}"
                )
                await self.permissions.send_permission_error_message(
                    channel, missing_required
                )
                return

            if missing_optional:
                self.logger.info(
                    f"Missing optional permissions in #{channel.name}: "
                    f"{', '.join(missing_optional)} "
                    "(bot will continue with reduced functionality)"
                )

            reply_info = await self.gather_reply_information(message, channel)
            if reply_info is None:
                self._log_metrics("gather_reply_info", False, error="Failed to gather info")
                return

            parent_id = reply_info.parent_message.id
            thread: discord.Thread | None = None
            async with self._with_parent_lock(parent_id):
                # Re-fetch the parent inside the lock so we pick up a thread
                # that another coroutine just created.
                try:
                    parent = await reply_info.channel.fetch_message(parent_id)
                    reply_info = replace(reply_info, parent_message=parent)
                except discord.NotFound:
                    self.logger.info(
                        f"Parent message {parent_id} deleted before thread creation; skipping"
                    )
                    return
                except (discord.Forbidden, discord.HTTPException) as e:
                    # Transient or permission issue on re-fetch — proceed
                    # with the parent we already loaded.
                    self.logger.warning(
                        f"Re-fetch of parent {parent_id} failed ({e}); using cached copy"
                    )

                if reply_info.parent_message.thread is not None:
                    thread = reply_info.parent_message.thread
                else:
                    thread = await self.create_thread_from_reply(reply_info)

            if thread is None:
                self.logger.warning(
                    f"Failed to create thread for reply {reply_info.message_id}"
                )
                return

            repost_success = await self.repost_reply_in_thread(thread, reply_info)
            if not repost_success:
                # Repost failed (including partial attachment loss). Do NOT
                # delete the original message; the user's content is still
                # only safely available in the source channel.
                self.logger.warning(
                    f"Repost incomplete for reply {reply_info.message_id}; "
                    "leaving original message intact to avoid data loss"
                )
                return

            await self.cleanup_messages(thread, reply_info)

            duration = asyncio.get_event_loop().time() - start_time
            self._log_metrics("process_reply_to_thread", True, duration)
            self.logger.info(
                f"Successfully processed reply: created thread '{thread.name}', "
                f"reposted content, and cleaned up messages for reply from {reply_info.author}"
            )

        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            self._log_metrics("process_reply_to_thread", False, duration, str(e))
            self.logger.exception(
                f"Error processing reply to thread for message {message.id} "
                f"in guild {message.guild.id if message.guild else 'DM'}: {e}"
            )

    # ------------------------------------------------------------------ #
    # Sub-steps
    # ------------------------------------------------------------------ #

    def _validate_processing_conditions(self, message: discord.Message) -> bool:
        if not message.reference or not message.reference.message_id:
            self.logger.debug(f"Message {message.id} has no valid reference")
            return False
        if message.guild is None:
            self.logger.debug(f"Message {message.id} is not in a guild")
            return False
        if not hasattr(message.channel, "create_thread"):
            self.logger.debug(
                f"Channel #{getattr(message.channel, 'name', '?')} does not support thread creation"
            )
            return False
        return True

    async def gather_reply_information(
        self,
        message: discord.Message,
        channel: discord.TextChannel | discord.VoiceChannel | discord.StageChannel,
    ) -> ReplyInfo | None:
        """Fetch the parent message and pack everything into a ReplyInfo."""
        try:
            if not (message.reference and message.reference.message_id):
                return None
            parent_message_id = message.reference.message_id

            try:
                parent_message = await channel.fetch_message(parent_message_id)
            except discord.NotFound:
                self.logger.warning(
                    f"Parent message {parent_message_id} not found for reply {message.id}"
                )
                return None
            except discord.Forbidden:
                self.logger.warning(
                    f"No permission to fetch parent message {parent_message_id} "
                    f"for reply {message.id}"
                )
                return None

            info = ReplyInfo(
                content=message.content,
                author=message.author,
                attachments=list(message.attachments),
                embeds=list(message.embeds),
                channel=channel,
                parent_message=parent_message,
                message_id=message.id,
                created_at=message.created_at,
            )
            self.logger.debug(
                f"Gathered reply info: content_length={len(info.content)}, "
                f"attachments={len(info.attachments)}, embeds={len(info.embeds)}, "
                f"parent_author={info.parent_message.author}"
            )
            return info
        except Exception as e:
            self.logger.exception(f"Error gathering reply information for message {message.id}: {e}")
            return None

    async def create_thread_from_reply(self, reply_info: ReplyInfo) -> discord.Thread | None:
        try:
            parent_message = reply_info.parent_message
            thread_name = Config.get_thread_name(parent_message.content)
            thread = await parent_message.create_thread(
                name=thread_name,
                auto_archive_duration=Config.DEFAULT_AUTO_ARCHIVE_DURATION,  # type: ignore[arg-type]
            )
            self.logger.debug(
                f"Created thread '{thread.name}' (ID: {thread.id}) on message "
                f"{parent_message.id} in channel "
                f"#{getattr(parent_message.channel, 'name', '?')}"
            )
            return thread
        except discord.Forbidden:
            guild_id = reply_info.parent_message.guild.id if reply_info.parent_message.guild else "?"
            self.logger.error(
                f"Missing permissions to create thread on message {reply_info.parent_message.id} "
                f"in guild {guild_id}"
            )
            return None
        except discord.HTTPException as e:
            self.logger.error(
                f"HTTP error creating thread on message {reply_info.parent_message.id}: {e}"
            )
            return None
        except Exception as e:
            self.logger.exception(
                f"Unexpected error creating thread on message {reply_info.parent_message.id}: {e}"
            )
            return None

    async def repost_reply_in_thread(
        self, thread: discord.Thread, reply_info: ReplyInfo
    ) -> bool:
        """
        Repost the original reply content in the thread.

        Returns ``False`` if any attachment could not be re-uploaded, so the
        caller knows to preserve the original message.
        """
        try:
            author = reply_info.author
            content = reply_info.content

            embed = discord.Embed(description=content or "", color=0x5865F2)
            embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)
            embed.timestamp = reply_info.created_at

            files, attachments_ok = await build_attachment_files(
                reply_info.attachments,
                max_bytes=Config.MAX_ATTACHMENT_BYTES,
                logger=self.logger,
            )

            all_embeds = [embed, *reply_info.embeds]
            if files:
                await thread.send(embeds=all_embeds, files=files)
            else:
                await thread.send(embeds=all_embeds)

            try:
                await thread.add_user(author)
                self.logger.debug(
                    f"Added {author.display_name} as participant to thread {thread.id}"
                )
            except discord.Forbidden:
                self.logger.warning(
                    f"Missing permissions to add {author.display_name} to thread {thread.id}"
                )
            except discord.HTTPException as e:
                self.logger.warning(
                    f"HTTP error adding {author.display_name} to thread {thread.id}: {e}"
                )
            except Exception as e:
                self.logger.warning(
                    f"Unexpected error adding {author.display_name} to thread {thread.id}: {e}"
                )

            self.logger.debug(
                f"Reposted reply content in thread {thread.id}: "
                f"content_length={len(content)}, attachments={len(reply_info.attachments)}, "
                f"attachments_reposted={len(files)}, original_embeds={len(reply_info.embeds)}, "
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

    async def cleanup_messages(self, thread: discord.Thread, reply_info: ReplyInfo) -> None:
        can_delete = self.permissions.check_specific_permission(
            reply_info.channel, "manage_messages"
        )

        deletion_successful = False
        if can_delete:
            deletion_successful = await self.delete_original_reply(reply_info)
        else:
            self.logger.info(
                f"Skipping message deletion in #{reply_info.channel.name} - "
                "missing manage_messages permission (this is optional)"
            )

        await self.send_temporary_notification(thread, reply_info, deletion_successful)

    async def delete_original_reply(self, reply_info: ReplyInfo) -> bool:
        try:
            original_message = await reply_info.channel.fetch_message(reply_info.message_id)
            await original_message.delete()
            self.logger.debug(
                f"Deleted original reply message {reply_info.message_id} "
                f"from #{reply_info.channel.name}"
            )
            return True
        except discord.NotFound:
            self.logger.debug(
                f"Original reply message {reply_info.message_id} not found (already deleted?)"
            )
            return False
        except discord.Forbidden:
            self.logger.warning(
                f"Missing permissions to delete original reply message {reply_info.message_id} "
                f"in #{reply_info.channel.name}"
            )
            return False
        except discord.HTTPException as e:
            self.logger.error(
                f"HTTP error deleting original reply message {reply_info.message_id}: {e}"
            )
            return False
        except Exception as e:
            self.logger.exception(
                f"Unexpected error deleting original reply message {reply_info.message_id}: {e}"
            )
            return False

    async def send_temporary_notification(
        self,
        thread: discord.Thread,
        reply_info: ReplyInfo,
        deletion_successful: bool = True,
    ) -> None:
        channel = reply_info.channel
        user = reply_info.author

        if deletion_successful:
            notification_content = (
                f"{user.mention}, please continue your conversation in {thread.mention}."
            )
        else:
            notification_content = (
                f"{user.mention}, I've created a thread for your reply: {thread.mention}. "
                "Please continue your conversation there!"
            )

        allowed = discord.AllowedMentions(
            users=[user], roles=False, everyone=False, replied_user=False
        )

        try:
            notification_message = await channel.send(
                notification_content, allowed_mentions=allowed
            )
        except discord.Forbidden:
            self.logger.warning(
                f"Missing permissions to send notification message in #{channel.name}"
            )
            return
        except discord.HTTPException as e:
            self.logger.error(f"HTTP error sending notification message: {e}")
            return
        except Exception as e:
            self.logger.exception(f"Unexpected error sending temporary notification: {e}")
            return

        if not deletion_successful:
            self.logger.debug(
                f"Sent notification message {notification_message.id} in #{channel.name} - "
                "will not auto-delete because we don't own manage_messages"
            )
            return

        # Defer the auto-delete so the main flow returns promptly.
        task = asyncio.create_task(self._delete_after(notification_message, 8))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    async def _delete_after(self, message: discord.Message, delay_seconds: float) -> None:
        try:
            await asyncio.sleep(delay_seconds)
            await message.delete()
            self.logger.debug(
                f"Auto-deleted notification message {message.id} in "
                f"#{getattr(message.channel, 'name', '?')}"
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

    async def delete_system_thread_message(self, message: discord.Message) -> None:
        try:
            await message.delete()
            self.logger.debug(
                f"Deleted system thread creation message {message.id} "
                f"in #{getattr(message.channel, 'name', '?')}"
            )
        except discord.Forbidden:
            self.logger.warning(
                f"Missing permissions to delete system messages in "
                f"#{getattr(message.channel, 'name', '?')}"
            )
        except discord.HTTPException as e:
            self.logger.error(f"HTTP error deleting system thread message {message.id}: {e}")
        except Exception as e:
            self.logger.exception(
                f"Unexpected error deleting system thread message {message.id}: {e}"
            )

    def _log_metrics(
        self,
        operation: str,
        success: bool,
        duration: float | None = None,
        error: str | None = None,
    ) -> None:
        status = "SUCCESS" if success else "FAILED"
        duration_str = f" ({duration:.2f}s)" if duration else ""
        if success:
            self.logger.info(f"METRICS: {operation} {status}{duration_str}")
        else:
            error_str = f" - {error}" if error else ""
            self.logger.warning(f"METRICS: {operation} {status}{duration_str}{error_str}")


