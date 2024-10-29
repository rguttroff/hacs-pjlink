"""Config flow for PjLink."""

from __future__ import annotations

import logging
from typing import Any

from pypjlink import Projector
from pypjlink.projector import ProjectorError, POWER_STATES
import voluptuous as vol

from homeassistant import data_entry_flow
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME, CONF_PASSWORD
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_ENCODING, ERR_PROJECTOR_UNAVAILABLE, DEFAULT_ENCODING, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)


class PjLinkFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a PjLink config flow."""

    VERSION = 1

    host: str
    port: str 
    name: str
    encoding: str
    password: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> data_entry_flow.ConfigFlowResult:
        """Handle a flow initiated by the user."""
        # Request user input, unless we are preparing discovery flow
        if user_input is None:
            return self._show_setup_form()

        self.host = user_input[CONF_HOST]
        self.port = user_input[CONF_PORT]
        self.name = user_input[CONF_NAME]
        self.encoding = user_input[CONF_ENCODING]
        self.password = user_input[CONF_PASSWORD]

        errors = {}
        # Check if device is a PjLink device

        try:
            projector = Projector.from_address(self.host, self.port)
            projector.authenticate(None if self.password == "" else self.password)
        except (TimeoutError, OSError) as err:
            errors["base"] = ERR_PROJECTOR_UNAVAILABLE
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        if not errors:
            await self.async_set_unique_id(self.host, raise_on_progress=False)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=self.name,
                data={
                    CONF_HOST: self.host,
                    CONF_PORT: self.port,
                    CONF_NAME: self.name,
                    CONF_ENCODING: self.encoding,
                    CONF_PASSWORD: self.password
                },
            )

        return self._show_setup_form(errors)

    def _show_setup_form(
        self, errors: dict | None = None
    ) -> data_entry_flow.ConfigFlowResult:
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema = vol.Schema(
                {
                    vol.Required(CONF_NAME): cv.string,
                    vol.Required(CONF_HOST): cv.string,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
                    vol.Optional(CONF_PASSWORD, default=""): cv.string,
                    vol.Optional(CONF_ENCODING, default=DEFAULT_ENCODING): cv.string,
                }
            ),
            errors=errors or {},
        )

    async def async_step_confirm(
        self, user_input=None
    ) -> data_entry_flow.ConfigFlowResult:
        """Allow the user to confirm adding the device."""
        if user_input is not None:
            return self.async_create_entry(
                title=self.name,
                data={
                    CONF_HOST: self.host,
                    CONF_PORT: self.port,
                    CONF_NAME: self.name,
                    CONF_ENCODING: self.encoding,
                    CONF_PASSWORD: self.password
                },
            )

        return self.async_show_form(step_id="confirm")