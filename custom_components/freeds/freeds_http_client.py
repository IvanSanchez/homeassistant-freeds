
import aiohttp
import asyncio
import json
import time
import sys

timeout = aiohttp.ClientTimeout(total=30, sock_read=10)


class FreeDSHTTPClient:

    session = None
    resp = None
    handlers = {}
    host = ''
    stop = False

    def __init__(self, host):
        self.host = host
        asyncio.create_task(self.loop())

    async def loop(self):
        if (self.session == None):
            self.session = aiohttp.ClientSession(timeout=timeout)

        try:
            self.resp = await self.session.get(f'http://{self.host}/events')
            # print(f'http://{self.host}/events', self.resp.status)
        except:
            ### TODO: Send the exception to HASS, somehow
            print(repr(sys.exception()))

        for _ in iter(int, 1):
            if (self.stop):
                break;

            try:
                msg = await (self.resp.content.read(2048))
            except Exception:
                ### TODO: Send the timeout to HASS, somehow
                print("Timeout")
                break;
            else:
                if msg.startswith(b'event: jsonweb\r\ndata:'):
                    # print (msg[22:])
                    event = json.loads(msg[22:])
                    # print (event)
                    # print (event['loadCalcWatts'], event['pwm'])
                    # print (event['wsolar'], event['wgrid'])
                    for field, handler in self.handlers.items():
                        handler(event[field])
                else:
                    # print(msg)
                    pass

        self.resp.close()

        # Call all handlers with None, to signify device is unavailable
        for field, handler in self.handlers.items():
            handler(None)

        if (self.stop):
            return
        else:
            await asyncio.sleep(10)
            print("Reconnecting...")
            await self.loop()


    def register(self, field, fn):
        self.handlers[field] = fn



# client = FreeDSHTTPClient('192.168.4.20')
#
# client.register('pwm', print)
#
#
# time.sleep(5)
# print ("STOP")
# client.stop = True

