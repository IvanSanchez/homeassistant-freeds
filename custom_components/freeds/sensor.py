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
            label="Surplus Load",
            unit=UnitOfPower.WATT,
            dev_class=SensorDeviceClass.POWER,
            icon="mdi:flash",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="loadCalcWatts",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="PWM frequency",
            unit=UnitOfFrequency.HERTZ,
            dev_class=SensorDeviceClass.FREQUENCY,
            icon="mdi:square-wave",
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
            icon="mdi:square-wave",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="pwm",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="Heater Temperature",
            unit=UnitOfTemperature.CELSIUS,
            dev_class=SensorDeviceClass.TEMPERATURE,
            icon="mdi:thermometer-water",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="tempTermo",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="TRIAC Temperature",
            unit=UnitOfTemperature.CELSIUS,
            dev_class=SensorDeviceClass.TEMPERATURE,
            icon="mdi:thermometer",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="tempTriac",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="Custom Temperature",
            unit=UnitOfTemperature.CELSIUS,
            dev_class=SensorDeviceClass.TEMPERATURE,
            icon="mdi:thermometer",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="tempCustom",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="Surplus Energy (Today)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            dev_class=SensorDeviceClass.ENERGY,
            icon="mdi:resistor",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="KwToday",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="Surplus Energy (Yesterday)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            dev_class=SensorDeviceClass.ENERGY,
            icon="mdi:resistor",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="KwYesterday",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="Surplus Energy (Total)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            dev_class=SensorDeviceClass.ENERGY,
            icon="mdi:resistor",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="KwTotal",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="Exported Energy (Today)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            dev_class=SensorDeviceClass.ENERGY,
            icon="mdi:transmission-tower-import",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="KwExportToday",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="Exported Energy (Yesterday)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            dev_class=SensorDeviceClass.ENERGY,
            icon="mdi:transmission-tower-import",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="KwExportYesterday",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="Exported Energy (Total)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            dev_class=SensorDeviceClass.ENERGY,
            icon="mdi:transmission-tower-import",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="KwExportTotal",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
        FreeDSSensor(
            label="Voltage",
            unit=UnitOfElectricPotential.VOLT,
            dev_class=SensorDeviceClass.VOLTAGE,
            icon="mdi:sine-wave",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="mvoltage",
            uniqueid=uniqueid,
            http_client=httpClient
        ),
    ]

    async_add_entities(sensors)


class FreeDSSensor(SensorEntity):
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
        self._icon = icon
        self._unit_of_measurement = unit
        self._device_class = dev_class
        self._state_class = state_class
        self._entity_category = entity_category
        self.json_field = json_field
        self._name = f"FreeDS {uniqueid} {label}"
        # self._name = label
        self.freeds_unique_id = uniqueid

        self._id = f"{uniqueid}_{json_field}"
        http_client.register(json_field, self.handle_update)

    def handle_update(self, value):
        # print ("FreeDS sensor handling update from http client")
        if (self.device_class == SensorDeviceClass.TEMPERATURE and value == "-127.0"):
            self.last_known_value = None
        else:
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
            "identifiers": { (DOMAIN, self.freeds_unique_id) },
            "name": f"FreeDS {self.freeds_unique_id}",
            # "sw_version": None,
            # "model": None,
            # "manufacturer": None,
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
    def unique_id(self): return self._id

