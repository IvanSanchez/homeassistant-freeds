"""Platform for button integration."""

from __future__ import annotations

import aiohttp
import asyncio
import logging
from datetime import timedelta

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN
from .entity import FreeDSEntity

_LOGGER = logging.getLogger(__name__)

# How long we disable the button after a reboot
REBOOT_COOLDOWN = timedelta(seconds=90)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Add reboot button for the FreeDS device."""
    unique_id = config_entry.data["uniqueid"]
    common_data = hass.data[DOMAIN][unique_id]

    button = FreeDSRebootButton(
        name="Reboot",
        icon="mdi:restart",
        entity_category=EntityCategory.CONFIG,
        **common_data,
    )

    async_add_entities([button])

    # Store the remove callback so we can clean it up on unload
    async def _check_if_back_online(now=None):
        await button.async_check_if_back_online()

    remove_interval = async_track_time_interval(
        hass, _check_if_back_online, timedelta(seconds=5)
    )

    # Save the remover so we can call it later when the config entry is unloaded
    hass.data[DOMAIN][unique_id]["reboot_check_remover"] = remove_interval

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry) -> bool:
    """Unload the reboot check interval when the integration is removed."""
    unique_id = config_entry.data["uniqueid"]
    remover = hass.data[DOMAIN][unique_id].pop("reboot_check_remover", None)
    if remover:
        remover()
    return True


class FreeDSRebootButton(FreeDSEntity, ButtonEntity):
    """FreeDS reboot button with protection against multiple presses and clear visual feedback."""

    _reboot_in_progress: bool = False
    _seen_offline: bool = False

    @property
    def available(self) -> bool:
        """Button is available only when device is online and not currently rebooting."""
        return super().available and not self._reboot_in_progress

    @property
    def icon(self) -> str:
        """Show a warning icon while reboot is in progress."""
        return "mdi:restart-alert" if self._reboot_in_progress else "mdi:restart"

    async def async_check_if_back_online(self):
        """Check if FreeDS has come back online after a reboot."""
        if not self._reboot_in_progress:
            return

        # Step 1 — wait until device drops offline
        if not self._seen_offline:
            if not self.coordinator.last_update_success:
                _LOGGER.info(f"FreeDS ({self.coordinator.host}) is now offline (expected during reboot).")
                self._seen_offline = True
            return

        # Step 2 — device was offline, now check if it came back
        if self.coordinator.last_update_success:
            _LOGGER.info(f"FreeDS ({self.coordinator.host}) is back online after reboot.")
            self._reboot_in_progress = False
            self.async_write_ha_state()

    async def async_press(self) -> None:
        """Send reboot command only if no reboot is already in progress."""
        if self._reboot_in_progress:
            _LOGGER.warning("Reboot already in progress – ignoring repeated button press.")
            return

        coordinator = self.coordinator
        url = f"http://{coordinator.host}:{coordinator.port}/reboot"

        self._reboot_in_progress = True
        self._seen_offline = False
        self.async_write_ha_state()

        _LOGGER.info(f"Sending reboot command to FreeDS {coordinator.host}...")

        try:
            timeout = aiohttp.ClientTimeout(total=6, sock_read=3)
            async with coordinator.session.get(
                url, auth=coordinator.auth, timeout=timeout
            ) as response:
                if response.status == 200:
                    _LOGGER.info("Reboot command accepted – FreeDS is restarting.")
                else:
                    _LOGGER.warning(f"FreeDS returned HTTP {response.status} on reboot command.")
                    self._reboot_in_progress = False
                    self.async_write_ha_state()

        except asyncio.TimeoutError:
            _LOGGER.info("Connection closed abruptly – expected during FreeDS reboot.")
        except Exception as e:
            _LOGGER.error(f"Unexpected error while sending reboot command: {e}")
            self._reboot_in_progress = False
            self.async_write_ha_state()

        # Safety-net: re-enable button after cooldown even if we miss the reconnect
        async def _force_unblock():
            await asyncio.sleep(REBOOT_COOLDOWN.total_seconds())
            if self._reboot_in_progress:
                _LOGGER.info("Reboot cooldown expired – re-enabling reboot button.")
                self._reboot_in_progress = False
                self.async_write_ha_state()

        asyncio.create_task(_force_unblock())