from homeassistant import config_entries
from .const import DOMAIN
from homeassistant.const import CONF_HOST
import voluptuous as vol
import logging
from typing import Any, Final
from homeassistant.data_entry_flow import FlowResult
from getmac import get_mac_address


_LOGGER = logging.getLogger(__name__)


### TODO: Add HTTP timeout (for the persistent HTTP connection to the FreeDS device)
### Right now a value of 30 seconds is hardcoded.
HOST_SCHEMA: Final = vol.Schema({vol.Required(CONF_HOST): str})
# HOST_SCHEMA = vol.Schema({("host"): str})



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
            host: str = user_input["host"]
            try:
                ### FIXME!!! Grab the unique ID from the FreeDS device, somehow
                info = self._async_get_info(host)

                print (info)

                if (info['uniqueid'] is None):
                    errors["base"] = "invalid_host"
                else:
                    await self.async_set_unique_id(info['uniqueid'])
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(title=f"FreeDS {info['uniqueid']}", data={
                        "host": user_input["host"],
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


    def _async_get_info(self, host):

        # Fetch the host's MAC address.
        # HASS config allows for a generic hostname/ip/FQDN input, but
        # the `getmac` package works with either IP or hostname, explicitly.
        # This looks for the MAC daisy-chaining getmac methods.
        mac = get_mac_address(ip=host)
        if (mac is None):
            mac = get_mac_address(hostname=host)
            if (mac is None):
                mac = get_mac_address(ip6=host)

        uniqueid = None
        if (mac is not None):
            # ID is the two last bytes of the MAC; one goes from characters 12 to 14,
            # the other from 15 to 17
            uniqueid = mac[12:14] + mac[15:17]

        ### FIXME: Fetch the firmware version and compilation date

        return {
            'uniqueid': uniqueid,
            'fwversion': None
        }

