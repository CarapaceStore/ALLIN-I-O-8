"""ALLIN Switch integration."""

from __future__ import annotations

import inspect

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DATA_COORDINATOR, DATA_HOST, DATA_HUB, DOMAIN


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

    # Récupère la liste des relais depuis la carte
    await hub.async_get_relays()

    entities: list[ALLINSwitch] = [
        ALLINSwitch(coordinator, host, hub, relay, entry.entry_id)
        for relay in hub.relays
    ]
    async_add_entities(entities)


class ALLINSwitch(CoordinatorEntity, SwitchEntity):
    """ALLIN Switch Entity."""

    def __init__(self, coordinator, host, hub, relay, config_entry_id):
        super().__init__(coordinator)
        self._host = host
        self._hub = hub
        self._relay = relay
        self._config_entry_id = config_entry_id

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
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity is enabled by default."""
        return True

    @property
    def is_on(self):
        """Return the current state of the relay."""
        relay = self._relay

        # Différentes versions de la lib peuvent exposer des attributs différents
        if hasattr(relay, "is_on"):
            return relay.is_on

        if hasattr(relay, "state"):
            return bool(relay.state)

        if hasattr(relay, "status"):
            return bool(relay.status)

        # Si on ne sait pas, on laisse l'état "unknown" dans HA
        return None

    @property
    def icon(self) -> str:
        """Icon to use in the frontend."""
        return "mdi:dip-switch"

    async def _call_any(self, target, names: tuple[str, ...], *args, **kwargs) -> bool:
        """Appelle la première méthode existante dans names sur target."""
        for name in names:
            method = getattr(target, name, None)
            if not callable(method):
                continue

            result = method(*args, **kwargs)
            if inspect.isawaitable(result):
                await result
            return True

        # Rien trouvé
        raise AttributeError(
            f"No usable method found on {type(target).__name__} for names {names}"
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        # D'abord on essaye sur l'objet Relay
        try:
            await self._call_any(
                self._relay,
                ("turn_on", "on", "async_turn_on", "set_on"),
            )
        except AttributeError:
            # Ensuite on essaye au niveau du hub, en passant l'id du relais
            await self._call_any(
                self._hub,
                (
                    "async_turn_on_relay",
                    "async_relay_on",
                    "turn_on_relay",
                    "relay_on",
                    "set_relay_on",
                ),
                self._relay.id,
            )

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        # D'abord on essaye sur l'objet Relay
        try:
            await self._call_any(
                self._relay,
                ("turn_off", "off", "async_turn_off", "set_off"),
            )
        except AttributeError:
            # Ensuite on essaye au niveau du hub
            await self._call_any(
                self._hub,
                (
                    "async_turn_off_relay",
                    "async_relay_off",
                    "turn_off_relay",
                    "relay_off",
                    "set_relay_off",
                ),
                self._relay.id,
            )

        await self.coordinator.async_request_refresh()
