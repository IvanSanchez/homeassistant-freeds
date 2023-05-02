"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
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
    """Add sensors for passed config_entry in HA."""

    # Fetch coordinator and device_info, needs to be passed to each and
    # every constructor.
    # "data" is a dict like {coordinator, device_info, freeds_id}
    common_data = hass.data[DOMAIN][config_entry.data["uniqueid"]]

    sensors = [
        FreeDSBinarySensor(
            name="Error",
            device_class=BinarySensorDeviceClass.PROBLEM,
            # icon="mdi:alert",
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Web",
            json_field="error",
            **common_data,
        ),
    ]

    async_add_entities(sensors)


class FreeDSBinarySensor(FreeDSEntity, BinarySensorEntity):
    """An individual FreeDSSensor entry for binary states."""

    def __init__(self, **kwargs):
        # Init FreeDSEntity
        super().__init__(**kwargs)

        # Instance attributes built into BinarySensorEntity
        self._attr_is_on = None

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        value = super()._handle_coordinator_update()

        if value is not None:
            value = bool(int(value))
            if not self._attr_available or value != self._attr_is_on:
                self._attr_available = True
                self._attr_is_on = value
                self.async_write_ha_state()
