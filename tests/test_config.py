"""Tests for config.Config helpers (pure, no Discord I/O)."""

from __future__ import annotations

import importlib

import pytest

import config


class TestGetThreadName:
    def test_simple_text_passes_through(self):
        assert config.Config.get_thread_name("hello world") == "hello world"

    def test_empty_returns_fallback(self):
        assert config.Config.get_thread_name("") == "Discussion Thread"

    def test_whitespace_only_returns_fallback(self):
        assert config.Config.get_thread_name("   \t\n") == "Discussion Thread"

    def test_strips_user_mention(self):
        assert config.Config.get_thread_name("hey <@123> what's up") == "hey what's up"

    def test_strips_channel_mention(self):
        assert config.Config.get_thread_name("check <#456> please") == "check please"

    def test_strips_link(self):
        assert config.Config.get_thread_name("see https://example.com cool") == "see cool"

    def test_strips_spoiler_and_inline_code(self):
        assert config.Config.get_thread_name("||hidden|| and `code` ok") == "and ok"

    def test_strips_at_everyone(self):
        # @everyone must be removed so thread names cannot be misleading.
        assert config.Config.get_thread_name("hey @everyone what up") == "hey what up"

    def test_strips_at_here_case_insensitive(self):
        assert config.Config.get_thread_name("hi @Here let us thread") == "hi let us thread"

    def test_strips_zero_width_chars(self):
        # zero-width space, zero-width joiner: U+200B, U+200D
        assert config.Config.get_thread_name("zero​width‍join") == "zerowidthjoin"

    def test_strips_bidi_override(self):
        # right-to-left override U+202E used for spoofing
        assert config.Config.get_thread_name("‮revert me") == "revert me"

    def test_truncates_to_discord_limit(self):
        long = "A" * 150
        result = config.Config.get_thread_name(long)
        assert len(result) == config.Config.MAX_THREAD_NAME_LENGTH
        assert result.endswith("...")

    def test_only_stripped_tokens_returns_fallback(self):
        assert (
            config.Config.get_thread_name("<@123> https://x.com `code`")
            == "Discussion Thread"
        )


class TestIntEnv:
    def test_returns_default_when_unset(self, monkeypatch):
        monkeypatch.delenv("FOO_THREADIT_TEST", raising=False)
        assert config._int_env("FOO_THREADIT_TEST", 42) == 42

    def test_returns_default_when_empty(self, monkeypatch):
        monkeypatch.setenv("FOO_THREADIT_TEST", "")
        assert config._int_env("FOO_THREADIT_TEST", 42) == 42

    def test_parses_valid_int(self, monkeypatch):
        monkeypatch.setenv("FOO_THREADIT_TEST", "1024")
        assert config._int_env("FOO_THREADIT_TEST", 42) == 1024

    def test_raises_clear_error_on_garbage(self, monkeypatch):
        monkeypatch.setenv("FOO_THREADIT_TEST", "abc")
        with pytest.raises(ValueError, match=r"FOO_THREADIT_TEST.*integer.*'abc'"):
            config._int_env("FOO_THREADIT_TEST", 42)


class TestConfigValidate:
    def test_passes_when_token_present(self, monkeypatch):
        monkeypatch.setattr(config.Config, "DISCORD_TOKEN", "real-token-shape")
        config.Config.validate()

    def test_raises_when_token_missing(self, monkeypatch):
        monkeypatch.setattr(config.Config, "DISCORD_TOKEN", None)
        with pytest.raises(ValueError, match="DISCORD_TOKEN"):
            config.Config.validate()


class TestDotenvOrdering:
    """The original bug: load_dotenv ran AFTER `from config import Config`.

    A regression here means self-hosters following the README would
    silently get DISCORD_TOKEN=None.
    """

    def test_config_picks_up_env_at_import_time(self, monkeypatch):
        monkeypatch.setenv("DISCORD_TOKEN", "loaded-from-env")
        # Force fresh evaluation of module-level os.getenv.
        reloaded = importlib.reload(config)
        assert reloaded.Config.DISCORD_TOKEN == "loaded-from-env"
