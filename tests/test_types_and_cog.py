"""Tests for shared helpers and the cog's help-message builder."""

from __future__ import annotations

from threadit.cog import build_help_message
from threadit.types import DEFAULT_CLIENT_ID, invite_url


class TestInviteUrl:
    def test_int_id(self):
        url = invite_url(12345)
        assert url.startswith("https://discord.com/oauth2/authorize?client_id=12345")

    def test_str_id(self):
        url = invite_url("abc")
        assert url.startswith("https://discord.com/oauth2/authorize?client_id=abc")

    def test_includes_both_required_scopes(self):
        # Without scope= Discord rejects the OAuth flow; without
        # applications.commands the bot can't register slash commands.
        url = invite_url(42)
        assert "scope=bot+applications.commands" in url

    def test_default_client_id_constant_matches_upstream(self):
        # If this changes, self-hosters following the README pre-login would
        # silently end up routed to a different deployment.
        assert DEFAULT_CLIENT_ID == "1386888801229734018"


class TestBuildHelpMessage:
    def test_dm_omits_permission_block(self):
        msg = build_help_message(
            in_guild=False,
            has_required_perms=True,
            missing_required=[],
            missing_optional=[],
            client_id="123",
        )
        assert "Permission Setup Required" not in msg
        assert "Optional Enhancement" not in msg
        assert "All permissions are correctly set up" not in msg

    def test_missing_required_includes_invite_url(self):
        msg = build_help_message(
            in_guild=True,
            has_required_perms=False,
            missing_required=["Embed Links", "Attach Files"],
            missing_optional=[],
            client_id="42",
        )
        assert "Permission Setup Required" in msg
        assert "• Embed Links" in msg
        assert "• Attach Files" in msg
        # Invite URL must use the runtime client_id, not the upstream one.
        assert "client_id=42" in msg
        assert "client_id=1386888801229734018" not in msg

    def test_missing_optional_shows_optional_block(self):
        msg = build_help_message(
            in_guild=True,
            has_required_perms=True,
            missing_required=[],
            missing_optional=["Manage Messages"],
            client_id="42",
        )
        assert "Optional Enhancement" in msg
        assert "Manage Messages" in msg

    def test_all_granted_shows_green_check(self):
        msg = build_help_message(
            in_guild=True,
            has_required_perms=True,
            missing_required=[],
            missing_optional=[],
            client_id="42",
        )
        assert "All permissions are correctly set up" in msg
