#!/usr/bin/env python3

"""
Proxy server to forward mail data from the dovecot container (which lacks curl and a lot of other
tools, so that really only netcat is available) to the rspamd container's HTTP endpoints for ham
and spam learning
"""

import asyncio
import logging
import os

import aiohttp

RSPAMD_HOST:     str        = os.environ.get("RSPAMD_HOST", "rspamd")
RSPAMD_PORT:     int        = int(os.environ.get("RSPAMD_PORT", "11334"))
RSPAMD_PASSWORD: str | None = os.environ.get("RSPAMD_PASSWORD")
HAM_PORT:        int        = int(os.environ.get("HAM_PORT", "9000"))
SPAM_PORT:       int        = int(os.environ.get("SPAM_PORT", "9001"))
LOG_LEVEL:       str        = os.environ.get("LOG_LEVEL", "INFO")

logger = logging.getLogger(__name__)


async def handle_request(
    session: aiohttp.ClientSession,
    endpoint: str,
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
) -> None:
    """
    Handle client request: read data and forward to rspamd
    """

    try:
        url = f"http://{RSPAMD_HOST}:{RSPAMD_PORT}/{endpoint}"
        data = await reader.read(-1)
        headers = {"Content-Type": "message/rfc822"}
        if RSPAMD_PASSWORD:
            headers["Password"] = RSPAMD_PASSWORD
        async with session.post(url, data=data, headers=headers) as resp:
            await resp.read()
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Error forwarding /%s: %s", endpoint, e)
    writer.close()


async def run_forwarder(
        session: aiohttp.ClientSession,
        endpoint: str,
        port: int
):
    """
    Spawn a forwarding server to the given endpoint, listening to the given port.

    :param session HTTP Client session used to connect to the endpoint
    :param endpoint Name of the endpoint on the rspamd controller (learnspam or learnham)
    :param port TCP port to listen on
    """

    server = await asyncio.start_server(
        lambda r, w: handle_request(session, endpoint, r, w),
        port=port
    )

    async with server:
        await server.serve_forever()


async def async_main() -> None:
    """
    Main coroutine: Starts server, handles connections indefinitely.
    """

    async with aiohttp.ClientSession() as session:
        logger.info("Forwarding spam:%d and ham:%d -> %s:%d", SPAM_PORT, HAM_PORT, RSPAMD_HOST, RSPAMD_PORT)
        await asyncio.gather(
            run_forwarder(session, "learnspam", SPAM_PORT),
            run_forwarder(session, "learnham", HAM_PORT)
        )

def main():
    """
    Synchronous main function: Spawns main coroutine in asyncio.run
    """
    logging.basicConfig(level=LOG_LEVEL)
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
