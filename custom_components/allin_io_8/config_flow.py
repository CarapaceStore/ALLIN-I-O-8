"""Config flow pour l'intégration ALLIN I/O 8."""

from __future__ import annotations

import logging

from homeassistant import config_entries
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_HOSTNAME,
    CONF_USERNAME,
    CONF_PASSWORD,
)

_LOGGER = logging.getLogger(__name__)

class AllinIO8ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOSTNAME])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input[CONF_HOSTNAME],
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOSTNAME): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
