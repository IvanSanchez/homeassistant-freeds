"""FreeDS client"""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import sensor
from .const import DOMAIN
from .coordinator import FreeDSCoordinator

PLATFORMS: list[str] = ["sensor", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a FreeDS sensor from a config entry."""

    print ("freeds setup", entry.data)

    uniqueid = entry.data['uniqueid']

    coordinator = FreeDSCoordinator(hass, entry.data['host'], name = f'FreeDS {uniqueid}')

    # Stores a ref to the coordinator in the HASS data. This will be fetched
    # by the different domains (sensors, buttons, binary sensors)
    hass.data.setdefault(DOMAIN, {})[entry.data['uniqueid']] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    print ("freeds unload entry", entry.data)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    # if unload_ok:
        # hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
