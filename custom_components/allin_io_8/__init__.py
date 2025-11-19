"""Integration ALLIN I/O 8.

Basée sur l'intégration kmtronic de Home Assistant.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant

DOMAIN = "allin_io_8"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up l'intégration ALLIN I/O 8 (configuration.yaml)."""
    # Pour l'instant, ne fait rien de spécial.
    return True
