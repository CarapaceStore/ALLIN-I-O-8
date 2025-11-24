"""ALLIN Switch integration."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DATA_COORDINATOR, DATA_HOST, DATA_HUB, DOMAIN, MANUFACTURER


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up ALLIN switch entities from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data[DATA_COORDINATOR]
    hub = data[DATA_HUB]
    host = data[DATA_HOST]

    # Charge la liste des relais depuis la carte
    await hub.async_get_relays()

    entities: list[ALLINSwitch] = [
        ALLINSwitch(coordinator, host, relay, entry.entry_id)
        for relay in hub.relays
    ]
    async_add_entities(entities)


class ALLINSwitch(CoordinatorEntity, SwitchEntity):
    """ALLIN Switch Entity."""

    def __init__(self, coordinator, host, relay, config_entry_id) -> None:
        super().__init__(coordinator)
        self._host = host
        self._relay = relay
        self._config_entry_id = config_entry_id

    # ---- Propriétés de base ----

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        return self.coordinator.last_update_success

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return f"Relay{self._relay.id}"

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the entity."""
        return f"{self._config_entry_id}_relay{self._relay.id}"

    @property
    def device_info(self) -> dict:
        """Return device info for linking entities to the device."""
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": f"ALLIN I/O 8 ({self._host})",
            "manufacturer": MANUFACTURER,
        }

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity is enabled by default."""
        return True

    @property
    def icon(self) -> str:
        """Icon to use in the frontend."""
        return "mdi:dip-switch"

    # ---- État ----

    @property
    def is_on(self):
        """Return the current state of the relay."""
        relay = self._relay

        # API pykmtronic : is_energised = True => ON
        if hasattr(relay, "is_energised"):
            return relay.is_energised

        # fallback éventuel si la lib évolue
        if hasattr(relay, "is_on"):
            return relay.is_on

        return None

    # ---- Commandes ON / OFF ----

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        # API pykmtronic : energise()
        await self._relay.energise()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        # API pykmtronic : de_energise()
        await self._relay.de_energise()
        await self.coordinator.async_request_refresh()
