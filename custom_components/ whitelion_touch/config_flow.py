import random
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_DEVICE_ID, CONF_IP_ADDRESS, CONF_MODEL

class WhitelionTouchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Whitelion Touch."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            ip_address = user_input[CONF_IP_ADDRESS]
            device_id = user_input[CONF_DEVICE_ID]
            try:
                # Attempt to log in and fetch device info
                device_info = await self.hass.async_add_executor_job(
                    self.login_and_fetch_info, ip_address, device_id
                )
                model = device_info.get("model")
                return self.async_create_entry(
                    title=f"Whitelion {device_id}",
                    data={
                        CONF_IP_ADDRESS: ip_address,
                        CONF_DEVICE_ID: device_id,
                        CONF_MODEL: model
                    },
                )
            except Exception as e:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema({
            vol.Required(CONF_IP_ADDRESS): str,
            vol.Required(CONF_DEVICE_ID): str,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    def login_and_fetch_info(self, ip_address, device_id):
        """Log in and fetch device information."""
        import requests

        # Login command
        serial_number = random.randint(0, 65536)
        login_response = requests.post(
            f"http://{ip_address}/api",
            json={"cmd": "LN", "device_ID": device_id, "data": ["admin", "1234"], "serial": serial_number},
            timeout=10
        )
        login_response.raise_for_status()

        # Fetch model command
        serial_number = random.randint(0, 65536)
        model_response = requests.post(
            f"http://{ip_address}/api",
            json={"cmd": "DL", "device_ID": device_id, "serial": serial_number},
            timeout=10
        )
        model_response.raise_for_status()

        return model_response.json()
