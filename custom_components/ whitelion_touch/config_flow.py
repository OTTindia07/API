import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .api import WhitelionTouchAPI

class WhitelionTouchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validate the input by logging into the device
            api = WhitelionTouchAPI(
                user_input["host"], user_input["device_id"], user_input["username"], user_input["password"]
            )
            response = await self.hass.async_add_executor_job(api.login)
            if response.get("error") == 0:
                return self.async_create_entry(title=user_input["device_id"], data=user_input)
            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("host"): str,
                vol.Required("device_id"): str,
                vol.Optional("username", default="admin"): str,
                vol.Optional("password", default="1234"): str,
            }),
            errors=errors
        )
