"""Tests for threadit.orchestrator.ThreadingOrchestrator (lock + helpers)."""

from __future__ import annotations

import asyncio
import logging
from unittest.mock import MagicMock

import pytest

from threadit.orchestrator import ThreadingOrchestrator
from threadit.permissions import PermissionsService


@pytest.fixture
def orchestrator() -> ThreadingOrchestrator:
    perms = PermissionsService(
        get_self_id=lambda: 999,
        get_client_id=lambda: "999",
        logger=logging.getLogger("test-perms"),
    )
    return ThreadingOrchestrator(
        permissions=perms,
        logger=logging.getLogger("test-orchestrator"),
    )


class TestWithParentLock:
    """
    These tests drive the production helper directly so a regression in
    the lock/cleanup wiring fails them.
    """

    async def test_dict_empties_after_single_use(self, orchestrator):
        async with orchestrator._with_parent_lock(42):
            pass
        assert 42 not in orchestrator._parent_locks

    async def test_dict_empties_after_concurrent_use(self, orchestrator):
        parent_id = 12345

        async def worker():
            async with orchestrator._with_parent_lock(parent_id):
                await asyncio.sleep(0)

        await asyncio.gather(*[worker() for _ in range(5)])
        assert parent_id not in orchestrator._parent_locks

    async def test_three_concurrent_workers_serialize(self, orchestrator):
        """A→B→C must execute strictly serialized, not interleaved."""
        parent_id = 99
        events: list[str] = []

        async def worker(name: str, delay: float):
            await asyncio.sleep(delay)
            async with orchestrator._with_parent_lock(parent_id):
                events.append(f"{name}-enter")
                await asyncio.sleep(0.01)
                events.append(f"{name}-exit")

        await asyncio.gather(worker("A", 0), worker("B", 0.001), worker("C", 0.002))

        # No interleaving: each worker's enter and exit appear consecutively.
        for i in range(0, 6, 2):
            assert events[i + 1] == events[i].replace("-enter", "-exit"), events

    async def test_releases_on_exception(self, orchestrator):
        with pytest.raises(RuntimeError, match="boom"):
            async with orchestrator._with_parent_lock(77):
                raise RuntimeError("boom")
        assert 77 not in orchestrator._parent_locks


class TestValidateProcessingConditions:
    def test_rejects_message_without_reference(self, orchestrator):
        message = MagicMock()
        message.reference = None
        message.guild = MagicMock()
        assert orchestrator._validate_processing_conditions(message) is False

    def test_rejects_dm(self, orchestrator):
        message = MagicMock()
        message.reference = MagicMock(message_id=1)
        message.guild = None
        assert orchestrator._validate_processing_conditions(message) is False

    def test_rejects_channel_without_create_thread(self, orchestrator):
        message = MagicMock()
        message.reference = MagicMock(message_id=1)
        message.guild = MagicMock()
        message.channel = MagicMock(spec=[])  # no create_thread attribute
        assert orchestrator._validate_processing_conditions(message) is False

    def test_accepts_valid_reply(self, orchestrator):
        message = MagicMock()
        message.reference = MagicMock(message_id=1)
        message.guild = MagicMock()
        # spec=["create_thread"] so hasattr(channel, 'create_thread') is True
        message.channel = MagicMock(spec=["create_thread", "name"])
        assert orchestrator._validate_processing_conditions(message) is True
