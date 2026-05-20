"""Tests for threadit.attachments.build_attachment_files."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

from threadit.attachments import build_attachment_files


@pytest.fixture
def logger() -> logging.Logger:
    return logging.getLogger("test-attachments")


def _attachment(filename: str, size: int, read_data: bytes | None = None,
                read_exc: Exception | None = None):
    att = MagicMock(spec=discord.Attachment)
    att.filename = filename
    att.size = size
    att.description = None
    if read_exc is not None:
        att.read = AsyncMock(side_effect=read_exc)
    else:
        att.read = AsyncMock(return_value=read_data or b"x" * min(size, 16))
    return att


MAX = 25 * 1024 * 1024


class TestBuildAttachmentFiles:
    async def test_empty_returns_ok(self, logger):
        files, ok = await build_attachment_files([], max_bytes=MAX, logger=logger)
        assert files == []
        assert ok is True

    async def test_small_attachment_downloaded(self, logger):
        att = _attachment("hi.txt", 10, b"hello")
        files, ok = await build_attachment_files([att], max_bytes=MAX, logger=logger)
        assert ok is True
        assert len(files) == 1
        assert files[0].filename == "hi.txt"

    async def test_oversize_skipped_and_flagged(self, logger):
        att = _attachment("big.bin", 30 * 1024 * 1024)
        files, ok = await build_attachment_files([att], max_bytes=MAX, logger=logger)
        assert ok is False, "oversize attachment must mark the batch as failed"
        assert files == []
        att.read.assert_not_called()

    async def test_download_failure_flagged(self, logger):
        att = _attachment("flaky.txt", 10, read_exc=RuntimeError("boom"))
        files, ok = await build_attachment_files([att], max_bytes=MAX, logger=logger)
        assert ok is False
        assert files == []

    async def test_partial_success_still_flags_failure(self, logger):
        good = _attachment("ok.txt", 10, b"ok")
        bad = _attachment("huge.bin", 99 * 1024 * 1024)
        files, ok = await build_attachment_files([good, bad], max_bytes=MAX, logger=logger)
        # Good attachment kept; ok=False signals "don't delete original".
        assert ok is False
        assert len(files) == 1
        assert files[0].filename == "ok.txt"
