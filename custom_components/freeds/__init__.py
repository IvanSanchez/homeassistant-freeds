"""FreeDS client"""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import sensor
from .const import DOMAIN

PLATFORMS: list[str] = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a FreeDS sensor from a config entry."""

    print ("freeds setup", entry.data)

    # entry.data["custom"] = "custom123";
    # hass.data.setdefault(DOMAIN, {})[entry.entry_id] = sensor.BatterySensor(hass, entry.data["host"])

    # hass.config_entries.async_setup_platforms(entry, PLATFORMS)
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
