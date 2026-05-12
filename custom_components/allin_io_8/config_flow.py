"""Config flow pour l'intégration ALLIN I/O 8 (KMTronic)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout
from pykmtronic.auth import Auth
from pykmtronic.hub import KMTronicHubAPI
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client

from .const import (
    CONF_HOSTNAME,
    CONF_PASSWORD,
    CONF_USERNAME,
    DEFAULT_TIMEOUT,
    DOMAIN,
    OPTION_RELAY_PREFIX,
    RELAY_COUNT,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOSTNAME): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def _validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Valider la connexion et l'authentification auprès du module KMTronic.

    Lève :
        CannotConnect — hôte injoignable, timeout, ou erreur réseau
        InvalidAuth   — identifiants HTTP refusés (401)
    """
    session = aiohttp_client.async_get_clientsession(hass)
    auth = Auth(
        session,
        f"http://{data[CONF_HOSTNAME]}",
        data[CONF_USERNAME],
        data[CONF_PASSWORD],
    )
    hub = KMTronicHubAPI(auth)

    try:
        async with async_timeout.timeout(DEFAULT_TIMEOUT):
            # Une mise à jour de l'état des relais oblige l'auth et le réseau
            await hub.async_update_relays()
    except aiohttp.ClientResponseError as err:
        if err.status == 401:
            raise InvalidAuth from err
        raise CannotConnect from err
    except (
        aiohttp.ClientConnectorError,
        aiohttp.ClientError,
        asyncio.TimeoutError,
    ) as err:
        raise CannotConnect from err


class AllinIO8ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestion du flux de configuration pour ALLIN I/O 8."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> AllinIO8OptionsFlow:
        """Retourner le flux d'options pour cette entrée."""
        return AllinIO8OptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Première étape de config (écran principal)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Identifiant unique = hôte (un seul config entry par module)
            await self.async_set_unique_id(user_input[CONF_HOSTNAME])
            self._abort_if_unique_id_configured()

            try:
                await _validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # noqa: BLE001 — capture défensive HA
                _LOGGER.exception("Erreur inattendue lors de la validation")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_HOSTNAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class AllinIO8OptionsFlow(config_entries.OptionsFlow):
    """Flux d'options pour personnaliser les noms des relais."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialiser le flux d'options."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Permettre la personnalisation du nom de chaque relais."""
        if user_input is not None:
            # Nettoyer les chaînes vides → fallback au nom par défaut
            cleaned = {
                key: value.strip()
                for key, value in user_input.items()
                if isinstance(value, str) and value.strip()
            }
            return self.async_create_entry(title="", data=cleaned)

        current = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Optional(
                    f"{OPTION_RELAY_PREFIX}{i}",
                    default=current.get(
                        f"{OPTION_RELAY_PREFIX}{i}", f"Relay {i}"
                    ),
                ): str
                for i in range(1, RELAY_COUNT + 1)
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)


class CannotConnect(HomeAssistantError):
    """Levée quand le module ALLIN I/O 8 est injoignable."""


class InvalidAuth(HomeAssistantError):
    """Levée quand les identifiants sont refusés par le module."""
