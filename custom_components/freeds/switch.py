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

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from homeassistant.const import (
    UnitOfPower,
    UnitOfEnergy,
    UnitOfTemperature,
    UnitOfElectricPotential,
    UnitOfFrequency,
    PERCENTAGE
)

import random

from .const import DOMAIN

import traceback

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add switches for passed config_entry in HA."""

    coordinator = hass.data[DOMAIN][config_entry.data['uniqueid']]

    uniqueid = config_entry.data["uniqueid"]

    switches = [
        FreeDSSwitch(
            label="PWM Enabled",
            # dev_class=BinarySensorDeviceClass.PLUG,
            icon="mdi:square-wave",
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="POn",
            button_idx = 6,
            uniqueid=uniqueid,
            coordinator=coordinator
        ),
        FreeDSSwitch(
            label="PWM Manual Mode",
            # dev_class=BinarySensorDeviceClass.PLUG,
            icon="mdi:square-wave",
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="PwmMan",
            button_idx = 7,
            uniqueid=uniqueid,
            coordinator=coordinator
        ),
    ]

    async_add_entities(switches)


class FreeDSSwitch(CoordinatorEntity, BinarySensorEntity):
    """An individual FreeDSsensor entry."""

    # should_poll = False

    _state = None

    def __init__ (self,
                  label,
                  icon,
                  json_field,
                  uniqueid,
                  coordinator,
                  button_idx,
                  dev_class = None,
                  entity_category = None):

        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=json_field)

        self._icon = icon
        self._device_class = dev_class
        self._entity_category = entity_category
        self.json_field = json_field
        self._name = f"FreeDS {uniqueid} {label}"
        self.freeds_unique_id = uniqueid
        self._button_idx = button_idx

        self._id = f"{uniqueid}_{json_field}"


    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if (not self.json_field in self.coordinator.data.keys()):
            return

        value = self.coordinator.data[self.json_field]
        if (value != self._state):
            self._state = self.coordinator.data[self.json_field]
            self.async_write_ha_state()

    @property
    def is_on(self) -> bool:
        return bool(self._state)

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {
            "identifiers": { (DOMAIN, self.freeds_unique_id) },
            "name": f"FreeDS {self.freeds_unique_id}",
            # "sw_version": None,
            # "model": None,
            # "manufacturer": None,
        }


    async def async_turn_on(self):
        if self.is_on:
            pass
        else:
            return await self.coordinator.async_send_toggle_button(self._button_idx)

    async def async_turn_off(self):
        if self.is_on:
            return await self.coordinator.async_send_toggle_button(self._button_idx)
        else:
            pass


    @property
    def icon(self): return self._icon
    @property
    def device_class(self): return self._device_class
    @property
    def entity_category(self): return self._entity_category
    @property
    def name(self): return self._name
    @property
    def unique_id(self): return self._id
