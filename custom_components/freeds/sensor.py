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

from .entity import FreeDSEntity

import traceback

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""

    # Fetch coordinator and device_info, needs to be passed to each and
    # every constructor.
    # "data" is a dict like {coordinator, device_info, freeds_id}
    common_data = hass.data[DOMAIN][config_entry.data['uniqueid']]

    sensors = [
        FreeDSSensor(
            name="Solar Power",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            icon="mdi:solar-power",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="wsolar",
            **common_data
        ),
        FreeDSSensor(
            name="Grid Power",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            # icon="mdi:transmission-tower",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="wgrid",
            **common_data
        ),
        FreeDSSensor(
            name="Surplus Load",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            # icon="mdi:flash",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="loadCalcWatts",
            **common_data
        ),
        FreeDSSensor(
            name="PWM frequency",
            unit=UnitOfFrequency.HERTZ,
            device_class=SensorDeviceClass.FREQUENCY,
            icon="mdi:square-wave",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_field="pwmfrec",
            **common_data
        ),
        FreeDSSensor(
            name="PWM %",
            unit=PERCENTAGE,
            icon="mdi:square-wave",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="pwm",
            **common_data
        ),
        FreeDSTemperatureSensor(
            name="Heater Temperature",
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            icon="mdi:thermometer-water",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="tempTermo",
            **common_data
        ),
        FreeDSTemperatureSensor(
            name="TRIAC Temperature",
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            # icon="mdi:thermometer",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="tempTriac",
            **common_data
        ),
        FreeDSTemperatureSensor(
            name="Custom Temperature",
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            # icon="mdi:thermometer",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="tempCustom",
            **common_data
        ),
        FreeDSSensor(
            name="Surplus Energy (Today)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            # icon="mdi:resistor",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="KwToday",
            **common_data
        ),
        FreeDSSensor(
            name="Surplus Energy (Yesterday)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            # icon="mdi:resistor",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="KwYesterday",
            **common_data
        ),
        FreeDSSensor(
            name="Surplus Energy (Total)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            # icon="mdi:resistor",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="KwTotal",
            **common_data
        ),
        FreeDSSensor(
            name="Exported Energy (Today)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            icon="mdi:transmission-tower-import",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="KwExportToday",
            **common_data
        ),
        FreeDSSensor(
            name="Exported Energy (Yesterday)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            icon="mdi:transmission-tower-import",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="KwExportYesterday",
            **common_data
        ),
        FreeDSSensor(
            name="Exported Energy (Total)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            icon="mdi:transmission-tower-import",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_field="KwExportTotal",
            **common_data
        ),
        FreeDSSensor(
            name="Voltage",
            unit=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            # icon="mdi:sine-wave",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_field="mvoltage",
            **common_data
        ),
        FreeDSWorkingModeSensor(
            name="Working Mode",
            unit=None,
            device_class=SensorDeviceClass.ENUM,
            icon="mdi:lan",
            # state_class=None,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_field="wversion",
            **common_data
        ),
    ]

    async_add_entities(sensors)


class FreeDSSensor(FreeDSEntity, SensorEntity):
    """An individual FreeDSsensor entry."""

    def __init__ (self,
                  state_class = None,
                  unit = None,
                  **kwargs
                  ):

        # Init FreeDSEntity
        super().__init__(**kwargs)

        # Instance attributes built into SensorEntity:
        self._attr_state_class = state_class
        self._attr_native_value = None
        self._attr_native_unit_of_measurement = unit


    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        value = super()._handle_coordinator_update()

        if (value is not None and (
            not self._attr_available or value != self._attr_native_value)
        ):
            self._attr_available = True
            self._attr_native_value = self.coordinator.data[self.json_field]
            self.async_write_ha_state()


class FreeDSTemperatureSensor(FreeDSSensor):
    # As FreeDSSensor, but handles the literal "-127.0" string as being
    # not available. FreeDS sends "-127.0" as the temperature value when
    # there is no temperature probe.

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
