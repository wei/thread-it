"""
Configuration module for Thread It bot.
Handles all configuration settings and constants.
"""

import os
import re
import unicodedata
from typing import Optional

from dotenv import load_dotenv

# Load .env before any Config attributes are evaluated.
load_dotenv()


# Strip Unicode control (Cc) and format (Cf) characters except common
# whitespace. This catches zero-width chars, bidi overrides, and other
# invisible glyphs that would otherwise survive into thread names.
_CONTROL_CHARS = ''.join(
    chr(c) for c in range(0x110000)
    if unicodedata.category(chr(c)) in ('Cc', 'Cf') and chr(c) not in '\t\n\r '
)
_CONTROL_CHARS_RE = re.compile(f'[{re.escape(_CONTROL_CHARS)}]')
_EVERYONE_RE = re.compile(r'@(everyone|here)\b', re.IGNORECASE)
_WHITESPACE_RE = re.compile(r'\s+')


def _int_env(name: str, default: int) -> int:
    """Read an integer env var; raise a clear error instead of Python's default."""
    raw = os.getenv(name)
    if raw is None or raw == '':
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(
            f"Environment variable {name} must be an integer, got {raw!r}"
        ) from exc


class Config:
    """Configuration class containing all bot settings."""

    # Discord API Configuration
    DISCORD_TOKEN: Optional[str] = os.getenv('DISCORD_TOKEN')

    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO').upper()

    # Thread Configuration
    DEFAULT_AUTO_ARCHIVE_DURATION: int = 1440  # 24 hours in minutes
    MAX_THREAD_NAME_LENGTH: int = 100  # Discord's limit for thread names

    # Attachment Configuration
    # Per-attachment cap to avoid OOM on small hosts. Discord's per-file
    # limit for non-boosted servers is 25 MiB; we mirror that as the default.
    MAX_ATTACHMENT_BYTES: int = _int_env('MAX_ATTACHMENT_BYTES', 25 * 1024 * 1024)

    # Rate-limit for in-channel "missing permission" warnings, per channel.
    PERMISSION_WARNING_COOLDOWN_SECONDS: int = _int_env(
        'PERMISSION_WARNING_COOLDOWN_SECONDS', 3600
    )

    @classmethod
    def validate(cls) -> None:
        """
        Validate that all required configuration is present.
        Raises:
            ValueError: If a required configuration is missing.
        """
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN environment variable not set.")

    @classmethod
    def get_thread_name(cls, original_message_content: str) -> str:
        """
        Generate a thread name from the original message content.

        Args:
            original_message_content: The content of the message being replied to.

        Returns:
            A truncated and cleaned thread name.
        """
        if not original_message_content or original_message_content.isspace():
            return "Discussion Thread"

        # Normalize and strip invisible control/format characters first so
        # tokenization below cannot be fooled by zero-width joins.
        normalized = unicodedata.normalize('NFKC', original_message_content)
        normalized = _CONTROL_CHARS_RE.sub('', normalized)
        normalized = _EVERYONE_RE.sub('', normalized)

        # Remove mentions, links, and other Discord formatting tokens.
        cleaned = ' '.join(
            word for word in normalized.split()
            if not (
                word.startswith(('<@', '<#', 'http://', 'https://')) or
                (word.startswith('||') and word.endswith('||')) or
                (word.startswith('`') and word.endswith('`'))
            )
        )

        cleaned = _WHITESPACE_RE.sub(' ', cleaned).strip()

        # Truncate to Discord's limit
        if len(cleaned) > cls.MAX_THREAD_NAME_LENGTH:
            cleaned = cleaned[:cls.MAX_THREAD_NAME_LENGTH - 3] + "..."

        return cleaned or "Discussion Thread"
