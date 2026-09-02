"""
Infrastructure · Keep-Alive & Health-Check Server
==================================================

This module provides two async components designed to prevent
Render's free-tier containers from sleeping after 15 min of inactivity:

1. **Health-check web server** (aiohttp)
   - Binds to the PORT environment variable (Render requirement).
   - Exposes ``GET /health`` → ``{"status": "alive"}``.

2. **Self-ping background task**
   - Periodically hits the bot's own external URL to generate
     inbound HTTP traffic and reset Render's idle timer.

Both are launched as fire-and-forget ``asyncio`` tasks from ``main.py``.

Design decisions
----------------
* Single Responsibility — this file owns *only* the keep-alive
  infrastructure; bot handlers live in ``handlers/``.
* All magic numbers are imported from ``config.py``.
* The self-ping loop is wrapped in ``try / except`` so transient
  network errors never crash the bot process.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Final

import aiohttp
from aiohttp import web

from config import RENDER_EXTERNAL_URL, KEEPALIVE_INTERVAL_SEC

logger: Final = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
#  Health-check endpoint
# ---------------------------------------------------------------------------

async def _health_handler(request: web.Request) -> web.Response:
    """Return a lightweight JSON heartbeat.

    This endpoint is intentionally minimal — no DB queries,
    no secrets, no heavy computation.

    Args:
        request: Incoming ``aiohttp`` request (unused).

    Returns:
        ``200 OK`` with ``{"status": "alive"}``.
    """
    return web.json_response({"status": "alive"})


# ---------------------------------------------------------------------------
#  Web-server lifecycle
# ---------------------------------------------------------------------------

async def start_health_server() -> web.AppRunner:
    """Start an ``aiohttp`` web server that binds to ``$PORT`` and serves Mini App."""
    from web_app import setup_web_app

    app = web.Application()
    app.router.add_get("/health", _health_handler)
    setup_web_app(app)

    runner = web.AppRunner(app, access_log=None)
    await runner.setup()

    port: int = int(os.getenv("PORT", "8080"))
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()

    logger.info("Health-check & Mini App server listening on 0.0.0.0:%s", port)
    return runner



# ---------------------------------------------------------------------------
#  Self-ping keep-alive loop
# ---------------------------------------------------------------------------

async def keepalive_loop() -> None:
    """Periodically ping the bot's own ``/health`` endpoint.

    The interval is controlled by ``KEEPALIVE_INTERVAL_SEC``
    (default ≈ 10 min), which must be shorter than Render's 15-min
    idle timeout.

    The task is fully fault-tolerant:
    * Network blips are logged as warnings — never raised.
    * If ``RENDER_EXTERNAL_URL`` is not set the loop exits
      gracefully so local development is unaffected.
    """
    if not RENDER_EXTERNAL_URL:
        logger.warning(
            "RENDER_EXTERNAL_URL is not set — self-ping disabled. "
            "The bot will sleep on Render's free tier."
        )
        return

    ping_url: str = f"{RENDER_EXTERNAL_URL.rstrip('/')}/health"
    logger.info(
        "Keep-alive loop started  ·  interval=%ss  ·  target=%s",
        KEEPALIVE_INTERVAL_SEC,
        ping_url,
    )

    while True:
        await asyncio.sleep(KEEPALIVE_INTERVAL_SEC)
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15),
            ) as session:
                async with session.get(ping_url) as resp:
                    logger.info(
                        "Self-ping OK  ·  %s  ·  HTTP %s",
                        ping_url,
                        resp.status,
                    )
        except Exception as exc:  # noqa: BLE001 — intentionally broad
            logger.warning(
                "Self-ping failed (will retry in %ss): %s",
                KEEPALIVE_INTERVAL_SEC,
                exc,
            )
