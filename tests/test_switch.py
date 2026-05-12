"""Tests de la plateforme switch (ALLINSwitch)."""

from __future__ import annotations

from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant

from custom_components.allin_io_8.const import (
    DOMAIN,
    OPTION_RELAY_PREFIX,
)
from custom_components.allin_io_8.switch import ALLINSwitch


def _make_entity(
    relay,
    *,
    coordinator=None,
    host: str = "192.168.1.42",
    options: dict | None = None,
    entry_id: str = "abc123",
):
    """Construire une ALLINSwitch isolée (sans HA tournant)."""
    coord = coordinator or MagicMock()
    coord.last_update_success = True
    # CoordinatorEntity nécessite quelques attributs lors de __init__
    coord.async_add_listener = MagicMock(return_value=lambda: None)

    entry = MagicMock()
    entry.entry_id = entry_id
    entry.options = options or {}

    return ALLINSwitch(coord, host, relay, entry)


# ─── Naming ─────────────────────────────────────────────────────────


def test_name_default(mock_relay):
    """Sans option custom, name = 'Relay N'."""
    entity = _make_entity(mock_relay)
    assert entity.name == "Relay 1"


def test_name_custom_from_options(mock_relay):
    """Avec une option custom, name = nom personnalisé."""
    entity = _make_entity(
        mock_relay, options={f"{OPTION_RELAY_PREFIX}1": "Salon"}
    )
    assert entity.name == "Salon"


def test_name_falls_back_when_option_empty(mock_relay):
    """Une option vide → fallback sur le défaut."""
    entity = _make_entity(
        mock_relay, options={f"{OPTION_RELAY_PREFIX}1": ""}
    )
    assert entity.name == "Relay 1"


# ─── unique_id ──────────────────────────────────────────────────────


def test_unique_id_combines_entry_and_relay(mock_relay):
    """unique_id = '<entry_id>_relay<N>'."""
    entity = _make_entity(mock_relay, entry_id="abc123")
    assert entity.unique_id == "abc123_relay1"


# ─── device_info ────────────────────────────────────────────────────


def test_device_info_groups_under_host(mock_relay):
    """device_info regroupe tous les relais sous (DOMAIN, host)."""
    entity = _make_entity(mock_relay, host="192.168.1.42")
    info = entity.device_info
    assert (DOMAIN, "192.168.1.42") in info["identifiers"]
    assert info["configuration_url"] == "http://192.168.1.42"


# ─── is_on ──────────────────────────────────────────────────────────


def test_is_on_reads_is_energised_true(mock_relay):
    """is_on reflète relay.is_energised quand True."""
    mock_relay.is_energised = True
    entity = _make_entity(mock_relay)
    assert entity.is_on is True


def test_is_on_reads_is_energised_false(mock_relay):
    """is_on reflète relay.is_energised quand False."""
    mock_relay.is_energised = False
    entity = _make_entity(mock_relay)
    assert entity.is_on is False


# ─── available ──────────────────────────────────────────────────────


def test_available_true_when_coordinator_ok(mock_relay):
    """available = True quand coordinator.last_update_success = True."""
    coord = MagicMock()
    coord.last_update_success = True
    coord.async_add_listener = MagicMock(return_value=lambda: None)
    entity = _make_entity(mock_relay, coordinator=coord)
    assert entity.available is True


def test_available_false_when_coordinator_failed(mock_relay):
    """available = False quand coordinator.last_update_success = False."""
    coord = MagicMock()
    coord.last_update_success = False
    coord.async_add_listener = MagicMock(return_value=lambda: None)
    entity = _make_entity(mock_relay, coordinator=coord)
    assert entity.available is False


# ─── Commandes ──────────────────────────────────────────────────────


async def test_async_turn_on_calls_energise_and_refresh(mock_relay):
    """async_turn_on doit appeler relay.energise() puis coordinator.async_request_refresh()."""
    coord = MagicMock()
    coord.last_update_success = True
    coord.async_add_listener = MagicMock(return_value=lambda: None)
    coord.async_request_refresh = MagicMock()

    async def _refresh():
        return None

    coord.async_request_refresh.side_effect = _refresh

    entity = _make_entity(mock_relay, coordinator=coord)
    await entity.async_turn_on()

    mock_relay.energise.assert_awaited_once()
    assert coord.async_request_refresh.called


async def test_async_turn_off_calls_de_energise_and_refresh(mock_relay):
    """async_turn_off doit appeler relay.de_energise() puis coordinator.async_request_refresh()."""
    coord = MagicMock()
    coord.last_update_success = True
    coord.async_add_listener = MagicMock(return_value=lambda: None)
    coord.async_request_refresh = MagicMock()

    async def _refresh():
        return None

    coord.async_request_refresh.side_effect = _refresh

    entity = _make_entity(mock_relay, coordinator=coord)
    await entity.async_turn_off()

    mock_relay.de_energise.assert_awaited_once()
    assert coord.async_request_refresh.called


# ─── Integration via HA ─────────────────────────────────────────────


async def test_switch_entities_created_per_relay(
    hass: HomeAssistant, mock_kmtronic, mock_config_entry
) -> None:
    """Setup complet → 8 entités switch créées (une par relais)."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    switch_ids = hass.states.async_entity_ids("switch")
    assert len(switch_ids) == 8
