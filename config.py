"""
Configuration module for Thread It bot.
Handles all configuration settings and constants.
"""

import os
from typing import Optional

class Config:
    """Configuration class containing all bot settings."""

    # Discord API Configuration
    DISCORD_TOKEN: Optional[str] = os.getenv('DISCORD_TOKEN')

    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO').upper()

    # Thread Configuration
    DEFAULT_AUTO_ARCHIVE_DURATION: int = 1440  # 24 hours in minutes
    MAX_THREAD_NAME_LENGTH: int = 100  # Discord's limit for thread names


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

        # Remove mentions, links, and other Discord formatting
        cleaned = ' '.join(
            word for word in original_message_content.split()
            if not (
                word.startswith(('<@', '<#', 'http://', 'https://')) or
                (word.startswith('||') and word.endswith('||')) or
                (word.startswith('`') and word.endswith('`'))
            )
        )

        # Truncate to Discord's limit
        if len(cleaned) > cls.MAX_THREAD_NAME_LENGTH:
            cleaned = cleaned[:cls.MAX_THREAD_NAME_LENGTH - 3] + "..."

        return cleaned or "Discussion Thread"
