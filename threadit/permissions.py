"""Permission validation, per-channel cooldown, and user-facing error messages."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

import discord

from config import Config

from .types import invite_url

REQUIRED_PERMISSIONS: list[tuple[str, str]] = [
    ("view_channel", "View Channels"),
    ("send_messages", "Send Messages"),
    ("send_messages_in_threads", "Send Messages in Threads"),
    ("create_public_threads", "Create Public Threads"),
    ("read_message_history", "Read Message History"),
    ("embed_links", "Embed Links"),
]

# Required only when the reply being processed carries attachments.
ATTACHMENTS_PERMISSION: tuple[str, str] = ("attach_files", "Attach Files")

OPTIONAL_PERMISSIONS: list[tuple[str, str]] = [
    ("manage_messages", "Manage Messages"),
]


class PermissionsService:
    """
    Encapsulates permission validation and warning emission.

    The cooldown state (``_warning_sent_at``) is owned here so the rest of
    the bot doesn't have to thread it through call sites.
    """

    def __init__(
        self,
        *,
        get_self_id: Callable[[], int | None],
        get_client_id: Callable[[], str],
        logger: logging.Logger,
    ) -> None:
        self._get_self_id = get_self_id
        self._get_client_id = get_client_id
        self.logger = logger
        # Map channel.id -> last-warned monotonic time. None sentinel means
        # "never sent" (using 0.0 would suppress the first warning on hosts
        # where time.monotonic() < cooldown — e.g. freshly-booted runners).
        self._warning_sent_at: dict[int, float] = {}

    def validate_permissions(
        self,
        channel: discord.abc.GuildChannel | discord.Thread | discord.DMChannel,
        *,
        has_attachments: bool = False,
    ) -> tuple[bool, list[str], list[str]]:
        """
        Check the bot's permissions in ``channel``.

        Returns ``(has_required, missing_required, missing_optional)``.
        """
        guild = getattr(channel, "guild", None)
        if guild is None:
            return False, ["Not a guild channel"], []

        self_id = self._get_self_id()
        if self_id is None:
            return False, ["Bot not yet ready"], []

        bot_member = guild.get_member(self_id)
        if bot_member is None:
            return False, ["Bot not in guild"], []

        permissions = channel.permissions_for(bot_member)
        missing_required: list[str] = []
        missing_optional: list[str] = []

        required = list(REQUIRED_PERMISSIONS)
        if has_attachments:
            required.append(ATTACHMENTS_PERMISSION)

        for perm_name, perm_display in required:
            if not getattr(permissions, perm_name, False):
                missing_required.append(perm_display)

        for perm_name, perm_display in OPTIONAL_PERMISSIONS:
            if not getattr(permissions, perm_name, False):
                missing_optional.append(perm_display)

        return len(missing_required) == 0, missing_required, missing_optional

    def check_specific_permission(
        self,
        channel: discord.abc.GuildChannel | discord.Thread | discord.DMChannel,
        permission_name: str,
    ) -> bool:
        guild = getattr(channel, "guild", None)
        if guild is None:
            return False

        self_id = self._get_self_id()
        if self_id is None:
            return False

        bot_member = guild.get_member(self_id)
        if bot_member is None:
            return False

        permissions = channel.permissions_for(bot_member)
        return bool(getattr(permissions, permission_name, False))

    async def send_permission_error_message(
        self,
        channel: discord.abc.Messageable,
        missing_required_permissions: list[str],
    ) -> None:
        """
        Post a user-facing setup-required message in the channel,
        rate-limited per channel to avoid spamming a misconfigured server.
        """
        # Avoid attempting a send we know will 403.
        if not self.check_specific_permission(channel, "send_messages"):  # type: ignore[arg-type]
            self.logger.error(
                f"Cannot send permission error message in #{getattr(channel, 'name', '?')} "
                f"- missing Send Messages permission"
            )
            return

        now = time.monotonic()
        channel_id: int = getattr(channel, "id", 0)
        last_sent = self._warning_sent_at.get(channel_id)
        if last_sent is not None and now - last_sent < Config.PERMISSION_WARNING_COOLDOWN_SECONDS:
            self.logger.debug(
                f"Suppressing duplicate permission warning in #{getattr(channel, 'name', '?')} "
                f"(cooldown {Config.PERMISSION_WARNING_COOLDOWN_SECONDS}s)"
            )
            return

        try:
            permission_list = "\n".join(f"• {perm}" for perm in missing_required_permissions)
            error_message = (
                "⚠️ **Thread It Permission Error**\n\n"
                "I'm missing some required permissions in this channel to function properly:\n\n"
                f"{permission_list}\n\n"
                "**To fix this:**\n"
                "1. Go to Server Settings → Roles\n"
                "2. Find the 'Thread It' role (or @Thread It)\n"
                "3. Enable the missing permissions listed above\n"
                f"4. Or re-invite me with the correct permissions: {invite_url(self._get_client_id())}\n\n"
            )
            await channel.send(error_message)
            self._warning_sent_at[channel_id] = now
            self.logger.info(f"Sent permission error message to #{getattr(channel, 'name', '?')}")
        except discord.Forbidden:
            self.logger.error(
                f"Failed to send permission error message in #{getattr(channel, 'name', '?')} - forbidden"
            )
        except discord.HTTPException as e:
            self.logger.error(
                f"HTTP error sending permission error message in #{getattr(channel, 'name', '?')}: {e}"
            )
        except Exception as e:
            self.logger.exception(
                f"Unexpected error sending permission error message in "
                f"#{getattr(channel, 'name', '?')}: {e}"
            )

    def log_guild_permissions(self, guild: discord.Guild) -> None:
        """Log the bot's permission status for a guild and its text channels."""
        try:
            self_id = self._get_self_id()
            if self_id is None:
                self.logger.warning(f"Skipping permission log for {guild.name}: bot not yet ready")
                return
            bot_member = guild.get_member(self_id)
            if bot_member is None:
                self.logger.warning(f"Bot not found as member in guild {guild.name} (ID: {guild.id})")
                return

            guild_permissions = bot_member.guild_permissions
            self.logger.info(f"Guild {guild.name} (ID: {guild.id}) - Bot permissions status:")

            key_guild_permissions: list[tuple[str, str]] = [
                ("view_channel", "View Channels"),
                ("send_messages", "Send Messages"),
                ("create_public_threads", "Create Public Threads"),
                ("embed_links", "Embed Links"),
                ("attach_files", "Attach Files"),
                ("manage_messages", "Manage Messages"),
                ("read_message_history", "Read Message History"),
            ]

            statuses = [
                f"{'✓' if getattr(guild_permissions, name, False) else '✗'} {display}"
                for name, display in key_guild_permissions
            ]
            self.logger.info(f"  Guild-level permissions: {', '.join(statuses)}")

            problematic_channels: list[str] = []
            for channel in guild.text_channels:
                has_required, missing_required, _ = self.validate_permissions(channel)
                if not has_required:
                    problematic_channels.append(
                        f"#{channel.name} (missing: {', '.join(missing_required)})"
                    )

            if problematic_channels:
                self.logger.warning(
                    f"  Channels with permission issues: {'; '.join(problematic_channels)}"
                )
            else:
                self.logger.info("  All text channels have required permissions ✓")
        except Exception as e:
            self.logger.exception(
                f"Error logging permissions for guild {guild.name} (ID: {guild.id}): {e}"
            )
