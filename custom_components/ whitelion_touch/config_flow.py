from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN
from .whitelion_api import WhitelionAPI

class WhitelionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Whitelion Touch."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input:
            api = WhitelionAPI(user_input["device_id"], user_input["ip_address"])
            try:
                await self.hass.async_add_executor_job(api.login)
                details = await self.hass.async_add_executor_job(api.get_details)
                model = details.get("model")
                if not model:
                    errors["base"] = "model_not_found"
                else:
                    return self.async_create_entry(
                        title=f"Whitelion {model}",
                        data={
                            "device_id": user_input["device_id"],
                            "ip_address": user_input["ip_address"],
                            "model": model,
                        },
                    )
            except Exception:
                errors["base"] = "connection_failed"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("device_id"): str,
                vol.Required("ip_address"): str,
            }),
            errors=errors,
        )
