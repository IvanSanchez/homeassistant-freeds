"""FreeDS coordinator: handles the HTTP request(s) for all entities"""

import logging

import asyncio
import aiohttp
import websockets
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
    """FreeDS coordinator, SSE flavour."""

    # This coordinator works as a weird HTTP client.
    # The way FreeDS provides updates via the /events endpoint.
    # It follows the EventSource spec,
    # see http://developer.mozilla.org/en-US/docs/Web/API/EventSource.html
    #
    # That's *kinda* like multipart HTTP content (RFC 1341, section 7.2).
    # Like multipart content, each chunk can be read with a single socket
    # read operation (or a resp.content.read() in python's aiohttp). Unlike
    # proper multipart content, there is no explicit data boundary.

    session = None
    resp = None
    host = ""
    retries = 1
    running = False

    def __init__(
        self, hass, host, port=80, user=None, passwd=None, name="FreeDS client"
    ):
        """Initialize coordinator."""
        super().__init__(hass, _LOGGER, name=name)
        self.host = host
        self.port = port
        self.name = name
        self.data = {}
        self.session = aiohttp.ClientSession(timeout=timeout)
        self.last_http_error = None
        self._mode = None

        if user is None:
            self.auth = None
        else:
            self.auth = aiohttp.BasicAuth(user, passwd)

    @callback
    def async_add_listener(self, update_callback, context):
        remove_handler = super().async_add_listener(update_callback, context)

        if not self.running:
            self.running = True
            asyncio.create_task(self.loop())

        return remove_handler

    async def loop(self):
        for _ in iter(int, 1):
            _LOGGER.info(f"Determining sse/websockets/getjson mode for {self.name}")
            mode = await self.query_mode()
            self.mode = mode
            
            if mode == "getjson":
                return await self.loop_getjson()
            elif mode == "websocket":
                return await self.loop_websocket()
            elif mode == "sse":
                return await self.loop_sse()
            await asyncio.sleep(10 * self.retries)
            self.retries += 1
            _LOGGER.info(
                f"Could not determine sse/websockets/getjson mode for {self.name}, retrying."
            )
            self.async_set_update_error("Could not connect")

    async def query_mode(self):
        if self._mode is not None:
            return self._mode

        try:
            # Does the host respond at all?
            resp = await self.session.get(
                f"http://{self.host}:{self.port}/", auth=self.auth
            )
            _LOGGER.info(
                f"Status response from http://{self.host}:{self.port}/ is {resp.status}"
            )

            if resp.status != 200:
                return
        except Exception:
            return
        
        try:
            # Try to detect JSON-capable firmware
            url = f"http://{self.host}:{self.port}/api/common"
            resp = await self.session.get(url, auth=self.auth)
            _LOGGER.info(f"GET {url} -> status: {resp.status}")

            # Safely try to parse JSON
            try:
                data = await resp.json()
            except Exception as err:
                _LOGGER.debug(f"{self.name}: /api/common did not return JSON: {err}")
                data = None

            if isinstance(data, dict):
                _LOGGER.info(f"Detecting version: {data.get('version')}")
                ver = data.get("version")

                if isinstance(ver, str):
                    # --- For Versions => 2.0 ---
                    # Exemple: "2.0.0 Beta Build..." -> "2.0.0"
                    try:
                        prefix = ver[0:5]
                        # Verify it look slike a number (Ex: "2.0.0" o "10.0.")
                        if prefix[0].isdigit() and "." in prefix:
                            major_ver_str = prefix.split('.')[0] # Get the number before the .
                            if int(major_ver_str) >= 2:
                                self._fwversion = ver
                                self._mode = "getjson"
                                _LOGGER.info(f"{self.name}: Mode GET/JSON enabled (Major version {major_ver_str}+ detected)")
                                return self._mode
                    except Exception:
                        pass # If this failes , fall bakc to legacy logic

                    # --- OLD LOGIC (Legacy 1.00.0021) ---
                    # Try to take slice 4..8 and get digits only
                    version_short = None
                    try:
                        slice_txt = ver[4:8]
                        digits = "".join(ch for ch in slice_txt if ch.isdigit())
                        if digits:
                            version_short = int(digits)
                    except Exception:
                        version_short = None

                    if version_short is not None and version_short > 20:
                        self._fwversion = ver
                        self._mode = "getjson"
                        _LOGGER.info(f"{self.name}: Mode GET/JSON enabled (version {version_short})")
                        return self._mode
                    else:
                        _LOGGER.debug(f"{self.name}: JSON mode not applicable, version slice={version_short}")
            else:
                _LOGGER.debug(f"{self.name}: /api/common returned non-dict response")  

        except Exception as err:
            _LOGGER.debug(f"{self.name}: GET /api/common failed: {err}")
            pass

        try:
            # Look for firmware 1.1 endpoint; fw 1.1 implements websockets
            resp = await self.session.get(
                f"http://{self.host}:{self.port}/api/common", auth=self.auth
            )
            _LOGGER.info(
                f"Status response from http://{self.host}:{self.port}/api/common is {resp.status}"
            )
            json = await resp.json()
            _LOGGER.info(f"Fetched version {json['version']}. Starting WebSocket mode.")
            self._fwversion = json["version"]
            self._mode = "websocket"
            return self._mode
        except Exception as err:
            pass

        try:
            # Look for SSE endpoint
            resp = await self.session.get(
                f"http://{self.host}:{self.port}/events", auth=self.auth
            )
            _LOGGER.info(
                f"Status response from http://{self.host}:{self.port}/events is {resp.status}"
            )
            status = resp.status
            resp.close()
            if status == 200:
                _LOGGER.info(f"Starting SSE mode.")
                self._mode = "sse"
                return self._mode
        except Exception as err:
            pass


    async def loop_getjson(self):
        _LOGGER.info(f"Starting GET-JSON loop for {self.name}")
        
        url = f"http://{self.host}:{self.port}/json"
        
        # We force connections not to be reused to avoid 'Data after Connection: close' 
        # or dirty buffer reads from other requests.
        headers = {"Connection": "close"}

        for _ in iter(int, 1):
            if not self._listeners:
                break

            try:
                # We make the request
                async with self.session.get(url, auth=self.auth, headers=headers) as resp:
                    if resp.status == 200:
                        # We read the text first to avoid partial decoding errors.
                        text_data = await resp.text()
                        try:
                            data = json.loads(text_data)
                        except json.JSONDecodeError:
                            # Sometimes FreeDS sends "}}HTTP/1.1" appended to the end
                            # We try to clean it up by looking for the last '}  
                             if "}" in text_data:
                                 clean_text = text_data[:text_data.rfind("}")+1]
                                 data = json.loads(clean_text)
                             else:
                                 raise

                        self.retries = 1
                        self.async_set_updated_data(data)
                    else:
                        _LOGGER.warning(f"Error fetching {url}, status: {resp.status}")
                        self.last_http_error = f"HTTP {resp.status}"
                        # We force error to go to the except block
                        raise Exception(f"HTTP Status {resp.status}")

            except Exception as err:
                self.last_http_error = err
                
                # --- EMERGENCY RECOVERY BLOCK ---
                # The error log shows that the JSON data arrives INSIDE the exception.
                # If the protocol fails but we have the data, we try to save it.
                recovered = False
                err_str = str(err)
                if "Data after Connection: close" in err_str or "{" in err_str:
                    try:
                        # We look for something that looks like JSON in the error message
                        import re
                        match = re.search(r'(\{.*\})', err_str)
                        if match:
                            raw_json = match.group(1)
                            # The log shows bytes b'...', clean if necessary
                            if raw_json.startswith("b'") or raw_json.startswith('b"'):
                                raw_json = raw_json[2:-1] # Take out b'...'
                            
                            # Sometimes the retrieved JSON has garbage at the end, we clean up to the last '}'
                            if raw_json.count('{') > 0 and raw_json.rfind('}') > 0:
                                raw_json = raw_json[:raw_json.rfind('}')+1]
                                
                            data = json.loads(raw_json) # If this doesn't work, let's go to the final exception
                            
                            _LOGGER.info(f"{self.name}: Recovered JSON data from HTTP error successfully.")
                            self.retries = 1
                            self.async_set_updated_data(data)
                            recovered = True
                    except Exception as parse_err:
                        _LOGGER.debug(f"Failed to recover JSON from error: {parse_err}")

                if not recovered:
                    if self.retries > 1:
                        self.data = {}
                        self.async_set_update_error(Exception(self.last_http_error))

                    _LOGGER.debug(f"Error requesting {url}: {err}. Retrying in 60s.")
                    await asyncio.sleep(60)
                    self.retries += 1
                    continue

            # Polling interval of 5 seconds
            await asyncio.sleep(5)

        _LOGGER.info(f"END GET-JSON loop for {self.name}")
        self.running = False

    async def loop_websocket(self):
        """Main loop: receive websockets"""
        self.logger.info(f"Starting websocket loop for {self.name}")

        async for websocket in websockets.connect(
            f"ws://{self.host}:{self.port}/jsonWeb"
        ):
            try:
                async for message in websocket:
                    if not self._listeners:
                        break
                    self.websocket_ok = True
                    # The websocket messages from firmware 1.1-beta16 are split
                    # into several categories: web, relays, energy, temperature
                    self.async_set_updated_data(json.loads(message))

            except websockets.ConnectionClosed as err:
                if not self._listeners:
                    break

                self.websocket_ok = False
                asyncio.create_task(self.error_websocket(err))
                await asyncio.sleep(10)
                self.logger.info(
                    f"{self.name} ({self.host}:{self.port}) reconnecting websocket..."
                )

                continue

        self.logger.info(f"Websocket loop stopped for {self.name} (no entities)")
        self.running = False

    async def error_websocket(self, err):
        """Returns null data to mark entities as "not available" after some time"""
        await asyncio.sleep(20)
        if not self.websocket_ok:
            self.data = {}
            self.async_set_update_error(Exception(err))

    async def loop_sse(self):
        """Main loop: creates HTTP connection and fetches data via SSE"""
        self.logger.info(f"Starting SSE request loop for {self.name}")

        for _ in iter(int, 1):
            try:
                self.resp = await self.session.get(
                    f"http://{self.host}:{self.port}/events", auth=self.auth
                )
                # print(f'http://{self.host}/events', self.resp.status)
                self.logger.info(
                    f"Status response from http://{self.host}:{self.port}/events is {self.resp.status}"
                )
            except Exception as err:
                # print("error connecting", err)
                # self.async_set_update_error(Exception(err))
                self.last_http_error = err

            if self.resp:
                for _ in iter(int, 1):
                    if not self._listeners:
                        break

                    try:
                        assert not self.resp.content.at_eof()
                        msg = await self.resp.content.readany()
                    except Exception as err:
                        # print("error reading", err)
                        # self.async_set_update_error(Exception(err))
                        self.last_http_error = err

                        break
                    else:
                        self.retries = 1
                        if msg.startswith(b"event: jsonweb\r\ndata:"):
                            try:
                                event = json.loads(msg[22:])
                            except Exception:
                                # async_set_update_error(Exception("Incomplete JSON message, ignoring."))
                                self.logger.debug("Incomplete JSON message, ignoring.")
                                pass
                            else:
                                # Send the entire event to the listening
                                # entities - they'll fetch the appropriate field.

                                # Sections are the default in 1.1-beta firmware
                                # and are added here for backwards compatibility

                                sectionedEvent = {
                                    "Web": {
                                        "Oled": event.get("Oled"),
                                        "screenBrightness": event.get(
                                            "screenBrightness"
                                        ),
                                        "POn": event.get("POn"),
                                        "PwmMan": event.get("PwmMan"),
                                        "SenTemp": event.get("SenTemp"),
                                        "Msg": event.get("Msg"),
                                        "pwmfrec": event.get("pwmfrec"),
                                        "pwm": event.get("pwm"),
                                        "loadCalcWatts": event.get("loadCalcWatts"),
                                        "baudiosMeter": event.get("baudiosMeter"),
                                        # "workingMode": event.get('workingMode'),
                                        "workingMode": event.get(
                                            "wversion"
                                        ),  # Name change
                                        # "workingModeName": event.get('workingModeName'),
                                        # "masterMode": event.get('masterMode'),
                                        # "masterModeName": event.get('masterModeName'),
                                        "invertedSign": event.get("invertedSign"),
                                        "tempShutdown": event.get("tempShutdown"),
                                        "error": event.get("error"),
                                    },
                                    "Relays": {
                                        "R01": event.get("R01"),
                                        "R02": event.get("R02"),
                                        "R03": event.get("R03"),
                                        "R04": event.get("R04"),
                                    },
                                    "Inverter": {
                                        "wsolar": event.get("wsolar"),
                                        "wgrid": event.get("wgrid"),
                                        "invTemp": event.get("invTemp"),
                                        "wtoday": event.get("wtoday"),
                                        "gridv": event.get("gridv"),
                                        "pv1c": event.get("pv1c"),
                                        "pv1v": event.get("pv1v"),
                                        "pv1w": event.get("pv1w"),
                                        "pv2c": event.get("pv2c"),
                                        "pv2v": event.get("pv2v"),
                                        "pv2w": event.get("pv2w"),
                                    },
                                    "Meter": {
                                        "mvoltage": event.get("mvoltage"),
                                        "mcurrent": event.get("mcurrent"),
                                        "mpowerFactor": event.get("mpowerFactor"),
                                        "mfrequency": event.get("mfrequency"),
                                        "mimportActive": event.get("mimportActive"),
                                        "mexportActive": event.get("mexportActive"),
                                    },
                                    "Energy": {
                                        "KwToday": event.get("KwToday"),
                                        "KwYesterday": event.get("KwYesterday"),
                                        "KwTotal": event.get("KwTotal"),
                                        "KwExportToday": event.get("KwExportToday"),
                                        "KwExportYesterday": event.get(
                                            "KwExportYesterday"
                                        ),
                                        "KwExportTotal": event.get("KwExportTotal"),
                                    },
                                    "Temperature": {
                                        "tempTermo": event.get("tempTermo"),
                                        "tempTriac": event.get("tempTriac"),
                                        "tempCustom": event.get("tempCustom"),
                                        # "customSensor": "Temp. Ambiente"
                                    },
                                }

                                self.async_set_updated_data(sectionedEvent)
                        else:
                            # Ignore any messages that are not events (uptime, etc)
                            pass

            if self.resp is not None:
                self.resp.close()

            if not self._listeners:
                break

            if self.retries > 1:
                # Marks entities as "not available" at the *second* consecutive
                # error
                self.data = {}
                self.async_set_update_error(Exception(self.last_http_error))

            await asyncio.sleep(10 * self.retries)
            self.retries += 1
            self.logger.info(f"{self.name} ({self.host}:{self.port}) reconnecting...")

        self.logger.info(f"SSE request loop stopped for {self.name} (no entities)")
        self.running = False

    async def async_send_toggle_button(self, button_idx):
        """Sends a HTTP POST query to toggle a button"""
        self.logger.info(f"Sending HTTP POST to toggle button {button_idx}")

        # Note the typo in the URL: "toogle" instead of "toggle". The firmware
        # uses "toogle".

        post_response = await self.session.post(
            f"http://{self.host}:{self.port}/tooglebuttons?data={button_idx}",
            auth=self.auth,
        )

        self.logger.info(f"Response status to button toggle: {post_response.status}")
        await post_response.text()
             