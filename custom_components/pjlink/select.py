"""The select entities for PjLink."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PjLinkDataUpdateCoordinator, format_input_source
from .entity import PjLinkCapabilityEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PjLink select entities based on a config entry."""
    coordinator: PjLinkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list = []

    if coordinator.data.input is not None:
        entities.append(PjLinkInputSoruce("input_source", "Input source", coordinator))

    async_add_entities(entities)


class PjLinkInputSoruce(PjLinkCapabilityEntity, SelectEntity):
    """Representation of a PjLink Select entity."""

    def __init__(
        self,
        id: str,
        name: str,
        coordinator: PjLinkDataUpdateCoordinator
    ) -> None:
        """Initialize the PjLink Select entity."""
        PjLinkCapabilityEntity.__init__(self, id, name, "", coordinator)

        if self.coordinator.data.input_list is not None:
            self._attr_options = list(format_input_source(*x) for x in self.coordinator.data.input_list)
        else:
            self._attr_options = [self.coordinator.data.input]

    async def async_select_option(self, option: str) -> None:
        """Select the given option."""
        self.coordinator.select_source(option)

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        return self.coordinator.data.input
