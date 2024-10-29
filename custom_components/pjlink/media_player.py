"""Support for controlling projector via the PJLink protocol."""

from __future__ import annotations

import contextlib
import logging
from typing import Any

from homeassistant.components import media_source
from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import uuid

from .const import DOMAIN
from .coordinator import PjLinkDataUpdateCoordinator
from .entity import PjLinkDeviceEntity

_LOGGER = logging.getLogger(__name__)

MUSIC_PLAYER_BASE_SUPPORT = (
    MediaPlayerEntityFeature.SELECT_SOURCE
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PjLink sensor based on a config entry."""
    coordinator: PjLinkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    name = coordinator.data.network_name

    media_players: list[Entity] = []

    media_players.append(
        PjLinkMediaPlayer(name, entry.entry_id, coordinator)
    )

    async_add_entities(media_players)


class PjLinkMediaPlayer(PjLinkDeviceEntity, MediaPlayerEntity):
    """The pjlink media player."""

    _attr_media_content_type = MediaType.VIDEO
    _attr_should_poll = False

    def __init__(self, name, entry_id, coordinator):
        """Initialize the pjlink device."""
        self._player_state = MediaPlayerState.ON
        self._volume_muted = False

        super().__init__(
            name=name,
            icon="mdi:projector",
            coordinator=coordinator,
        )

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the player."""
        if self.coordinator.data.power == True:
            return MediaPlayerState.ON
        return MediaPlayerState.OFF

    @property
    def source_mapping(self):
        """Return a mapping of the actual source names to their labels configured in the PjLink App."""
        ret = {}
        for inp in self.coordinator.data.input_list:
            ret[inp] = inp
        return ret

    @property
    def reverse_source_mapping(self):
        """Return a mapping from the source label to the source name."""
        return {v: k for k, v in self.source_mapping.items()}

    @property
    def is_volume_muted(self):
        """Return boolean if volume is currently muted."""
        return self.coordinator.data.audio_mute

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this media_player."""
        return self.coordinator.data.device_id

    async def async_turn_on(self) -> None:
        """Turn the media player on."""
        self.coordinator.turn_on()
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Turn the media player off."""
        self.coordinator.turn_off()
        self.async_write_ha_state()

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute the volume."""
        self.coordinator.mute_volume(mute)
        self.async_write_ha_state()

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Flag media player features that are supported."""
        supported_features = MUSIC_PLAYER_BASE_SUPPORT

        supported_features |= (
            MediaPlayerEntityFeature.TURN_ON | MediaPlayerEntityFeature.TURN_OFF
        )

        supported_features |= MediaPlayerEntityFeature.VOLUME_MUTE

        return supported_features

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        self.coordinator.select_source(source)

    @property
    def source_id(self):
        """ID of the current input source."""
        return self.coordinator.data.input

    @property
    def source(self):
        """Name of the current input source."""
        return self.source_mapping.get(self.source_id)

    @property
    def source_list(self):
        """List of available input sources."""
        return list(self.source_mapping.values())
