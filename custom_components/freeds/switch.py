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
    PERCENTAGE,
)

import random

from .const import DOMAIN
from .entity import FreeDSEntity

import traceback


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add switches for passed config_entry in HA."""

    # Fetch coordinator and device_info, needs to be passed to each and
    # every constructor.
    # "data" is a dict like {coordinator, device_info, freeds_id}
    common_data = hass.data[DOMAIN][config_entry.data["uniqueid"]]

    switches = [
        FreeDSSwitch(
            name="PWM Enabled",
            device_class=SwitchDeviceClass.SWITCH,
            icon="mdi:square-wave",
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Web",
            json_field="POn",
            button_idx=6,
            **common_data,
        ),
        FreeDSSwitch(
            name="PWM Manual Mode",
            device_class=SwitchDeviceClass.SWITCH,
            icon="mdi:square-wave",
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Web",
            json_field="PwmMan",
            button_idx=7,
            **common_data,
        ),
        FreeDSSwitch(
            name="Relay 1",
            device_class=SwitchDeviceClass.SWITCH,
            icon="mdi:connection",
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Relays",
            json_field="R01",
            button_idx=1,
            **common_data,
        ),
        FreeDSSwitch(
            name="Relay 2",
            device_class=SwitchDeviceClass.SWITCH,
            icon="mdi:connection",
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Relays",
            json_field="R02",
            button_idx=2,
            **common_data,
        ),
        FreeDSSwitch(
            name="Relay 3",
            device_class=SwitchDeviceClass.SWITCH,
            icon="mdi:connection",
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Relays",
            json_field="R03",
            button_idx=3,
            **common_data,
        ),
        FreeDSSwitch(
            name="Relay 4",
            device_class=SwitchDeviceClass.SWITCH,
            icon="mdi:connection",
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Relays",
            json_field="R04",
            button_idx=4,
            **common_data,
        ),
    ]

    async_add_entities(switches)


class FreeDSSwitch(FreeDSEntity, SwitchEntity):
    """An individual FreeDSSwitch entry, used for relays and enabling PWM."""

    def __init__(self, button_idx=None, **kwargs):
        # Init FreeDSEntity
        super().__init__(**kwargs)

        # Instance attributes built into SwitchEntity
        self._attr_is_on = None

        self._button_idx = button_idx

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        value = super()._handle_coordinator_update()

        if value is not None:
            value = bool(int(value))
            if not self._attr_available or value != self._attr_is_on:
                self._attr_available = True
                self._attr_is_on = value
                self.async_write_ha_state()

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
