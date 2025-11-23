"""ALLIN I/O 8 integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

import aiohttp
from pykmtronic.auth import Auth
from pykmtronic.hub import KMTronicHubAPI

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client, device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_HOSTNAME,
    CONF_PASSWORD,
    CONF_USERNAME,
    DATA_COORDINATOR,
    DATA_HUB,
    DATA_HOST,
    DOMAIN,
    MANUFACTURER,
)

PLATFORMS: list[Platform] = [Platform.SWITCH]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the ALLIN I/O 8 integration (legacy YAML not supported)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ALLIN I/O 8 from a config entry."""

    session = aiohttp_client.async_get_clientsession(hass)
    auth = Auth(
        session,
        f"http://{entry.data[CONF_HOSTNAME]}",
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )
    hub = KMTronicHubAPI(auth)

    async def async_update_data() -> None:
        """Fetch latest state from ALLIN I/O 8 hub."""
        try:
            async with asyncio.timeout(10):
                await hub.async_update_relays()
        except aiohttp.client_exceptions.ClientResponseError as err:
            # Typically wrong credentials
            raise UpdateFailed(f"Wrong credentials: {err}") from err
        except (
            asyncio.TimeoutError,
            aiohttp.client_exceptions.ClientConnectorError,
        ) as err:
            # Network / timeout / connection issues
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{MANUFACTURER} {getattr(hub, 'name', 'ALLIN I/O 8')}",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    # First refresh to validate connectivity
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_HUB: hub,
        DATA_HOST: entry.data[CONF_HOSTNAME],
        DATA_COORDINATOR: coordinator,
    }

    # Register the hub as a device for nicer device/entity grouping
    device_registry = dr.async_get(hass)
    host = entry.data[CONF_HOSTNAME]
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, host)},
        manufacturer=MANUFACTURER,
        name=f"ALLIN I/O 8 ({host})",
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok and DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
