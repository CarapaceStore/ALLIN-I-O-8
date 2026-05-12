"""Support du téléchargement de diagnostics pour ALLIN I/O 8."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    DATA_COORDINATOR,
    DATA_HOST,
    DATA_HUB,
    DOMAIN,
)

TO_REDACT = {CONF_USERNAME, CONF_PASSWORD}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Retourner un export diagnostique pour cette entrée de configuration."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data[DATA_COORDINATOR]
    hub = data[DATA_HUB]
    host = data[DATA_HOST]

    relays_dump: list[dict[str, Any]] = []
    for relay in getattr(hub, "relays", None) or []:
        relays_dump.append(
            {
                "id": getattr(relay, "id", None),
                "is_energised": getattr(relay, "is_energised", None),
            }
        )

    return {
        "config_entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "host": host,
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
        },
        "hub": {
            "name": getattr(hub, "name", None),
            "relays_count": len(relays_dump),
            "relays": relays_dump,
        },
    }
