"""Pytest configuration: provide a DISCORD_TOKEN before bot is imported."""

import os

# bot.py / config.py read DISCORD_TOKEN at import time via load_dotenv.
# Tests don't talk to Discord, but Config.validate() refuses to load
# without one, so seed a placeholder before any test module imports bot.
os.environ.setdefault("DISCORD_TOKEN", "test-token")
