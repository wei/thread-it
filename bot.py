#!/usr/bin/env python3
"""
Thread It — entry point.

Sets up logging, builds the discord.ext.commands Bot, constructs the
services and cog, syncs the slash-command tree, and runs the gateway.
"""

from __future__ import annotations

import asyncio
import logging
import sys

import discord
from discord.ext import commands

from config import Config
from threadit.cog import ThreadItCog
from threadit.orchestrator import ThreadingOrchestrator
from threadit.permissions import PermissionsService
from threadit.types import DEFAULT_CLIENT_ID

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure root logger and quiet discord.py to WARNING."""
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logging.basicConfig(level=Config.LOG_LEVEL, handlers=[handler])
    logging.getLogger("discord").setLevel(logging.WARNING)
    logger.info(f"Logging configured - Level: {Config.LOG_LEVEL}")
    logger.info(f"Bot starting up - discord.py version: {discord.__version__}")


def build_bot() -> commands.Bot:
    """Construct the discord.py Bot with the intents/defaults Thread It needs."""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.guild_messages = True

    return commands.Bot(
        # Prefix is kept only because hybrid commands need one for the text
        # form; the actual user-facing surface is `/thread-it` (slash).
        command_prefix="!",
        intents=intents,
        allowed_mentions=discord.AllowedMentions.none(),
        help_command=None,
    )


async def run() -> None:
    setup_logging()
    Config.validate()

    bot = build_bot()

    permissions = PermissionsService(
        get_self_id=lambda: bot.user.id if bot.user else None,
        get_client_id=lambda: str(bot.user.id) if bot.user else DEFAULT_CLIENT_ID,
        logger=logging.getLogger("threadit.permissions"),
    )
    orchestrator = ThreadingOrchestrator(
        permissions=permissions,
        logger=logging.getLogger("threadit.orchestrator"),
    )
    cog = ThreadItCog(
        bot,
        orchestrator,
        permissions,
        get_client_id=lambda: str(bot.user.id) if bot.user else DEFAULT_CLIENT_ID,
        logger=logging.getLogger("threadit.cog"),
    )
    await bot.add_cog(cog)

    @bot.event
    async def setup_hook() -> None:
        # Push the latest slash-command definitions to Discord. Global sync
        # can take up to an hour to propagate; users can also force-sync per
        # guild if they need faster iteration.
        try:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} application command(s)")
        except Exception as exc:
            logger.warning(f"Failed to sync application commands: {exc}")

    assert Config.DISCORD_TOKEN is not None  # narrowed by Config.validate()
    # `async with bot:` guarantees bot.close() (HTTP session, websocket,
    # background tasks) runs on shutdown — including the exception path —
    # so the event loop tears down cleanly under container restarts and
    # test runners.
    async with bot:
        await bot.start(Config.DISCORD_TOKEN)


def main() -> None:
    try:
        asyncio.run(run())
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)
    except discord.LoginFailure:
        print("Error: Invalid Discord token!", file=sys.stderr)
        sys.exit(1)
    except discord.HTTPException as exc:
        print(f"HTTP error occurred: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Bot shutdown requested by user.", file=sys.stderr)
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
