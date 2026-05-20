"""Smoke test: bot.build_bot() + cog wiring + /thread-it command registration.

Catches a class of regressions (decorator typo, cog name change, missing
add_cog call, slash command name change) at unit-test speed without
needing a real Discord gateway.
"""

from __future__ import annotations

import logging

import pytest

import bot
from threadit.cog import ThreadItCog
from threadit.orchestrator import ThreadingOrchestrator
from threadit.permissions import PermissionsService


def _wire(bot_instance):
    """Mirror bot.run()'s service+cog wiring without starting the gateway."""
    permissions = PermissionsService(
        get_self_id=lambda: None,
        get_client_id=lambda: "999",
        logger=logging.getLogger("test"),
    )
    orchestrator = ThreadingOrchestrator(
        permissions=permissions,
        logger=logging.getLogger("test"),
    )
    cog = ThreadItCog(
        bot_instance,
        orchestrator,
        permissions,
        get_client_id=lambda: "999",
        logger=logging.getLogger("test"),
    )
    return cog


class TestBuildBot:
    def test_build_bot_returns_commands_bot_with_required_intents(self):
        from discord.ext import commands

        b = bot.build_bot()
        assert isinstance(b, commands.Bot)
        assert b.intents.message_content is True
        assert b.intents.guilds is True
        assert b.intents.guild_messages is True
        assert b.allowed_mentions is not None
        assert b.allowed_mentions.everyone is False

    async def test_cog_loads_and_registers_thread_it_command(self):
        b = bot.build_bot()
        cog = _wire(b)
        await b.add_cog(cog)

        # The hybrid command must be discoverable both as a prefix command
        # (via Bot.get_command) and as a slash command (via Bot.tree).
        assert b.get_command("thread-it") is not None, "prefix command missing"
        slash_names = [c.name for c in b.tree.get_commands()]
        assert "thread-it" in slash_names, f"slash command missing; tree has {slash_names}"
        await b.close()

    @pytest.mark.parametrize("listener_name", ["on_message", "on_ready", "on_guild_join"])
    async def test_cog_listeners_are_registered(self, listener_name):
        b = bot.build_bot()
        cog = _wire(b)
        await b.add_cog(cog)

        listeners = b.extra_events.get(listener_name, [])
        assert any(
            getattr(coro, "__qualname__", "").startswith("ThreadItCog.")
            for coro in listeners
        ), f"ThreadItCog.{listener_name} not registered (have: {listeners})"
        await b.close()
