"""FreeDS client"""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import sensor
from .const import DOMAIN
from .coordinator import FreeDSCoordinator

PLATFORMS: list[str] = ["sensor", "binary_sensor", "switch", "light"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a FreeDS sensor from a config entry."""

    uniqueid = entry.data["uniqueid"]
    host = entry.data["host"]
    port = entry.data["port"]
    user = entry.data["username"]
    passwd = entry.data["password"]

    if user is None:
        configuration_url = f"http://{host}:{port}"
    else:
        configuration_url = f"http://{user}:{passwd}@{host}:{port}"

    coordinator = FreeDSCoordinator(
        hass,
        host,
        port=port,
        user=user,
        passwd=passwd,
        name=f"FreeDS {uniqueid} HTTP client",
    )

    # TODO:(re-)fetch FW version from coordinator

    # Stores a ref to the coordinator & device info in the HASS data. This will
    # be fetched by the different domains (sensors, buttons, binary sensors)
    hass.data.setdefault(DOMAIN, {})[entry.data["uniqueid"]] = {
        "freeds_id": uniqueid,
        "coordinator": coordinator,
        "device_info": {
            "identifiers": {(DOMAIN, uniqueid)},
            "name": f"FreeDS {uniqueid}",
            "configuration_url": configuration_url,
            # "config_entries": [entry],
            # "default_manufacturer": "FreeDS"
            "sw_version": entry.data["fwversion"],
        },
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    # print ("freeds unload entry", entry.data)

    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)
    # if unload_ok:
    # hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
