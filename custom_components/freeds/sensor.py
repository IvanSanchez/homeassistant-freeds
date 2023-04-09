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

from .const import (
    DOMAIN,
    WORKING_MODES
)


import traceback

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""

    coordinator = hass.data[DOMAIN][config_entry.data['uniqueid']]

    uniqueid = config_entry.data["uniqueid"]

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
            coordinator=coordinator
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
            coordinator=coordinator
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
            coordinator=coordinator
        ),
        FreeDSSensor(
            label="PWM frequency",
            unit=UnitOfFrequency.HERTZ,
            dev_class=SensorDeviceClass.FREQUENCY,
            icon="mdi:square-wave",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_field="pwmfrec",
            uniqueid=uniqueid,
            coordinator=coordinator
        ),
        FreeDSSensor(
            label="PWM %",
            unit=PERCENTAGE,
            icon="mdi:square-wave",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="pwm",
            uniqueid=uniqueid,
            coordinator=coordinator
        ),
        FreeDSTemperatureSensor(
            label="Heater Temperature",
            unit=UnitOfTemperature.CELSIUS,
            dev_class=SensorDeviceClass.TEMPERATURE,
            icon="mdi:thermometer-water",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="tempTermo",
            uniqueid=uniqueid,
            coordinator=coordinator
        ),
        FreeDSTemperatureSensor(
            label="TRIAC Temperature",
            unit=UnitOfTemperature.CELSIUS,
            dev_class=SensorDeviceClass.TEMPERATURE,
            icon="mdi:thermometer",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="tempTriac",
            uniqueid=uniqueid,
            coordinator=coordinator
        ),
        FreeDSTemperatureSensor(
            label="Custom Temperature",
            unit=UnitOfTemperature.CELSIUS,
            dev_class=SensorDeviceClass.TEMPERATURE,
            icon="mdi:thermometer",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="tempCustom",
            uniqueid=uniqueid,
            coordinator=coordinator
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
            coordinator=coordinator
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
            coordinator=coordinator
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
            coordinator=coordinator
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
            coordinator=coordinator
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
            coordinator=coordinator
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
            coordinator=coordinator
        ),
        FreeDSSensor(
            label="Voltage",
            unit=UnitOfElectricPotential.VOLT,
            dev_class=SensorDeviceClass.VOLTAGE,
            icon="mdi:sine-wave",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_field="mvoltage",
            uniqueid=uniqueid,
            coordinator=coordinator
        ),
        FreeDSWorkingModeSensor(
            label="Working Mode",
            unit=None,
            dev_class=SensorDeviceClass.ENUM,
            icon="mdi:lan",
            state_class=None,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_field="wversion",
            uniqueid=uniqueid,
            coordinator=coordinator
        ),
    ]

    async_add_entities(sensors)


class FreeDSSensor(CoordinatorEntity, SensorEntity):
    """An individual FreeDSsensor entry."""

    # native_value = None

    def __init__ (self,
                  label,
                  icon,
                  unit,
                  state_class,
                  json_field,
                  uniqueid,
                  coordinator,
                  dev_class = None,
                  entity_category = None):

        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=json_field)

        # Instance attributes built into Entity:
        self._attr_icon = icon
        self._attr_entity_category = entity_category
        self._attr_name = f"FreeDS {uniqueid} {label}"
        self._attr_unique_id = f"{uniqueid}_{json_field}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = dev_class
        self._attr_available = False

        # Instance attributes built into Sensor:
        self._attr_state_class = state_class
        self._attr_native_value = None

        self.freeds_unique_id = uniqueid
        self.json_field = json_field

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
            if (not self._attr_available or value != self._attr_native_value):
                self._attr_available = True
                self._attr_native_value = self.coordinator.data[self.json_field]
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


class FreeDSTemperatureSensor(FreeDSSensor):
    # As FreeDSSensor, but handles the literal "-127.0" string as None.
    # FreeDS sends "-127.0" as the temperature value when there is no
    # temperature probe.

    @property
    def available(self):
        return (self._attr_native_value != "-127.0")


class FreeDSWorkingModeSensor(FreeDSSensor):
    # As FreeDSSensor, but translates the (known) numerical working modes into
    # readable strings, as per the defined constants. e.g. working mode 25
    # gets translated to "Shelly EM"

    @property
    def native_value(self):
        if (self._attr_native_value is None):
            return None
        else:
            return WORKING_MODES[self._attr_native_value]
