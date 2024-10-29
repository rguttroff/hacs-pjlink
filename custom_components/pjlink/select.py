"""The select entities for PjLink."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PjLinkDataUpdateCoordinator
from .entity import PjLinkCapabilityEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PjLink select entities based on a config entry."""
    coordinator: PjLinkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list = []

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
        PjLinkCapabilityEntity.__init__(self, id, name, coordinator)
        self._attr_options = list(coordinator.data.input_list)

    async def async_select_option(self, option: str) -> None:
        """Select the given option."""
        await self.coordinator.select_source(value)

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        return self.coordinator.data.input
