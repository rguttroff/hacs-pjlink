"""The PjLink integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING

from pypjlink import Projector
from pypjlink.projector import ProjectorError, POWER_STATES, MUTE_AUDIO, POWER_STATES_REV

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, ERR_PROJECTOR_UNAVAILABLE

if TYPE_CHECKING:
    from .entity import PjLinkDeviceEntity

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

def format_input_source(input_source_name, input_source_number):
    """Format input source for display in UI."""
    return f"{input_source_name} {input_source_number}"

class PjLinkData:
    """Object that holds data for a MusicCast device."""

    def __init__(self):
        """Ctor."""
        # device info
        self.device_id = None
        self.name = None
        self.manufacturer = None
        self.product_name = None

        # network status
        self.network_name = None

        self.power: bool | None = None
        self.power_state = None

        self.input = None
        self.inputs: Dict[str, str] = {}
        self.lamps: Dict[int, bool] = {}
        self.errors: Dict[str, str] = {}
        
        self.video_mute: bool | None = None
        self.audio_mute: bool | None = None

class PjLinkDataUpdateCoordinator(DataUpdateCoordinator[PjLinkData]):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, host: str, port: int, name: str, encoding: str, password: str) -> None:
        """Initialize."""
        self._name = name
        self._host = host
        self._port = port
        self._password = password
        self._encoding = encoding

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.entities: list[PjLinkDeviceEntity] = []

    async def _async_update_data(self) -> PjLinkData:
        """Update data via library."""
        try:

            with self.projector() as projector:

                data = PjLinkData()

                data.device_id = self._host
                data.host = self._host
                data.name = self._name
                data.manufacturer = projector.get_manufacturer()
                data.product_name = projector.get_product_name()

                data.power_state = projector.get_power()

                if(data.power_state in (POWER_STATES_REV['1'], POWER_STATES_REV['2'], POWER_STATES_REV['3'])):
                    data.power = True
                else:
                    data.power = False

                data.input = format_input_source(*projector.get_input())
                try:
                    data.input_list = projector.get_inputs()
                except Exception as exception:
                    data.input_list = []
                    _LOGGER.warning(
                        "Fehler beim Abrufen der Inputs"
                        "%s",
                        exception
                    )

                try:
                    data.lamp_list = projector.get_lamps()
                except Exception as exception:
                    data.lamp_list = []
                    _LOGGER.warning(
                        "Fehler beim Abrufen der Lamps"
                        "%s",
                        exception
                    )

                try:
                    data.errors = projector.get_errors()
                except Exception as exception:
                    data.error = []
                    _LOGGER.warning(
                        "Fehler beim Abrufen der Errors"
                        "%s",
                        exception
                    )

                try:
                    data.video_mute = projector.get_mute()[0]
                    data.audio_mute = projector.get_mute()[1]
                except Exception as exception:
                    data.video_mute = False
                    data.audio_mute = False
                    _LOGGER.warning(
                        "Fehler beim Abrufen der Errors"
                        "%s",
                        exception
                    )

        except ProjectorError as exception:
            raise UpdateFailed from exception
        return data

    def projector(self):
        """Create PJLink Projector instance."""

        try:
            projector = Projector.from_address(self._host, self._port)
            projector.authenticate(None if self._password == "" else self._password)
        except (TimeoutError, OSError) as err:
            self._attr_available = False
            raise ProjectorError(ERR_PROJECTOR_UNAVAILABLE) from err

        return projector

    def turn_off(self) -> None:
        """Turn projector off."""
        with self.projector() as projector:
            projector.set_power("off")

    def turn_on(self) -> None:
        """Turn projector on."""
        with self.projector() as projector:
            projector.set_power("on")

    def mute_volume(self, mute: bool) -> None:
        """Mute (true) of unmute (false) media player."""
        with self.projector() as projector:
            projector.set_mute(MUTE_AUDIO, mute)

    def select_source(self, source: str) -> None:
        """Set the input source."""
        source_name_mapping = {format_input_source(*x): x for x in self.data.inputs}
        source = source_name_mapping[source]
        with self.projector() as projector:
            projector.set_input(*source)