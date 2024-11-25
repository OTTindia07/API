import voluptuous as vol
from homeassistant import config_entries
from aiohttp import ClientSession, ClientError
import logging

from .const import DOMAIN, CONF_DEVICE_ID, CONF_API_URL

_LOGGER = logging.getLogger(__name__)

class WhitelionTouchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Whitelion Touch Panel."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the input
            if await self._validate_touch_panel(user_input[CONF_API_URL], user_input[CONF_DEVICE_ID]):
                return self.async_create_entry(
                    title=f"Whitelion Panel ({user_input[CONF_DEVICE_ID]})",
                    data=user_input,
                )
            errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE_ID): str,
                vol.Required(CONF_API_URL): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def _validate_touch_panel(self, api_url, device_id):
        """Validate connection to the touch panel."""
        try:
            async with ClientSession() as session:
                payload = {
                    "cmd": "DS",
                    "device_ID": device_id,
                    "serial": 1,
                }
                headers = {"Content-Type": "application/json"}
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        _LOGGER.debug("Validation response: %s", data)
                        return "model" in data  # Validation based on API response
                    else:
                        _LOGGER.error(
                            "Touch panel returned non-200 status: %s", response.status
                        )
        except ClientError as e:
            _LOGGER.error("Error connecting to touch panel: %s", e)
        except Exception as e:
            _LOGGER.error("Unexpected error during validation: %s", e)
        return False
