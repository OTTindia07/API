import random
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_DEVICE_ID, CONF_IP_ADDRESS

class WhitelionTouchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Whitelion Touch."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            ip_address = user_input[CONF_IP_ADDRESS]
            device_id = user_input[CONF_DEVICE_ID]
            try:
                device_info = await self.hass.async_add_executor_job(self.fetch_device_info, ip_address, device_id)
                if device_info:
                    return self.async_create_entry(
                        title=f"Whitelion {device_info['model']}",
                        data={
                            CONF_IP_ADDRESS: ip_address,
                            CONF_DEVICE_ID: device_id,
                            "model": device_info["model"]
                        }
                    )
                else:
                    errors["base"] = "invalid_response"
            except Exception:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema({
            vol.Required(CONF_IP_ADDRESS): str,
            vol.Required(CONF_DEVICE_ID): str,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    def fetch_device_info(self, ip_address, device_id):
        """Fetch device information."""
        import requests
        serial_number = random.randint(0, 65536)
        response = requests.post(
            f"http://{ip_address}/api",
            json={"cmd": "DL", "device_ID": device_id, "serial": serial_number},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
