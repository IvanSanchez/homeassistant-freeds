"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.const import (
    UnitOfPower,
    UnitOfEnergy,
    UnitOfTemperature,
    UnitOfElectricPotential,
    UnitOfFrequency,
    PERCENTAGE
)

import random

from homeassistant.helpers.entity import Entity

from .const import DOMAIN

from .freeds_http_client import FreeDSHTTPClient

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    print ("freeds/sensor.py async create entry", config_entry.data)

    uniqueid = config_entry.data["uniqueid"]

    httpClient = FreeDSHTTPClient(config_entry.data["host"])

    sensors = [
        FreeDSSensor(
            label="Solar Power",
            unit=UnitOfPower.WATT,
            dev_class=SensorDeviceClass.POWER,
            icon="mdi:solar-power",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="wsolar",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="Grid Power",
            unit=UnitOfPower.WATT,
            dev_class=SensorDeviceClass.POWER,
            icon="mdi:transmission-tower",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="wgrid",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="PWM frequency",
            unit=UnitOfFrequency.HERTZ,
            dev_class=SensorDeviceClass.FREQUENCY,
            icon="mdi:sine-wave",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="pwmfrec",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="PWM",
            unit=PERCENTAGE,
            # dev_class=SensorDeviceClass.POWER_FACTOR,
            icon="mdi:sine-wave",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="pwm",
            uniqueid=uniqueid,
            http_client=httpClient
        ),

    ]

    async_add_entities(sensors)


class FreeDSSensor(Entity):
    """An individual FreeDSsensor entry."""

    # should_poll = False

    last_known_value = None

    def __init__ (self,
                  label,
                  icon,
                  unit,
                  state_class,
                  json_field,
                  uniqueid,
                  http_client,
                  dev_class = None,
                  entity_category = None):
        self.label = label
        self._icon = icon
        self._unit_of_measurement = unit
        self._device_class = dev_class
        self._state_class = state_class
        self._entity_category = entity_category
        self.json_field = json_field
        self._name = f"FreeDS {uniqueid} {label}"
        self._unique_id = f"{uniqueid}-{json_field}"
        self.freeds_unique_id = uniqueid

        http_client.register(json_field, self.handle_update)

    def handle_update(self, value):
        # print ("FreeDS sensor handling update from http client")
        self.last_known_value = value
        self.async_write_ha_state()

    def available(self) -> bool:
        """Return True if FreeDS is available."""
        return self.last_known_value is not None

    @property
    def state(self):
        return self.last_known_value

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {
            "identifiers": {
                (DOMAIN, self.freeds_unique_id),
            }
        }

    @property
    def icon(self): return self._icon
    @property
    def unit_of_measurement(self): return self._unit_of_measurement
    @property
    def device_class(self): return self._device_class
    @property
    def state_class(self): return self._state_class
    @property
    def entity_category(self): return self._entity_category
    @property
    def name(self): return self._name
    @property
    def unique_id(self): return self._unique_id

    # @property




