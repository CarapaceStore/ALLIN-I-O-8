"""ALLIN I/O 8 — intégration Home Assistant."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

import aiohttp
import async_timeout
from pykmtronic.auth import Auth
from pykmtronic.hub import KMTronicHubAPI
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client, device_registry as dr
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    ATTR_DURATION,
    CONF_HOSTNAME,
    CONF_PASSWORD,
    CONF_USERNAME,
    DATA_COORDINATOR,
    DATA_HOST,
    DATA_HUB,
    DEFAULT_PULSE_DURATION,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    SERVICE_PULSE,
)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["switch"]

SERVICE_PULSE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): str,
        vol.Optional(ATTR_DURATION, default=DEFAULT_PULSE_DURATION): vol.All(
            vol.Coerce(float), vol.Range(min=0.1, max=60.0)
        ),
    }
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Configurer le composant ALLIN I/O 8 (sans entry)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configurer une instance ALLIN I/O 8 à partir d'une entrée."""
    session = aiohttp_client.async_get_clientsession(hass)
    auth = Auth(
        session,
        f"http://{entry.data[CONF_HOSTNAME]}",
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )
    hub = KMTronicHubAPI(auth)

    async def async_update_data() -> None:
        """Rafraîchir l'état de tous les relais depuis le module."""
        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                await hub.async_update_relays()
        except aiohttp.ClientResponseError as err:
            raise UpdateFailed(f"Identifiants incorrects: {err}") from err
        except (
            aiohttp.ClientConnectorError,
            aiohttp.ClientError,
            asyncio.TimeoutError,
        ) as err:
            raise UpdateFailed(f"Erreur de communication: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{MANUFACTURER} {MODEL} {entry.data[CONF_HOSTNAME]}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_HUB: hub,
        DATA_HOST: entry.data[CONF_HOSTNAME],
        DATA_COORDINATOR: coordinator,
    }

    # Inscription dans le registre des appareils
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.data[CONF_HOSTNAME])},
        manufacturer=MANUFACTURER,
        model=MODEL,
        name=f"ALLIN I/O 8 ({entry.data[CONF_HOSTNAME]})",
    )

    # Chargement des plateformes
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listener: recharger l'intégration si les options changent
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    # Enregistrement du service pulse (une seule fois, indépendamment des entries)
    if not hass.services.has_service(DOMAIN, SERVICE_PULSE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_PULSE,
            _make_pulse_handler(hass),
            schema=SERVICE_PULSE_SCHEMA,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Décharger une entrée de configuration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    # Si plus aucune entrée, retirer le service global
    if not hass.data.get(DOMAIN) and hass.services.has_service(DOMAIN, SERVICE_PULSE):
        hass.services.async_remove(DOMAIN, SERVICE_PULSE)

    return unload_ok


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Recharger l'intégration quand les options changent (noms relais)."""
    await hass.config_entries.async_reload(entry.entry_id)


def _make_pulse_handler(hass: HomeAssistant):
    """Construire le handler du service pulse."""

    async def handle_pulse(call: ServiceCall) -> None:
        """Activer un relais pendant `duration` secondes puis le couper.

        Service-level: on s'appuie sur switch.turn_on / switch.turn_off
        plutôt que de manipuler les entités directement, ce qui maintient
        l'intégration découplée du nom interne du relais.
        """
        entity_id = call.data[ATTR_ENTITY_ID]
        duration: float = call.data[ATTR_DURATION]

        if not entity_id.startswith("switch."):
            _LOGGER.error("Pulse: entity_id doit être un switch (reçu %s)", entity_id)
            return

        _LOGGER.debug("Pulse sur %s pendant %.1fs", entity_id, duration)

        await hass.services.async_call(
            "switch", "turn_on", {ATTR_ENTITY_ID: entity_id}, blocking=True
        )
        await asyncio.sleep(duration)
        await hass.services.async_call(
            "switch", "turn_off", {ATTR_ENTITY_ID: entity_id}, blocking=True
        )

    return handle_pulse
