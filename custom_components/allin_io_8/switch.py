"""Plateforme switch pour l'intégration ALLIN I/O 8."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DATA_COORDINATOR,
    DATA_HOST,
    DATA_HUB,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    OPTION_RELAY_PREFIX,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Créer les entités switch pour chaque relais du module."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data[DATA_COORDINATOR]
    hub = data[DATA_HUB]
    host = data[DATA_HOST]

    # Découverte des relais via l'API KMTronic
    await hub.async_get_relays()

    entities: list[ALLINSwitch] = [
        ALLINSwitch(coordinator, host, relay, entry)
        for relay in hub.relays
    ]
    async_add_entities(entities)


class ALLINSwitch(CoordinatorEntity, SwitchEntity):
    """Entité Switch ALLIN — un relais individuel."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:dip-switch"

    def __init__(self, coordinator, host: str, relay, entry: ConfigEntry) -> None:
        """Initialiser l'entité switch."""
        super().__init__(coordinator)
        self._host = host
        self._relay = relay
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_relay{relay.id}"

    # ─── Identité ──────────────────────────────────────────────

    @property
    def name(self) -> str:
        """Nom personnalisé via options, sinon 'Relay N' par défaut."""
        custom = self._entry.options.get(f"{OPTION_RELAY_PREFIX}{self._relay.id}")
        return custom or f"Relay {self._relay.id}"

    @property
    def device_info(self) -> DeviceInfo:
        """Informations appareil pour regrouper les 8 relais sous un device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._host)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=f"ALLIN I/O 8 ({self._host})",
            configuration_url=f"http://{self._host}",
        )

    # ─── Disponibilité & état ──────────────────────────────────

    @property
    def available(self) -> bool:
        """Disponibilité = dernière mise à jour réussie du coordinator."""
        return self.coordinator.last_update_success

    @property
    def is_on(self) -> bool | None:
        """Retourner l'état du relais (True = activé)."""
        relay = self._relay
        if hasattr(relay, "is_energised"):
            return relay.is_energised
        if hasattr(relay, "is_on"):
            return relay.is_on
        return None

    # ─── Commandes ─────────────────────────────────────────────

    async def async_turn_on(self, **kwargs) -> None:
        """Activer le relais."""
        await self._relay.energise()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Désactiver le relais."""
        await self._relay.de_energise()
        await self.coordinator.async_request_refresh()
