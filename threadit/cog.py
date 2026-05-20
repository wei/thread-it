"""Cog wiring: gateway listeners and the user-facing `/thread-it` command."""

from __future__ import annotations

import logging
from collections.abc import Callable

import discord
from discord.ext import commands

from .orchestrator import ThreadingOrchestrator
from .permissions import PermissionsService
from .types import invite_url


def build_help_message(
    in_guild: bool,
    has_required_perms: bool,
    missing_required: list[str],
    missing_optional: list[str],
    client_id: str,
) -> str:
    base = (
        "Hi there! I'm Thread It. My purpose is to keep your Discord channels clean "
        "by automatically converting message replies into organized public threads.\n\n"
        "**How I work:**\n"
        "1. When someone replies to a message in a channel, I detect it.\n"
        "2. I then create a new public thread based on the original message.\n"
        "3. The reply (and any subsequent replies to it) will be moved into this new thread.\n"
        "4. I'll also delete the original reply from the main channel and send a temporary "
        "notification to guide users to the new thread.\n\n"
        "**No commands are needed for my core function!** Just reply to a message, and "
        "I'll do the rest."
    )

    if not in_guild:
        return base

    if not has_required_perms:
        permission_list = "\n".join(f"• {perm}" for perm in missing_required)
        return base + (
            "\n\n⚠️ **Permission Setup Required**\n"
            "I'm currently missing some required permissions in this channel:\n\n"
            f"{permission_list}\n\n"
            "**To fix this:**\n"
            "1. Go to Server Settings → Roles\n"
            "2. Find the 'Thread It' role (or @Thread It)\n"
            "3. Enable the missing permissions listed above\n"
            f"4. Or re-invite me with the correct permissions: {invite_url(client_id)}"
        )

    if missing_optional:
        return base + (
            "\n\n📝 **Optional Enhancement**\n"
            "For the best experience, consider granting the 'Manage Messages' permission. "
            "This allows me to clean up the original reply messages after moving them to "
            "threads. Without this permission, I'll still create threads but won't delete "
            "the original replies."
        )

    return base + (
        "\n\n✅ **All permissions are correctly set up!** I'm ready to organize your conversations."
    )


class ThreadItCog(commands.Cog, name="ThreadIt"):
    """
    Dispatches Discord gateway events to the orchestrator and serves the
    hybrid ``/thread-it`` (slash) and ``!thread-it`` (prefix) help command.
    """

    def __init__(
        self,
        bot: commands.Bot,
        orchestrator: ThreadingOrchestrator,
        permissions: PermissionsService,
        *,
        get_client_id: Callable[[], str],
        logger: logging.Logger,
    ) -> None:
        self.bot = bot
        self.orchestrator = orchestrator
        self.permissions = permissions
        self._get_client_id = get_client_id
        self.logger = logger

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        assert self.bot.user is not None
        self.logger.info(f"Bot logged in as {self.bot.user} (ID: {self.bot.user.id})")
        self.logger.info(f"Connected to {len(self.bot.guilds)} guilds")

        self.logger.info("Checking permissions across all guilds...")
        for guild in self.bot.guilds:
            self.permissions.log_guild_permissions(guild)

        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for replies to convert to threads",
        )
        await self.bot.change_presence(activity=activity)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        self.permissions.log_guild_permissions(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        self.logger.info(f"Removed from guild: {guild.name} (ID: {guild.id})")

    # ------------------------------------------------------------------ #
    # Main event
    # ------------------------------------------------------------------ #

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # System "X started a thread" messages: delete ours immediately.
        if (
            message.type == discord.MessageType.thread_created
            and message.author == self.bot.user
        ):
            await self.orchestrator.delete_system_thread_message(message)
            return

        # 1. Ignore bots (including ourselves) to prevent loops.
        if message.author.bot:
            return

        # 2. Ignore non-replies.
        if message.reference is None:
            return

        # 3. Ignore messages already inside a thread.
        if isinstance(message.channel, discord.Thread):
            return

        # 4. Guild-only.
        if message.guild is None:
            return

        self.logger.debug(
            f"Processing reply from {message.author} (ID: {message.author.id}) "
            f"in guild {message.guild.name} (ID: {message.guild.id}), "
            f"channel #{getattr(message.channel, 'name', '?')} (ID: {message.channel.id})"
        )
        await self.orchestrator.process(message)

    # ------------------------------------------------------------------ #
    # Help command — hybrid (works as /thread-it and !thread-it)
    # ------------------------------------------------------------------ #

    @commands.hybrid_command(  # type: ignore[arg-type]
        name="thread-it",
        description="Show Thread It help and permission status for this channel.",
    )
    async def thread_it_help(self, ctx: commands.Context) -> None:
        in_guild = ctx.guild is not None
        if in_guild:
            has_required, missing_required, missing_optional = (
                self.permissions.validate_permissions(ctx.channel)  # type: ignore[arg-type]
            )
        else:
            has_required, missing_required, missing_optional = True, [], []

        message = build_help_message(
            in_guild=in_guild,
            has_required_perms=has_required,
            missing_required=missing_required,
            missing_optional=missing_optional,
            client_id=self._get_client_id(),
        )
        await ctx.reply(message, ephemeral=True if ctx.interaction else False)


async def setup(bot: commands.Bot) -> None:  # pragma: no cover
    """
    discord.ext.commands extension entry point.

    Not used directly — `bot.py` constructs and injects the cog with its
    dependencies because the cog needs handles to a PermissionsService and
    a ThreadingOrchestrator. This stub exists so future `load_extension`
    callers get a clear error.
    """
    raise RuntimeError(
        "ThreadItCog must be constructed with explicit dependencies; "
        "use bot.add_cog(ThreadItCog(...)) instead of load_extension."
    )
