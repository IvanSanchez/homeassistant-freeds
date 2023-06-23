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
    UnitOfElectricCurrent,
    UnitOfFrequency,
    PERCENTAGE,
)

import random

from .const import (
    DOMAIN,
    WORKING_MODES_1_0,
    WORKING_MODES_1_1,
)

from .entity import FreeDSEntity

import traceback


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""

    # Fetch coordinator and device_info, needs to be passed to each and
    # every constructor.
    # "data" is a dict like {coordinator, device_info, freeds_id}
    common_data = hass.data[DOMAIN][config_entry.data["uniqueid"]]

    sensors = [
        FreeDSNumericSensor(
            name="Solar Power",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            icon="mdi:solar-power",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Inverter",
            json_field="wsolar",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Grid Power",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            # icon="mdi:transmission-tower",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Inverter",
            json_field="wgrid",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Grid Voltage",
            unit=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            # icon="mdi:transmission-tower",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Inverter",
            json_field="gridv",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Battery Power",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            icon="mdi:battery-charging",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Inverter",
            json_field="wbattery",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Surplus Load",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            # icon="mdi:flash",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Web",
            json_field="loadCalcWatts",
            **common_data,
        ),
        FreeDSPWMFrequencySensor(
            name="PWM frequency",
            unit=UnitOfFrequency.HERTZ,
            device_class=SensorDeviceClass.FREQUENCY,
            icon="mdi:square-wave",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Web",
            json_field="pwmfrec",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="PWM %",
            unit=PERCENTAGE,
            icon="mdi:square-wave",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Web",
            json_field="pwm",
            **common_data,
        ),
        FreeDSTemperatureSensor(
            name="Heater Temperature",
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            icon="mdi:thermometer-water",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Temperature",
            json_field="tempTermo",
            **common_data,
        ),
        FreeDSTemperatureSensor(
            name="TRIAC Temperature",
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            # icon="mdi:thermometer",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Temperature",
            json_field="tempTriac",
            **common_data,
        ),
        FreeDSTemperatureSensor(
            name="Inverter Temperature",
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            # icon="mdi:thermometer",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Inverter",
            json_field="invTemp",
            **common_data,
        ),
        FreeDSTemperatureSensor(
            name="Custom Temperature",
            unit=UnitOfTemperature.CELSIUS,
            device_class=SensorDeviceClass.TEMPERATURE,
            # icon="mdi:thermometer",
            state_class=SensorStateClass.MEASUREMENT,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Temperature",
            json_field="tempCustom",
            **common_data,
        ),
        # FreeDSSensor(
        #     name="Inverter state of charge",
        #     unit=PERCENTAGE,
        #     device_class=SensorDeviceClass.BATTERY,
        #     # icon="mdi:resistor",
        #     state_class=SensorStateClass.MEASUREMENT,
        #     # entity_category=EntityCategory.DIAGNOSTIC,
        #     json_field="invSoC",
        #     **common_data
        # ),
        FreeDSNumericSensor(
            name="Inverter Line 1 Voltage",
            unit=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            # icon="mdi:resistor",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Inverter",
            json_field="pv1v",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Inverter Line 1 Current",
            unit=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            # icon="mdi:resistor",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Inverter",
            json_field="pv1c",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Inverter Line 1 Power",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            # icon="mdi:resistor",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Inverter",
            json_field="pv1w",
            # json_field="pw1", # Typo in 1.0.7rev2!
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Inverter Line 2 Voltage",
            unit=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            # icon="mdi:resistor",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Inverter",
            json_field="pv2v",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Inverter Line 2 Current",
            unit=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            # icon="mdi:resistor",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Inverter",
            json_field="pv2c",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Inverter Line 2 Power",
            unit=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            # icon="mdi:resistor",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Inverter",
            json_field="pv2w",
            # json_field="pw1", # Typo in 1.0.7rev2!
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Surplus Energy (Today)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            # icon="mdi:resistor",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Energy",
            json_field="KwToday",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Surplus Energy (Yesterday)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            # icon="mdi:resistor",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Energy",
            json_field="KwYesterday",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Surplus Energy (Total)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            # icon="mdi:resistor",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Energy",
            json_field="KwTotal",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Exported Energy (Today)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            icon="mdi:transmission-tower-import",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Energy",
            json_field="KwExportToday",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Exported Energy (Yesterday)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            icon="mdi:transmission-tower-import",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Energy",
            json_field="KwExportYesterday",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Exported Energy (Total)",
            unit=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            icon="mdi:transmission-tower-import",
            state_class=SensorStateClass.TOTAL_INCREASING,
            # entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Energy",
            json_field="KwExportTotal",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="AC Voltage",
            unit=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            # icon="mdi:sine-wave",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Meter",
            json_field="mvoltage",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="AC Current",
            unit=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            # icon="mdi:sine-wave",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Meter",
            json_field="mcurrent",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="AC Frequency",
            unit=UnitOfFrequency.HERTZ,
            device_class=SensorDeviceClass.FREQUENCY,
            # icon="mdi:sine-wave",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Meter",
            json_field="mfrequency",
            **common_data,
        ),
        FreeDSNumericSensor(
            name="Power Factor",
            unit=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            # icon="mdi:sine-wave",
            state_class=SensorStateClass.MEASUREMENT,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Meter",
            json_field="mpowerFactor",
            **common_data,
        ),
        FreeDSWorkingModeSensor(
            name="Working Mode",
            unit=None,
            device_class=SensorDeviceClass.ENUM,
            icon="mdi:lan",
            # state_class=None,
            entity_category=EntityCategory.DIAGNOSTIC,
            json_section="Web",
            # json_field="wversion", # Name change between 1.0.x and 1.1-beta
            json_field="workingMode",
            **common_data,
        ),
    ]

    async_add_entities(sensors)


