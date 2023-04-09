"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
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
            dev_class=SwitchDeviceClass.SWITCH,
            icon="mdi:square-wave",
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="POn",
            button_idx = 6,
            uniqueid=uniqueid,
            coordinator=coordinator
        ),
        FreeDSSwitch(
            label="PWM Manual Mode",
            dev_class=SwitchDeviceClass.SWITCH,
            icon="mdi:square-wave",
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="PwmMan",
            button_idx = 7,
            uniqueid=uniqueid,
            coordinator=coordinator
        ),
    ]

    async_add_entities(switches)


class FreeDSSwitch(CoordinatorEntity, SwitchEntity):
    """An individual FreeDSSwitch entry, used for relays and enabling PWM."""

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

        # Instance attributes built into Entity:
        self._attr_icon = icon
        self._attr_entity_category = entity_category
        self._attr_name = f"FreeDS {uniqueid} {label}"
        self._attr_unique_id = f"{uniqueid}_{json_field}"
        self._attr_device_class = dev_class
        self._attr_available = False

        # Instance attributes built into Switch:

        self.freeds_unique_id = uniqueid
        self.json_field = json_field
        self._button_idx = button_idx


    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if (self.coordinator.data is None):
            # This means the coordinator couldn't fetch any data at all,
            # i.e. an error
            if (self._attr_available):
                self._attr_available = False
                self.async_write_ha_state()

        elif (not self.json_field in self.coordinator.data.keys()):
            # Last coordinator update didn't include data for this entity
            pass
        else:
            value = self.coordinator.data[self.json_field]
            if (not self._attr_available or value != self._attr_is_on):
                self._attr_available = True
                self._attr_is_on = value
                self.async_write_ha_state()


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
