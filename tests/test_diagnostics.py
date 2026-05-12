"""Tests du module diagnostics."""

from __future__ import annotations

from homeassistant.components.diagnostics import REDACTED
from homeassistant.core import HomeAssistant

from custom_components.allin_io_8.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
)
from custom_components.allin_io_8.diagnostics import (
    async_get_config_entry_diagnostics,
)


async def test_diagnostics_structure(
    hass: HomeAssistant, mock_kmtronic, mock_config_entry
) -> None:
    """Le dump diagnostique doit contenir config_entry / host / coordinator / hub."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    # Présence des clés principales
    assert "config_entry" in result
    assert "host" in result
    assert "coordinator" in result
    assert "hub" in result

    # Coordinator
    assert "last_update_success" in result["coordinator"]
    assert "update_interval" in result["coordinator"]

    # Hub : nom + relais
    assert result["hub"]["name"] == "KMTronic Hub"
    assert result["hub"]["relays_count"] == 8
    assert len(result["hub"]["relays"]) == 8
    for relay_dump in result["hub"]["relays"]:
        assert "id" in relay_dump
        assert "is_energised" in relay_dump


async def test_diagnostics_redacts_credentials(
    hass: HomeAssistant, mock_kmtronic, mock_config_entry
) -> None:
    """Username et password doivent être REDACTED dans le dump."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    entry_data = result["config_entry"]["data"]
    assert entry_data[CONF_USERNAME] == REDACTED
    assert entry_data[CONF_PASSWORD] == REDACTED
    # Le host n'est PAS redacted (utile au debug)
    assert entry_data.get("host") != REDACTED
