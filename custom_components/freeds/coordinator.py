"""FreeDS coordinator: handles the HTTP request(s) for all entities"""

import logging

import asyncio
import aiohttp
import json
import sys

from homeassistant.core import callback
# from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

timeout = aiohttp.ClientTimeout(total=None, sock_read=3)

class FreeDSCoordinator(DataUpdateCoordinator):
    """FreeDS coordinator."""

    # This coordinator works as a weird HTTP client.
    # The way FreeDS provides updates via the /events endpoint
    # is *kinda* like multipart HTTP content (RFC 1341, section 7.2).
    # Like multipart content, each chunk can be read with a single socket
    # read operation (or a resp.content.read() in python's aiohttp). Unlike
    # proper multipart content, there is no explicit data boundary, so
    # reliability of the protocol can be somewhat flaky.
    #
    # (see https://www.w3.org/Protocols/rfc1341/7_2_Multipart.html).

    session = None
    resp = None
    host = ''
    retries = 1
    running = False

    def __init__(self, hass, host, name = "FreeDS"):
        """Initialize coordinator."""
        super().__init__( hass, _LOGGER, name = name)
        self.host = host
        self.name = name
        self.data = {}

    @callback
    def async_add_listener( self, update_callback, context):
        remove_handler = super().async_add_listener(update_callback, context)

        if (not self.running):
            self.logger.info(f'Starting HTTP request loop for {self.name}')
            self.running = True
            asyncio.create_task(self.loop())

        return remove_handler

    async def loop(self):
        """Main loop: creates HTTP connection and fetches data"""

        for _ in iter(int, 1):
            if (self.session is None):
                self.session = aiohttp.ClientSession(timeout=timeout)

            try:
                self.resp = await self.session.get(f'http://{self.host}:3333/events')
                # print(f'http://{self.host}/events', self.resp.status)
                self.logger.info(f'Status response from http://{self.host}:3333/events is {self.resp.status}')
            except Exception as err:
                self.async_set_update_error(sys.exception())
                # _LOGGER.exception(sys.exception())

            if (self.resp):
                for _ in iter(int, 1):
                    if (not self._listeners):
                        break;

                    try:
                        msg = await (self.resp.content.read(2048))
                        # print (msg)
                    except Exception as err:
                        # _LOGGER.error(f"{self.host} HTTP timeout")
                        # _LOGGER.error(err)
                        self.async_set_update_error(sys.exception())
                        break;
                    else:
                        self.retries = 1
                        if msg.startswith(b'event: jsonweb\r\ndata:'):
                            try:
                                event = json.loads(msg[22:])
                            except Exception:
                                # async_set_update_error(Exception("Incomplete JSON message, ignoring."))
                                self.logger.debug("Incomplete JSON message, ignoring.")
                                pass
                            else:
                                # Send the entire event to the listening
                                # entities - they'll fetch the appropriate field.
                                self.async_set_updated_data(event)
                        else:
                            # Ignore any messages that are not events (uptime, etc)
                            pass

            if (self.resp is not None):
                self.resp.close()

            if (not self._listeners):
                break;

            await asyncio.sleep(10 * self.retries)
            self.retries += 1
            self.logger.info(f"{self.name} ({self.host}) reconnecting...")

        self.logger.info(f'HTTP request loop stopped for {self.name} (no entities)')
        self.running = False
