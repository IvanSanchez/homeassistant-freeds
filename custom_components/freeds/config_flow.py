from homeassistant import config_entries
from .const import DOMAIN
from homeassistant.const import CONF_HOST
import voluptuous as vol
import logging
from typing import Any, Final
from homeassistant.data_entry_flow import FlowResult

_LOGGER = logging.getLogger(__name__)


### TODO: Add HTTP timeout (for the persistent HTTP connection to the FreeDS device)
### Right now a value f 30 seconds is hardcoded.
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
    # info: dict[str, Any] = {}
    uniqueid: str=""

    print ("FreeDSConfigFlow")

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        print ("async_step_user", user_input)

        errors: dict[str, str] = {}
        if user_input is not None:
            # host: str = user_input[CONF_HOST]
            host: str = user_input["host"]
            try:
                ### FIXME!!! Grab the unique ID from the FreeDS device, somehow
                # info = self._async_get_info(host)
                uniqueid = "abcd"
                await self.async_set_unique_id(uniqueid)
                return self.async_create_entry(title=f"FreeDS {uniqueid}", data={"host": user_input["host"], "uniqueid": uniqueid})
            # except DeviceConnecionError:
            #     errors["base"] = "cannot_connect"
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


    # def _async_get_info(self, host):
        ### TODO: Fetch http://${host}/masterdata, check version
        ### Somehow get a unique ID
        # self.id = "abcd"
        # return None

