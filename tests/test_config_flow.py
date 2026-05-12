"""Tests du config flow et options flow ALLIN I/O 8."""

from __future__ import annotations

from unittest.mock import patch

import aiohttp
from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant

from custom_components.allin_io_8.config_flow import CannotConnect, InvalidAuth
from custom_components.allin_io_8.const import (
    CONF_HOSTNAME,
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
    OPTION_RELAY_PREFIX,
    RELAY_COUNT,
)

from .conftest import make_client_response_error


# ─── Step user — happy path ────────────────────────────────────────


async def test_user_flow_success(
    hass: HomeAssistant, mock_kmtronic, user_input
) -> None:
    """Un flux user complet doit créer une entrée."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] in (None, {})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input
    )
    await hass.async_block_till_done()

    assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result2["title"] == user_input[CONF_HOSTNAME]
    assert result2["data"] == user_input


# ─── Step user — erreurs ────────────────────────────────────────────


async def test_user_flow_cannot_connect(
    hass: HomeAssistant, user_input
) -> None:
    """CannotConnect → erreur 'cannot_connect' affichée."""
    with patch(
        "custom_components.allin_io_8.config_flow._validate_input",
        side_effect=CannotConnect,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input
        )

    assert result2["type"] == data_entry_flow.FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_user_flow_invalid_auth(
    hass: HomeAssistant, user_input
) -> None:
    """InvalidAuth → erreur 'invalid_auth' affichée."""
    with patch(
        "custom_components.allin_io_8.config_flow._validate_input",
        side_effect=InvalidAuth,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input
        )

    assert result2["type"] == data_entry_flow.FlowResultType.FORM
    assert result2["errors"] == {"base": "invalid_auth"}


async def test_user_flow_unknown_error(
    hass: HomeAssistant, user_input
) -> None:
    """Exception inattendue → erreur 'unknown'."""
    with patch(
        "custom_components.allin_io_8.config_flow._validate_input",
        side_effect=RuntimeError("boom"),
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input
        )

    assert result2["type"] == data_entry_flow.FlowResultType.FORM
    assert result2["errors"] == {"base": "unknown"}


# ─── Step user — doublon ────────────────────────────────────────────


async def test_user_flow_duplicate_host_aborts(
    hass: HomeAssistant, mock_kmtronic, mock_config_entry, user_input
) -> None:
    """Même hôte deux fois → abort 'already_configured'."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input
    )

    assert result2["type"] == data_entry_flow.FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


# ─── _validate_input direct (couverture de la conversion d'erreurs) ─


async def test_validate_input_raises_invalid_auth_on_401(
    hass: HomeAssistant, user_input
) -> None:
    """Une 401 doit lever InvalidAuth (pas CannotConnect)."""
    from custom_components.allin_io_8.config_flow import _validate_input

    err = make_client_response_error(status=401)

    with patch(
        "custom_components.allin_io_8.config_flow.KMTronicHubAPI"
    ) as hub_cls:
        hub = hub_cls.return_value
        hub.async_update_relays.side_effect = err

        try:
            await _validate_input(hass, user_input)
        except InvalidAuth:
            pass
        else:
            raise AssertionError("InvalidAuth attendue")


async def test_validate_input_raises_cannot_connect_on_network(
    hass: HomeAssistant, user_input
) -> None:
    """Une erreur réseau doit lever CannotConnect."""
    from custom_components.allin_io_8.config_flow import _validate_input

    with patch(
        "custom_components.allin_io_8.config_flow.KMTronicHubAPI"
    ) as hub_cls:
        hub = hub_cls.return_value
        hub.async_update_relays.side_effect = aiohttp.ClientError("boom")

        try:
            await _validate_input(hass, user_input)
        except CannotConnect:
            pass
        else:
            raise AssertionError("CannotConnect attendue")


# ─── OptionsFlow ────────────────────────────────────────────────────


async def test_options_flow_shows_form_with_defaults(
    hass: HomeAssistant, mock_kmtronic, mock_config_entry
) -> None:
    """Step init de l'OptionsFlow doit afficher un formulaire."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "init"


async def test_options_flow_submission_keeps_custom_names(
    hass: HomeAssistant, mock_kmtronic, mock_config_entry
) -> None:
    """Soumission OptionsFlow → noms custom conservés, chaînes vides exclues."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id
    )

    # Soumission : 2 noms custom, 1 vide, le reste par défaut → form va
    # remplir tout avec des valeurs (vides incluses). On vérifie le filtrage.
    submission = {
        f"{OPTION_RELAY_PREFIX}{i}": ""
        for i in range(1, RELAY_COUNT + 1)
    }
    submission[f"{OPTION_RELAY_PREFIX}1"] = "Salon"
    submission[f"{OPTION_RELAY_PREFIX}2"] = "Cuisine"
    submission[f"{OPTION_RELAY_PREFIX}3"] = "   "  # whitespace → exclu

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"], submission
    )
    await hass.async_block_till_done()

    assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result2["data"] == {
        f"{OPTION_RELAY_PREFIX}1": "Salon",
        f"{OPTION_RELAY_PREFIX}2": "Cuisine",
    }