class FreeDSSensor(FreeDSEntity, SensorEntity):
    """An individual FreeDSsensor entry."""

    def __init__(self, state_class=None, unit=None, **kwargs):
        # Init FreeDSEntity
        super().__init__(**kwargs)

        # Instance attributes built into SensorEntity:
        self._attr_state_class = state_class
        self._attr_native_value = None
        self._attr_native_unit_of_measurement = unit

        # All sensors should start as unavailable. Some of them will never be,
        # depending on the FreeDS Working Mode.
        self._attr_available = False

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        value = super()._handle_coordinator_update()

        if value is not None and (
            not self._attr_available or value != self._attr_native_value
        ):
            self._attr_available = True
            self._attr_native_value = value
            self.async_write_ha_state()

    @property
    def available(self):
        return self._attr_available and self._attr_native_value is not None


class FreeDSNumericSensor(FreeDSSensor):
    """A FreeDS Sensor which ignores non-numerical values"""

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        try:
            value = float(self.coordinator.data[self.json_section][self.json_field])
        except:
            value = None

        if value is not None and self.coordinator.last_update_success:
            if not self._attr_available or value != self._attr_native_value:
                self._attr_available = True
                self._attr_native_value = value
                self.async_write_ha_state()
        else:
            self._attr_available = False
            self._attr_native_value = value
            self.async_write_ha_state()


class FreeDSTemperatureSensor(FreeDSSensor):
    # As FreeDSSensor, but handles the literal "-127.0" string as being
    # not available. FreeDS sends "-127.0" as the temperature value when
    # there is no temperature probe.

    @property
    def available(self):
        return self._attr_available and self._attr_native_value != "-127.0"


class FreeDSPWMFrequencySensor(FreeDSSensor):
    # As FreeDSSensor, but the value displayed is one tenth of the received one.
    # For whatever reason, FreeDS reports pwm frequency values in decihertz, not
    # in hertz/kilohertz.

    @property
    def native_value(self):
        return int(self._attr_native_value) / 10


class FreeDSWorkingModeSensor(FreeDSSensor):
    # As FreeDSSensor, but translates the (known) numerical working modes into
    # readable strings, as per the defined constants. e.g. working mode 25
    # gets translated to "Shelly EM"

    @property
    def native_value(self):
        if self._attr_native_value is None:
            return None
        elif self.coordinator.mode == "websocket":
            return (
                WORKING_MODES_1_1.get(self._attr_native_value)
                or self._attr_native_value
            )
        else:
            return (
                WORKING_MODES_1_0.get(self._attr_native_value)
                or self._attr_native_value
            )
