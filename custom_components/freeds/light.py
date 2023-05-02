"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.light import (
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity import EntityCategory

from .entity import FreeDSEntity

from homeassistant.const import (
    UnitOfPower,
    UnitOfEnergy,
    UnitOfTemperature,
    UnitOfElectricPotential,
    UnitOfFrequency,
    PERCENTAGE,
)

import random

from .const import DOMAIN

import traceback


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add lights for passed config_entry in HA."""

    # Fetch coordinator and device_info, needs to be passed to each and
    # every constructor.
    # "data" is a dict like {coordinator, device_info, freeds_id}
    common_data = hass.data[DOMAIN][config_entry.data["uniqueid"]]

    lights = [
        FreeDSLight(
            name="Backlight",
            # icon="mdi:alert",
            entity_category=EntityCategory.DIAGNOSTIC,
            button_idx=5,
            json_section="Web",
            # json_field_on="Oled",
            # json_field_brightness="screenBrightness",
            **common_data,
        ),
    ]

    async_add_entities(lights)


class FreeDSLight(FreeDSEntity, LightEntity):
    """An individual FreeDSSensor entry for binary states."""

    def __init__(self, button_idx=None, **kwargs):
        # Init FreeDSEntity
        super().__init__(**kwargs)

        # Instance attributes built into ToggleEntity
        self._attr_is_on = None

        # Instance attributes built into LightEntity
        self._attr_brightness = None
        self._attr_supported_color_modes = set(ColorMode.BRIGHTNESS)

        # FreeDS-specific
        self._button_idx = button_idx

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        self.json_field = "Oled"
        value_on = super()._handle_coordinator_update()
        self.json_field = "screenBrightness"
        value_bright = super()._handle_coordinator_update()

        if value_on is not None:
            value_on = bool(int(value_on))
            if (
                not self._attr_available
                or value_on != self._attr_is_on
                or value_bright != self._attr_brightness
            ):
                self._attr_available = True
                self._attr_is_on = value_on
                self._attr_brightness = value_bright
                self.async_write_ha_state()

    @property
    def brightness(self):
        if self._attr_brightness is None:
            return None
        else:
            return 1 + self._attr_brightness * 254 / 100

    async def async_turn_on(self, **kwargs):
        if self.is_on:
            pass
        else:
            return await self.coordinator.async_send_toggle_button(self._button_idx)

    async def async_turn_off(self, **kwargs):
        if self.is_on:
            return await self.coordinator.async_send_toggle_button(self._button_idx)
        else:
            pass
