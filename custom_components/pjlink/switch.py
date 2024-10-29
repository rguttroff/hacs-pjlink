"""The switch entities for PjLink."""

from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up PjLink sensor based on a config entry."""
    coordinator: PjLinkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list = []

    entities.append(PjLinkPowerSwitch("power", "Power", coordinator))

    async_add_entities(entities)


class PjLinkPowerSwitch(PjLinkCapabilityEntity, SwitchEntity):
    """Representation of a PjLink power switch."""

    @property
    def is_on(self) -> bool:
        """Return the current status."""
        return self.coordinator.data.power

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the capability."""
        await self.coordinator.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the capability."""
        await self.capability.turn_off()