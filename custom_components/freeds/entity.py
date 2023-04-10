
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

class FreeDSEntity(CoordinatorEntity):
    """Funcionality common to all FreeDS entities"""

    def __init__(self,
                 name = None,
                 icon = None,
                 entity_category = None,
                 device_class = None,
                 device_info = None,

                 freeds_id = None,
                 coordinator = None,
                 json_field = None,
                 ):

        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=json_field)

        # Instance attributes built into Entity:
        self._attr_icon = icon
        self._attr_entity_category = entity_category
        self._attr_has_entity_name = True
        self._attr_name = name
        self._attr_unique_id = f"{freeds_id}_{json_field}"
        self._attr_device_class = device_class
        self._attr_available = False
        self._attr_should_poll = False
        self._attr_device_info = device_info

        # FreeDS-specific attributes
        self.coordinator = coordinator
        self.json_field = json_field
        self.freeds_id = freeds_id


    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        # Returns the data for the entity's json_field, *if any*.
        # Sensors should store this in _attr_native_value, while switches and
        # binary sensors should store this in _attr_is_on.

        if (not self.coordinator.last_update_success):
            # This means the coordinator had errors while fetching data
            if (self._attr_available):
                self._attr_available = False
                self.async_write_ha_state()

        elif (self.json_field in self.coordinator.data.keys()):
            return self.coordinator.data[self.json_field]
