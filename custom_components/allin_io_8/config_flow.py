"""Config flow pour l'intégration ALLIN I/O 8."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD
import voluptuous as vol
import aiohttp

from pykmtronic.auth import Auth
from pykmtronic.hub import KMTronicHubAPI

from .const import DOMAIN, CONF_HOSTNAME, CONF_USERNAME as ALLIN_CONF_USERNAME, CONF_PASSWORD as ALLIN_CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """Erreur de connexion à l'équipement ALLIN I/O 8."""


class InvalidAuth(Exception):
    """Identifiants invalides pour l'équipement ALLIN I/O 8."""


async def _validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Valider les données saisies en testant une connexion au contrôleur ALLIN I/O 8."""
    host = data[CONF_HOST]
    username = data[CONF_USERNAME]
    password = data[CONF_PASSWORD]

    session = aiohttp.ClientSession()
    try:
        auth = Auth(session, f"http://{host}", username, password)
        hub = KMTronicHubAPI(auth)
        # On tente une mise à jour des relais pour valider la connexion
        async with asyncio.timeout(10):
            await hub.async_update_relays()
    except aiohttp.client_exceptions.ClientResponseError as err:
        _LOGGER.warning("Authentication failed when connecting to %s: %s", host, err)
        raise InvalidAuth from err
    except (
        asyncio.TimeoutError,
        aiohttp.client_exceptions.ClientConnectorError,
    ) as err:
        _LOGGER.warning("Error connecting to ALLIN I/O 8 at %s: %s", host, err)
        raise CannotConnect from err
    finally:
        await session.close()

    return {"title": f"ALLIN I/O 8 ({host})"}


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class AllinIo8ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow pour ALLIN I/O 8."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Premier écran de configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await _validate_input(self.hass, user_input)

                # Utiliser l'adresse IP / host comme identifiant unique
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                # On mappe vers nos constantes internes de l'intégration
                data = {
                    CONF_HOSTNAME: user_input[CONF_HOST],
                    ALLIN_CONF_USERNAME: user_input[CONF_USERNAME],
                    ALLIN_CONF_PASSWORD: user_input[CONF_PASSWORD],
                }

                return self.async_create_entry(
                    title=info["title"],
                    data=data,
                )

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Erreur inattendue lors du config flow ALLIN I/O 8")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
