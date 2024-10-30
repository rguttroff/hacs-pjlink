"""The PjLink integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import (
    DeviceInfo
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PjLinkDataUpdateCoordinator


class PjLinkEntity(CoordinatorEntity[PjLinkDataUpdateCoordinator]):
    """Defines a base PjLink entity."""

    def __init__(
        self,
        *,
        name: str,
        icon: str,
        coordinator: PjLinkDataUpdateCoordinator,
        enabled_default: bool = True,
    ) -> None:
        """Initialize the PjLink entity."""
        super().__init__(coordinator)
        self._attr_entity_registry_enabled_default = enabled_default
        self._attr_icon = icon
        self._attr_name = name


class PjLinkDeviceEntity(PjLinkEntity):
    """Defines a PjLink device entity."""

    @property
    def device_id(self):
        return self.coordinator.data.device_id

    @property
    def device_name(self):
        """Return the name of the current device."""
        return self.coordinator.data.name

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this PjLink device."""

        device_info = DeviceInfo(
            name=self.device_name,
            identifiers={
                (
                    DOMAIN,
                    self.device_id,
                )
            },
            manufacturer=self.coordinator.data.manufacturer,
            model=self.coordinator.data.product_name
        )

        return device_info

class PjLinkCapabilityEntity(PjLinkDeviceEntity):
    """Base Entity type for all capabilities."""

    def __init__(
        self,
        id: str,
        name: str,
        icon: str,
        coordinator: PjLinkDataUpdateCoordinator
    ) -> None:
        """Initialize a capability based entity."""
        self.capability_id = id
        super().__init__(name=name, icon=icon, coordinator=coordinator)

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return f"{self.device_id}_{self.capability_id}"
