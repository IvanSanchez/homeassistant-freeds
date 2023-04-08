
import aiohttp
import asyncio
import json
import time
import sys
import logging

_LOGGER = logging.getLogger(__name__)
timeout = aiohttp.ClientTimeout(total=30, sock_read=30)


class FreeDSHTTPClient:

    session = None
    resp = None
    handlers = {}
    host = ''
    stop = False
    retries = 1

    def __init__(self, host):
        self.host = host
        asyncio.create_task(self.loop())

    async def loop(self):
        if (self.session is None):
            self.session = aiohttp.ClientSession(timeout=timeout)

        try:
            self.resp = await self.session.get(f'http://{self.host}/events')
            # print(f'http://{self.host}/events', self.resp.status)
            _LOGGER.info(f'Status response from http://{self.host}/events is {self.resp.status}')
        except:
            _LOGGER.exception(sys.exception())

        if self.resp:
            for _ in iter(int, 1):
                if (self.stop):
                    break;

                try:
                    msg = await (self.resp.content.read(2048))
                except Exception:
                    ### TODO: Send the timeout to HASS, somehow
                    _LOGGER.error(f"{self.host} HTTP timeout")
                    break;
                else:
                    self.retries = 1
                    if msg.startswith(b'event: jsonweb\r\ndata:'):
                        try:
                            event = json.loads(msg[22:])
                            # print (event['loadCalcWatts'], event['pwm'])
                        except:
                            _LOGGER.error("Incomplete JSON message, ignoring.")
                        else:
                            for field, handler in self.handlers.items():
                                handler(event[field])
                    else:
                        # Ignore any messages that are not events (uptime, etc)
                        pass

        if (self.resp is not None):
            self.resp.close()

        # Call all handlers with None, to signify device is unavailable
        for field, handler in self.handlers.items():
            handler(None)

        if (self.stop):
            return
        else:
            await asyncio.sleep(10 * self.retries)
            self.retries += 1
            _LOGGER.info(f"{self.host} reconnecting...")
            await self.loop()


    def register(self, field, fn):
        """Registers a handler function for a JSON field"""
        self.handlers[field] = fn


