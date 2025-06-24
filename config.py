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
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        if not cls.DISCORD_TOKEN:
            return False
        return True

    @classmethod
    def get_thread_name(cls, original_message_content: str) -> str:
        """
        Generate a thread name from the original message content.

        Args:
            original_message_content: The content of the message being replied to

        Returns:
            A truncated and cleaned thread name
        """
        if not original_message_content or original_message_content.isspace():
            return "Discussion Thread"

        # Clean the content for use as a thread name
        # Remove newlines and extra whitespace
        cleaned = ' '.join(original_message_content.split())

        # Remove mentions, links, and other Discord formatting
        # This is a basic implementation - could be enhanced
        words = []
        for word in cleaned.split():
            if not (word.startswith('<@') or word.startswith('<#') or
                   word.startswith('http://') or word.startswith('https://')):
                words.append(word)

        thread_name = ' '.join(words)

        # Truncate to Discord's limit
        if len(thread_name) > cls.MAX_THREAD_NAME_LENGTH:
            thread_name = thread_name[:cls.MAX_THREAD_NAME_LENGTH - 3] + "..."

        return thread_name or "Discussion Thread"
