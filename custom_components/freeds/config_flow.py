from homeassistant import config_entries
from .const import DOMAIN
from homeassistant.const import (CONF_HOST, CONF_PORT)
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

            try:
                info = await self._async_get_info(host, port)

                if (info['uniqueid'] is None):
                    errors["base"] = "invalid_host"
                else:
                    await self.async_set_unique_id(info['uniqueid'])
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(title=f"FreeDS {info['uniqueid']}", data={
                        "host": user_input[CONF_HOST],
                        "port": user_input[CONF_PORT],
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


    async def _async_get_info(self, host, port = 80):

        session = aiohttp.ClientSession()

        # For FreeDS version 1.0.x, try fetching /index.html and scrapping
        # some text strings.

        ### TODO: Implement a more robust method of fetching information for
        ### any newer firmware versions

        try:
            html = await (await session.get(f'http://{host}:{port}/')).text()

            # Sanity check
            title = re.search('<meta name="description" content="FreeDS - Derivador de energía solar excedente">', html).span()

            # Scrape firmware version from page footer
            fwversion = re.search('<div>Copyright © 2020. Derivador de energía solar excedente (.*)</div>', html).groups()[0]

            html = await (await session.get(f'http://{host}:{port}/Red.html')).text()

            # Sanity check
            title = re.search('<meta name="description" content="FreeDS - Derivador de energía solar excedente">', html).span()

            # Scrape hostname (which, by default, contains the 4-hexdigit unique ID)
            # from the network configuration webpage
            hostname = re.search('<label class="col-sm-4 form-control-label language" key="HOSTNAME"></label>\s+<div class="col-sm-8 mg-t-10 mg-sm-t-0">\s+                                                            <input id=\'host\' name="host" type="text" maxlength="11" class="form-control" value="(.*)">\s+</div>', html).groups()[0]

            uniqueid = hostname[-4:]

            session.close()
            return {
                "uniqueid": uniqueid,
                "fwversion": fwversion,
            }

        except Exception as err:
            session.close()

            # raise Exception("invalid_host")
            # _LOGGER.error(Exception(err))

            return {
                "uniqueid": None
            }

