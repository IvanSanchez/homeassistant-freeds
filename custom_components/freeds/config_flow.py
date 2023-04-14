from homeassistant import config_entries
from .const import DOMAIN
from homeassistant.const import (CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD)
import voluptuous as vol
import logging
from typing import Any, Final
from homeassistant.data_entry_flow import FlowResult
from getmac import get_mac_address
import aiohttp
import re


_LOGGER = logging.getLogger(__name__)


HOST_SCHEMA: Final = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_PORT, default=80): int
})
FULL_SCHEMA: Final = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_PORT, default=80): int,
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
})


class FreeDSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1

    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    # Schema only has a host (hostname/FQDN/ip address)
    host: str=""
    uniqueid: str=""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        # print ("async_step_user", user_input)

        errors: dict[str, str] = {}
        if user_input is not None:
            # host: str = user_input[CONF_HOST]
            host: str = user_input[CONF_HOST]
            port: str = user_input[CONF_PORT]
            user = user_input.get(CONF_USERNAME)
            passwd = user_input.get(CONF_PASSWORD)

            try:
                info = await self._async_get_info(host, port, user, passwd)

                if (info.get('error') == 'invalid_auth'):
                    return self.async_show_form(
                        step_id="user", data_schema=vol.Schema({
                            vol.Required(CONF_HOST, default=host): str,
                            vol.Required(CONF_PORT, default=port): int,
                            vol.Required(CONF_USERNAME, default=user): str,
                            vol.Required(CONF_PASSWORD, default=passwd): str,
                        }), errors={"base": "invalid_auth"}
                    )

                if (info['uniqueid'] is None):
                    errors["base"] = info['error']
                else:
                    await self.async_set_unique_id(info['uniqueid'])
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(title=f"FreeDS {info['uniqueid']}", data={
                        "host": user_input[CONF_HOST],
                        "port": user_input[CONF_PORT],
                        "username": user_input.get(CONF_USERNAME),
                        "password": user_input.get(CONF_PASSWORD),
                        "uniqueid": info['uniqueid'],
                        "fwversion": info['fwversion']
                    })

            # except CannotConnect:
            #     errors["base"] = "cannot_connect"
            # except InvalidHost:
            #     errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=HOST_SCHEMA, errors=errors
        )


    async def _async_get_info(self, host, port = 80, user = None, passwd = None):

        session = aiohttp.ClientSession()

        auth = None
        if (user is not None):
            auth = aiohttp.BasicAuth(user, passwd)

        # For FreeDS version 1.0.x, try fetching /index.html and scrapping
        # some text strings.

        ### TODO: Implement a more robust method of fetching information for
        ### any newer firmware versions

        _LOGGER.info(f"Checking for the FreeDS version by reading http://{host}:{port}/api/common (method for FreeDS >= 1.1.0-beta16)")

        try:
            resp = await session.get(f'http://{host}:{port}/', auth=auth)
            _LOGGER.info(f'Status response from http://{host}:{port}/ is {resp.status}')

            if (resp.status == 401):
                return { 'error': 'invalid_auth' }

            resp = await session.get(f'http://{host}:{port}/api/common', auth=auth)
            _LOGGER.info(f'Status response from http://{host}:{port}/api/common is {resp.status}')

            json = await resp.json()

            ### TODO: Fetch the MAC, not just the hostname.
            ### This depends on a firmware update, see https://github.com/pablozg/freeds/issues/82
            hostname = re.search('FreeDS \((.*)\)', json['title']).groups()[0]
            uniqueid = hostname[-4:]

            _LOGGER.info(f"Fetched hostname: {hostname} with unique ID {uniqueid}, firmware version {json['version']}.")

            await session.close()
            return {
                "uniqueid": uniqueid,
                "fwversion": json['version'],
                "mode": "websocket"
            }

        except Exception as err:
            _LOGGER.warning(f"API query failed ({err}). The device at {host} doesn't seem to be a FreeDS ~= 1.1-beta")
            pass


        _LOGGER.info(f"Checking for the FreeDS version by scraping http://{host}:{port}/ (method for FreeDS 1.0.x)")

        try:
            resp = await session.get(f'http://{host}:{port}/', auth=auth)
            _LOGGER.info(f'Status response from http://{host}:{port}/ is {resp.status}')

            if (resp.status == 401):
                return { 'error': 'invalid_auth' }

            html = await resp.text()

            _LOGGER.info(f"Successfully loaded http://{host}:{port}/ .")

            # Sanity check
            title = re.search('<meta name="description" content="FreeDS - Derivador de energía solar excedente">', html).span()

            _LOGGER.info(f'Found "FreeDS - Derivador de energía solar excedente" in http://{host}:{port}/ .')

            # Scrape firmware version from page footer
            fwversion = re.search('<div>Copyright © 2020. Derivador de energía solar excedente (.*)</div>', html).groups()[0]

            _LOGGER.info(f"Scrapped firmware version: {fwversion}")

            _LOGGER.info(f"Checking for the FreeDS hostname & unique ID by scraping  http://{host}:{port}/Red.html (method for FreeDS 1.0.x)")
            html = await (await session.get(f'http://{host}:{port}/Red.html', auth=auth)).text()

            # Sanity check
            title = re.search('<meta name="description" content="FreeDS - Derivador de energía solar excedente">', html).span()

            _LOGGER.info(f'Found "FreeDS - Derivador de energía solar excedente" in http://{host}:{port}/Red.html .')

            # Scrape hostname (which, by default, contains the 4-hexdigit unique ID)
            # from the network configuration webpage
            hostname = re.search('<label class="col-sm-4 form-control-label language" key="HOSTNAME"></label>\s+<div class="col-sm-8 mg-t-10 mg-sm-t-0">\s+                                                            <input id=\'host\' name="host" type="text" maxlength="11" class="form-control" value="(.*)">\s+</div>', html).groups()[0]

            uniqueid = hostname[-4:]

            _LOGGER.info(f"Scrapped hostname: {hostname} with unique ID {uniqueid}. All scrapping successful.")

            await session.close()
            return {
                "uniqueid": uniqueid,
                "fwversion": fwversion,
            }

        except Exception as err:
            _LOGGER.warning(f"Scraping failed ({err}). The device at {host} doesn't seem to be a FreeDS 1.0.7.")

            await session.close()

            # raise Exception("invalid_host")
            # _LOGGER.error(Exception(err))

            return {
                "uniqueid": None,
                "error": "invalid_host",
                "mode": "sse"
            }

