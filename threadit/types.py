"""Shared types and small helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import discord


# Client ID used in static error text before login. At runtime we prefer
# self.user.id so self-hosters get a link pointing at their own bot, not
# the upstream deployment.
DEFAULT_CLIENT_ID = "1386888801229734018"

# Both scopes are required: `bot` to join the guild, `applications.commands`
# so the bot can register slash commands. Without `scope=` Discord rejects
# the OAuth flow entirely.
_INVITE_SCOPES = "bot+applications.commands"


def invite_url(client_id: str | int) -> str:
    return (
        "https://discord.com/oauth2/authorize"
        f"?client_id={client_id}&scope={_INVITE_SCOPES}"
    )


@dataclass(frozen=True)
class ReplyInfo:
    """All the information about an incoming reply needed to convert it."""

    content: str
    author: discord.Member | discord.User
    attachments: list[discord.Attachment]
    embeds: list[discord.Embed]
    channel: discord.TextChannel | discord.VoiceChannel | discord.StageChannel
    parent_message: discord.Message
    message_id: int
    created_at: datetime
