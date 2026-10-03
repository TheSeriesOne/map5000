import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import Map5000Api
from .const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, DOMAIN


class Map5000ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für MAP 5000 - by MK."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """MAP-5000-Verbindung konfigurieren."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            api = Map5000Api(host, username, password)

            try:
                await api.get_config()
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(host.lower())
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"MAP 5000 - by MK ({host})",
                    data={
                        CONF_HOST: host,
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST,
                    default=(
                        user_input.get(CONF_HOST, "")
                        if user_input
                        else ""
                    ),
                ): str,
                vol.Required(
                    CONF_USERNAME,
                    default=(
                        user_input.get(CONF_USERNAME, "")
                        if user_input
                        else ""
                    ),
                ): str,
                vol.Required(CONF_PASSWORD): TextSelector(
                    TextSelectorConfig(
                        type=TextSelectorType.PASSWORD,
                        autocomplete="current-password",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
