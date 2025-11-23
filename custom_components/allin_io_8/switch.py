"""ALLIN I/O 8 Switch integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DATA_HOST, DATA_HUB, DOMAIN, MANUFACTURER


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    hub = data[DATA_HUB]
    coordinator = data[DATA_COORDINATOR]
    host = data[DATA_HOST]

    entities: list[AllinSwitch] = [
        AllinSwitch(coordinator, host, relay, idx)
        for idx, relay in enumerate(getattr(hub, "relays", []), start=1)
    ]

    async_add_entities(entities)


class AllinSwitch(CoordinatorEntity, SwitchEntity):

    _attr_has_entity_name = True

    def __init__(self, coordinator, host: str, relay: Any, index: int) -> None:
        super().__init__(coordinator)
        self._host = host
        self._relay = relay
        self._index = index

        relay_id = getattr(relay, "id", index)
        self._attr_unique_id = f"{host}_relay_{relay_id}"
        self._attr_name = f"Relay {relay_id}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, host)},
            "manufacturer": MANUFACTURER,
            "name": f"ALLIN I/O 8 ({host})",
        }

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def is_on(self) -> bool:

        state = getattr(self._relay, "state", None)
        if isinstance(state, bool):
            return state

        if isinstance(state, (int, float)):
            return bool(state)

        is_on_attr = getattr(self._relay, "is_on", None)
        if isinstance(is_on_attr, bool):
            return is_on_attr

        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._relay.energise()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._relay.de_energise()
        await self.coordinator.async_request_refresh()
