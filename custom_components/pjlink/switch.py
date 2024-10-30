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

    if coordinator.data.audio_mute is not None:
        entities.append(PjLinkAudioMuteSwitch("audio_mute", "Audio Mute", coordinator))

    if coordinator.data.video_mute is not None:
        entities.append(PjLinkVideoMuteSwitch("video_mute", "Video Mute", coordinator))

    async_add_entities(entities)


class PjLinkPowerSwitch(PjLinkCapabilityEntity, SwitchEntity):
    """Representation of a PjLink power switch."""

    def __init__(
        self,
        id: str,
        name: str,
        coordinator: PjLinkDataUpdateCoordinator
    ) -> None:
        """Initialize the PjLink Select entity."""
        PjLinkCapabilityEntity.__init__(self, id, name, "", coordinator)

    @property
    def is_on(self) -> bool:
        """Return the current status."""
        return self.coordinator.data.power

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the capability."""
        self.coordinator.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the capability."""
        self.coordinator.turn_off()

class PjLinkAudioMuteSwitch(PjLinkCapabilityEntity, SwitchEntity):
    """Representation of a PjLink audio mute switch."""

    def __init__(
        self,
        id: str,
        name: str,
        coordinator: PjLinkDataUpdateCoordinator
    ) -> None:
        """Initialize the PjLink Select entity."""
        PjLinkCapabilityEntity.__init__(self, id, name, "mdi:volume-mute", coordinator)

    @property
    def is_on(self) -> bool:
        """Return the current status."""
        return self.coordinator.data.audio_mute

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the capability."""
        self.coordinator.mute_volume(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the capability."""
        self.coordinator.mute_volume(False)

class PjLinkVideoMuteSwitch(PjLinkCapabilityEntity, SwitchEntity):
    """Representation of a PjLink video mute switch."""

    def __init__(
        self,
        id: str,
        name: str,
        coordinator: PjLinkDataUpdateCoordinator
    ) -> None:
        """Initialize the PjLink Select entity."""
        PjLinkCapabilityEntity.__init__(self, id, name, "mdi:video-off", coordinator)

    @property
    def is_on(self) -> bool:
        """Return the current status."""
        return self.coordinator.data.video_mute

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the capability."""
        self.coordinator.mute_video(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the capability."""
        self.coordinator.mute_video(False)