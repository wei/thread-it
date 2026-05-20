"""Tests for ThreadItBot helpers that don't require a live Discord gateway."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

import bot

# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture
def threadit_bot():
    """A ThreadItBot instance with the Discord gateway hooks bypassed."""
    # Avoid invoking the real discord.Client setup (network, signal handlers).
    with patch.object(discord.Client, "__init__", lambda self, *a, **kw: None):
        b = bot.ThreadItBot.__new__(bot.ThreadItBot)
        b._parent_locks = {}
        b._permission_warning_sent_at = {}
        b._background_tasks = set()
        # Replicate the logger setup ThreadItBot.setup_logging() does, minus
        # global logging.basicConfig side effects.
        import logging

        b.logger = logging.getLogger("test-threadit")
        # discord.Client subclasses expose .user; default to a stand-in.
        b._user = SimpleNamespace(id=999, mention="<@999>")
        yield b


def _make_attachment(filename: str, size: int, read_data: bytes | None = None,
                     read_exc: Exception | None = None):
    """Build a discord.Attachment-shaped mock."""
    att = MagicMock(spec=discord.Attachment)
    att.filename = filename
    att.size = size
    att.description = None
    if read_exc is not None:
        att.read = AsyncMock(side_effect=read_exc)
    else:
        att.read = AsyncMock(return_value=read_data or b"x" * min(size, 16))
    return att


# --------------------------------------------------------------------------- #
# invite_url + _client_id
# --------------------------------------------------------------------------- #


class TestInviteUrl:
    def test_uses_provided_client_id(self):
        assert bot.invite_url(12345) == "https://discord.com/oauth2/authorize?client_id=12345"

    def test_default_client_id_constant_matches_upstream(self):
        # If this changes, self-hosters following the README pre-login will
        # silently end up routed to a different deployment.
        assert bot.DEFAULT_CLIENT_ID == "1386888801229734018"


class TestClientIdHelper:
    def test_returns_default_when_not_logged_in(self, threadit_bot):
        threadit_bot._user = None
        # _client_id reads self.user; discord.Client makes it a property,
        # but our test instance is bare so we expose it via attribute.
        with patch.object(type(threadit_bot), "user", None, create=True):
            assert threadit_bot._client_id() == bot.DEFAULT_CLIENT_ID

    def test_returns_self_user_id_when_logged_in(self, threadit_bot):
        with patch.object(type(threadit_bot), "user",
                          SimpleNamespace(id=42), create=True):
            assert threadit_bot._client_id() == "42"


# --------------------------------------------------------------------------- #
# _build_attachment_files
# --------------------------------------------------------------------------- #


class TestBuildAttachmentFiles:
    async def test_empty_list_returns_empty_and_ok(self, threadit_bot):
        files, ok = await threadit_bot._build_attachment_files([])
        assert files == []
        assert ok is True

    async def test_small_attachment_downloaded(self, threadit_bot):
        att = _make_attachment("hi.txt", size=10, read_data=b"hello")
        files, ok = await threadit_bot._build_attachment_files([att])
        assert ok is True
        assert len(files) == 1
        assert files[0].filename == "hi.txt"

    async def test_oversize_attachment_is_skipped_and_flagged(self, threadit_bot):
        # 30 MiB > default 25 MiB cap
        att = _make_attachment("big.bin", size=30 * 1024 * 1024)
        files, ok = await threadit_bot._build_attachment_files([att])
        assert ok is False, "oversize attachment must mark the batch as failed"
        assert files == []
        att.read.assert_not_called()

    async def test_download_failure_is_caught_and_flagged(self, threadit_bot):
        att = _make_attachment("flaky.txt", size=10, read_exc=RuntimeError("boom"))
        files, ok = await threadit_bot._build_attachment_files([att])
        assert ok is False
        assert files == []

    async def test_partial_success_still_flags_overall_failure(self, threadit_bot):
        good = _make_attachment("ok.txt", size=10, read_data=b"ok")
        bad = _make_attachment("huge.bin", size=99 * 1024 * 1024)
        files, ok = await threadit_bot._build_attachment_files([good, bad])
        # The good attachment is kept; ok=False signals "don't delete original".
        assert ok is False
        assert len(files) == 1
        assert files[0].filename == "ok.txt"


# --------------------------------------------------------------------------- #
# validate_permissions: required vs optional, attachments toggle, DM safety
# --------------------------------------------------------------------------- #


def _channel_with_perms(perms: dict[str, bool], guild_member_id: int = 999):
    """Build a guild channel with a configurable permission set."""
    guild = MagicMock()
    bot_member = MagicMock()
    guild.get_member = MagicMock(return_value=bot_member)

    channel = MagicMock()
    channel.guild = guild
    channel.name = "test-channel"

    # permissions_for() returns an object whose attribute lookup we control.
    perm_obj = SimpleNamespace(**perms)
    channel.permissions_for = MagicMock(return_value=perm_obj)
    return channel, guild_member_id


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
    def test_dm_channel_rejected(self, threadit_bot):
        dm = MagicMock(spec=[])  # no .guild attribute
        ok, missing_req, missing_opt = threadit_bot.validate_permissions(dm)
        assert ok is False
        assert missing_req == ["Not a guild channel"]
        assert missing_opt == []

    def test_all_perms_granted(self, threadit_bot):
        channel, _ = _channel_with_perms(_ALL_PERMS)
        with patch.object(type(threadit_bot), "user",
                          SimpleNamespace(id=999), create=True):
            ok, missing_req, missing_opt = threadit_bot.validate_permissions(channel)
        assert ok is True
        assert missing_req == []
        assert missing_opt == []

    def test_missing_embed_links_blocks(self, threadit_bot):
        perms = dict(_ALL_PERMS, embed_links=False)
        channel, _ = _channel_with_perms(perms)
        with patch.object(type(threadit_bot), "user",
                          SimpleNamespace(id=999), create=True):
            ok, missing_req, _ = threadit_bot.validate_permissions(channel)
        assert ok is False
        assert "Embed Links" in missing_req

    def test_attach_files_required_only_when_has_attachments(self, threadit_bot):
        perms = dict(_ALL_PERMS, attach_files=False)
        channel, _ = _channel_with_perms(perms)
        with patch.object(type(threadit_bot), "user",
                          SimpleNamespace(id=999), create=True):
            ok_no_att, missing_no_att, _ = threadit_bot.validate_permissions(
                channel, has_attachments=False
            )
            ok_with_att, missing_with_att, _ = threadit_bot.validate_permissions(
                channel, has_attachments=True
            )
        assert ok_no_att is True
        assert "Attach Files" not in missing_no_att
        assert ok_with_att is False
        assert "Attach Files" in missing_with_att

    def test_manage_messages_is_optional(self, threadit_bot):
        perms = dict(_ALL_PERMS, manage_messages=False)
        channel, _ = _channel_with_perms(perms)
        with patch.object(type(threadit_bot), "user",
                          SimpleNamespace(id=999), create=True):
            ok, missing_req, missing_opt = threadit_bot.validate_permissions(channel)
        assert ok is True
        assert missing_req == []
        assert missing_opt == ["Manage Messages"]


# --------------------------------------------------------------------------- #
# Permission warning rate-limit
# --------------------------------------------------------------------------- #


class TestPermissionWarningRateLimit:
    async def test_first_warning_sends_subsequent_suppressed(self, threadit_bot):
        channel = MagicMock()
        channel.id = 7777
        channel.name = "test"
        channel.send = AsyncMock()

        # Pin time.monotonic() so the test is deterministic regardless of how
        # long the host has been up. Specifically, return a value that is LESS
        # than the cooldown — this is the freshly-booted-host scenario where
        # the prior `0.0` sentinel would have suppressed the very first warning.
        monotonic_values = iter([10.0, 11.0, 12.0])
        with (
            patch.object(threadit_bot, "check_specific_permission", return_value=True),
            patch.object(threadit_bot, "_client_id", return_value="999"),
            patch("bot.time.monotonic", side_effect=lambda: next(monotonic_values)),
        ):
            await threadit_bot.send_permission_error_message(channel, ["Embed Links"])
            await threadit_bot.send_permission_error_message(channel, ["Embed Links"])
            await threadit_bot.send_permission_error_message(channel, ["Embed Links"])

        assert channel.send.await_count == 1, (
            "First warning must send even on freshly-booted hosts where "
            "monotonic() < cooldown; subsequent warnings must be suppressed"
        )

    async def test_different_channels_are_independent(self, threadit_bot):
        ch_a, ch_b = MagicMock(), MagicMock()
        ch_a.id, ch_b.id = 1, 2
        ch_a.name, ch_b.name = "a", "b"
        ch_a.send = AsyncMock()
        ch_b.send = AsyncMock()

        with (
            patch.object(threadit_bot, "check_specific_permission", return_value=True),
            patch.object(threadit_bot, "_client_id", return_value="999"),
        ):
            await threadit_bot.send_permission_error_message(ch_a, ["Embed Links"])
            await threadit_bot.send_permission_error_message(ch_b, ["Embed Links"])

        assert ch_a.send.await_count == 1
        assert ch_b.send.await_count == 1


# --------------------------------------------------------------------------- #
# Concurrent reply race — verifies the per-parent asyncio.Lock + cleanup
# --------------------------------------------------------------------------- #


class TestParentLockCleanup:
    """
    These tests drive the production helper ThreadItBot._with_parent_lock
    directly, so a regression in the lock/cleanup wiring would fail them.
    """

    async def test_lock_dict_empties_after_use(self, threadit_bot):
        import asyncio

        parent_id = 12345

        async def worker():
            async with threadit_bot._with_parent_lock(parent_id):
                await asyncio.sleep(0)

        await asyncio.gather(*[worker() for _ in range(5)])
        assert parent_id not in threadit_bot._parent_locks

    async def test_lock_dict_empties_after_single_use(self, threadit_bot):
        """No-contention case: a single acquire/release must still clean up."""
        async with threadit_bot._with_parent_lock(42):
            pass
        assert 42 not in threadit_bot._parent_locks

    async def test_three_concurrent_workers_serialize(self, threadit_bot):
        """A→B→C must execute strictly serialized, not interleaved."""
        import asyncio

        parent_id = 99
        events: list[str] = []

        async def worker(name: str, delay: float):
            await asyncio.sleep(delay)
            async with threadit_bot._with_parent_lock(parent_id):
                events.append(f"{name}-enter")
                await asyncio.sleep(0.01)
                events.append(f"{name}-exit")

        await asyncio.gather(worker("A", 0), worker("B", 0.001), worker("C", 0.002))

        # No interleaving: each worker's enter and exit appear consecutively.
        for i in range(0, 6, 2):
            assert events[i + 1] == events[i].replace("-enter", "-exit"), events

    async def test_lock_releases_on_exception(self, threadit_bot):
        """If the body raises, the entry must still be removed (no leak)."""
        with pytest.raises(RuntimeError, match="boom"):
            async with threadit_bot._with_parent_lock(77):
                raise RuntimeError("boom")
        assert 77 not in threadit_bot._parent_locks
