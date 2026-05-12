"""Tests du module __init__ : setup/unload/service pulse."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from custom_components.allin_io_8.const import (
    ATTR_DURATION,
    DATA_COORDINATOR,
    DATA_HOST,
    DATA_HUB,
    DOMAIN,
    SERVICE_PULSE,
)


# ─── async_setup_entry ──────────────────────────────────────────────


async def test_async_setup_entry_happy_path(
    hass: HomeAssistant, mock_kmtronic, mock_config_entry
) -> None:
    """Le setup d'une entrée doit charger la plateforme switch et enregistrer le service."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Entrée bien chargée
    assert mock_config_entry.state == ConfigEntryState.LOADED

    # hass.data peuplé
    data = hass.data[DOMAIN][mock_config_entry.entry_id]
    assert DATA_HUB in data
    assert DATA_HOST in data
    assert DATA_COORDINATOR in data

    # Service pulse enregistré globalement
    assert hass.services.has_service(DOMAIN, SERVICE_PULSE)

    # Au moins une entité switch créée
    states = hass.states.async_entity_ids("switch")
    assert len(states) > 0


async def test_async_unload_entry_removes_service(
    hass: HomeAssistant, mock_kmtronic, mock_config_entry
) -> None:
    """Décharger la dernière entrée doit retirer le service pulse."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert hass.services.has_service(DOMAIN, SERVICE_PULSE)

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state == ConfigEntryState.NOT_LOADED
    # Plus aucune entrée → service retiré
    assert not hass.services.has_service(DOMAIN, SERVICE_PULSE)


# ─── Service pulse ──────────────────────────────────────────────────


async def test_pulse_service_turn_on_then_off(
    hass: HomeAssistant, mock_kmtronic, mock_config_entry
) -> None:
    """Le service pulse doit appeler switch.turn_on, attendre, puis switch.turn_off."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Récupérer une entité switch réellement créée pour avoir un entity_id valide
    switch_entities = hass.states.async_entity_ids("switch")
    assert switch_entities, "Aucun switch créé par le setup"
    target_entity = switch_entities[0]

    # On patche asyncio.sleep pour ne pas attendre + on espionne switch.turn_on/off
    with patch(
        "custom_components.allin_io_8.asyncio.sleep", new=AsyncMock()
    ) as sleep_mock:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_PULSE,
            {ATTR_ENTITY_ID: target_entity, ATTR_DURATION: 2.5},
            blocking=True,
        )

    # Le relais mocké correspondant doit avoir été energise() puis de_energise()
    hub = mock_kmtronic["hub"]
    # Au moins un relais a vu energise + de_energise (le pulse a fait turn_on + turn_off)
    relay_called = [
        r for r in hub.relays
        if r.energise.await_count >= 1 and r.de_energise.await_count >= 1
    ]
    assert relay_called, "Aucun relais n'a vu energise+de_energise"

    # sleep appelé avec la durée demandée
    sleep_mock.assert_awaited_once_with(2.5)


async def test_pulse_service_rejects_non_switch_entity(
    hass: HomeAssistant, mock_kmtronic, mock_config_entry
) -> None:
    """Le service pulse doit ignorer une entité non-switch (early return)."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    hub = mock_kmtronic["hub"]
    # Compteurs avant appel
    before_energise = sum(r.energise.await_count for r in hub.relays)
    before_de_energise = sum(r.de_energise.await_count for r in hub.relays)

    with patch(
        "custom_components.allin_io_8.asyncio.sleep", new=AsyncMock()
    ) as sleep_mock:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_PULSE,
            {ATTR_ENTITY_ID: "light.kitchen", ATTR_DURATION: 1.0},
            blocking=True,
        )

    # Aucun relais n'a bougé, et sleep n'a pas été appelé
    after_energise = sum(r.energise.await_count for r in hub.relays)
    after_de_energise = sum(r.de_energise.await_count for r in hub.relays)
    assert after_energise == before_energise
    assert after_de_energise == before_de_energise
    sleep_mock.assert_not_awaited()
