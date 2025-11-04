"""Platform for button integration."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN
from .entity import FreeDSEntity

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Add button for passed config_entry in HA."""
    common_data = hass.data[DOMAIN][config_entry.data["uniqueid"]]

    async_add_entities(
        [
            FreeDSRebootButton(
                name="Reboot",
                icon="mdi:restart",
                entity_category=EntityCategory.CONFIG,
                **common_data,
            )
        ]
    )


class FreeDSRebootButton(FreeDSEntity, ButtonEntity):
    """FreeDS reboot button."""

    async def async_press(self) -> None:
        coordinator = self.coordinator
        url = f"http://{coordinator.host}:{coordinator.port}/reboot"

        try:
            _LOGGER.info(f"Sending reboot command to {url}")
            response = await coordinator.session.get(url, auth=coordinator.auth)

            if response.status == 200:
                _LOGGER.info("FreeDS reboot command accepted successfully.")
            else:
                _LOGGER.warning(f"Unexpected HTTP {response.status} on reboot.")
            await response.text()

        except Exception as e:
            _LOGGER.error(f"Failed to send reboot command: {e}")
