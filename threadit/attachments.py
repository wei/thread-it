"""Attachment download with per-file size cap."""

from __future__ import annotations

import io
import logging

import discord


async def build_attachment_files(
    attachments: list[discord.Attachment],
    *,
    max_bytes: int,
    logger: logging.Logger,
) -> tuple[list[discord.File], bool]:
    """
    Download attachments and convert them into ``discord.File`` objects,
    enforcing the per-attachment size cap so a malicious or unlucky upload
    can't OOM a small host.

    Returns ``(files, all_succeeded)``. ``all_succeeded`` is ``False`` if any
    attachment was skipped (oversize) or failed to download — the caller
    uses this to avoid deleting the original message.
    """
    files: list[discord.File] = []
    all_succeeded = True

    for attachment in attachments:
        if attachment.size and attachment.size > max_bytes:
            logger.warning(
                f"Skipping oversize attachment {attachment.filename} "
                f"({attachment.size} bytes > {max_bytes} byte limit)"
            )
            all_succeeded = False
            continue

        try:
            file_data = await attachment.read()
            files.append(discord.File(
                fp=io.BytesIO(file_data),
                filename=attachment.filename,
                description=attachment.description,
            ))
        except Exception as e:
            logger.warning(f"Failed to process attachment {attachment.filename}: {e}")
            all_succeeded = False

    return files, all_succeeded
