"""Debug helpers for NeoPilot tools."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neopilot.api.client import NeoDashClient


def debug_block(client: NeoDashClient) -> str:
    """Build a debug info block from the client's last request/response.

    The API token is already masked in ``client.last_url``.
    The raw response is truncated at 2000 chars to avoid flooding the LLM context.
    """
    parts = ["\n---\n**[DEBUG]**"]
    if client.last_url:
        parts.append(f"**Request URL:** `{client.last_url}`")
    if client.last_raw_response:
        raw = client.last_raw_response
        if len(raw) > 2000:
            raw = raw[:2000] + "\n... (truncated)"
        parts.append(f"**Raw Response:**\n```json\n{raw}\n```")
    return "\n".join(parts)
