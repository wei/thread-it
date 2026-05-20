"""Tests for threadit.permissions.PermissionsService."""

from __future__ import annotations

import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from threadit.permissions import PermissionsService


@pytest.fixture
def perms() -> PermissionsService:
    return PermissionsService(
        get_self_id=lambda: 999,
        get_client_id=lambda: "999",
        logger=logging.getLogger("test-perms"),
    )


def _channel_with_perms(perms_dict: dict[str, bool]):
    """Build a guild channel with a configurable permission set."""
    guild = MagicMock()
    bot_member = MagicMock()
    guild.get_member = MagicMock(return_value=bot_member)

    channel = MagicMock()
    channel.guild = guild
    channel.name = "test-channel"
    channel.permissions_for = MagicMock(return_value=SimpleNamespace(**perms_dict))
    return channel


_ALL_PERMS = {
    "view_channel": True,
    "send_messages": True,
    "send_messages_in_threads": True,
    "create_public_threads": True,
    "read_message_history": True,
    "embed_links": True,
    "attach_files": True,
    "manage_messages": True,
}


class TestValidatePermissions:
    def test_dm_channel_rejected(self, perms):
        dm = MagicMock(spec=[])  # no .guild attribute
        ok, missing_req, missing_opt = perms.validate_permissions(dm)
        assert ok is False
        assert missing_req == ["Not a guild channel"]
        assert missing_opt == []

    def test_bot_not_ready(self):
        p = PermissionsService(
            get_self_id=lambda: None,
            get_client_id=lambda: "999",
            logger=logging.getLogger("test"),
        )
        channel = _channel_with_perms(_ALL_PERMS)
        ok, missing_req, _ = p.validate_permissions(channel)
        assert ok is False
        assert "Bot not yet ready" in missing_req

    def test_bot_not_in_guild(self, perms):
        channel = _channel_with_perms(_ALL_PERMS)
        channel.guild.get_member = MagicMock(return_value=None)
        ok, missing_req, _ = perms.validate_permissions(channel)
        assert ok is False
        assert "Bot not in guild" in missing_req

    def test_all_perms_granted(self, perms):
        channel = _channel_with_perms(_ALL_PERMS)
        ok, missing_req, missing_opt = perms.validate_permissions(channel)
        assert ok is True
        assert missing_req == []
        assert missing_opt == []

    def test_missing_embed_links_blocks(self, perms):
        channel = _channel_with_perms({**_ALL_PERMS, "embed_links": False})
        ok, missing_req, _ = perms.validate_permissions(channel)
        assert ok is False
        assert "Embed Links" in missing_req

    def test_attach_files_required_only_when_has_attachments(self, perms):
        channel = _channel_with_perms({**_ALL_PERMS, "attach_files": False})
        ok_no_att, missing_no_att, _ = perms.validate_permissions(channel, has_attachments=False)
        ok_with_att, missing_with_att, _ = perms.validate_permissions(channel, has_attachments=True)
        assert ok_no_att is True
        assert "Attach Files" not in missing_no_att
        assert ok_with_att is False
        assert "Attach Files" in missing_with_att

    def test_manage_messages_is_optional(self, perms):
        channel = _channel_with_perms({**_ALL_PERMS, "manage_messages": False})
        ok, missing_req, missing_opt = perms.validate_permissions(channel)
        assert ok is True
        assert missing_req == []
        assert missing_opt == ["Manage Messages"]


class TestCheckSpecificPermission:
    def test_dm_returns_false(self, perms):
        dm = MagicMock(spec=[])
        assert perms.check_specific_permission(dm, "send_messages") is False

    def test_granted(self, perms):
        channel = _channel_with_perms(_ALL_PERMS)
        assert perms.check_specific_permission(channel, "manage_messages") is True

    def test_missing(self, perms):
        channel = _channel_with_perms({**_ALL_PERMS, "manage_messages": False})
        assert perms.check_specific_permission(channel, "manage_messages") is False


class TestSendPermissionErrorMessage:
    async def test_first_warning_sends_subsequent_suppressed(self, perms):
        """Regression test for the freshly-booted-host cooldown bug."""
        channel = MagicMock()
        channel.id = 7777
        channel.name = "test"
        channel.send = AsyncMock()

        # Pin monotonic() to small values < cooldown (3600). The old `0.0`
        # sentinel would have suppressed the very first call here.
        monotonic_values = iter([10.0, 11.0, 12.0])
        with (
            patch.object(perms, "check_specific_permission", return_value=True),
            patch("threadit.permissions.time.monotonic", side_effect=lambda: next(monotonic_values)),
        ):
            for _ in range(3):
                await perms.send_permission_error_message(channel, ["Embed Links"])

        assert channel.send.await_count == 1

    async def test_different_channels_independent(self, perms):
        ch_a, ch_b = MagicMock(), MagicMock()
        ch_a.id, ch_b.id = 1, 2
        ch_a.name, ch_b.name = "a", "b"
        ch_a.send = AsyncMock()
        ch_b.send = AsyncMock()

        with patch.object(perms, "check_specific_permission", return_value=True):
            await perms.send_permission_error_message(ch_a, ["Embed Links"])
            await perms.send_permission_error_message(ch_b, ["Embed Links"])

        assert ch_a.send.await_count == 1
        assert ch_b.send.await_count == 1

    async def test_no_send_messages_perm_skips_send(self, perms):
        channel = MagicMock()
        channel.id = 1
        channel.name = "x"
        channel.send = AsyncMock()

        with patch.object(perms, "check_specific_permission", return_value=False):
            await perms.send_permission_error_message(channel, ["Embed Links"])

        channel.send.assert_not_called()
