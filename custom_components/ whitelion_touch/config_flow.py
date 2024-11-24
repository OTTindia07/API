from homeassistant import config_entries
import voluptuous as vol
import requests

from .const import DOMAIN, CONF_DEVICE_ID, CONF_IP_ADDRESS, CONF_SERIAL

class WhitelionTouchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Whitelion Touch."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            ip_address = user_input[CONF_IP_ADDRESS]
            device_id = user_input[CONF_DEVICE_ID]

            # Fetch device information using DL command
            try:
                response = requests.post(
                    f"http://{ip_address}/api",
                    json={
                        "cmd": "DL",
                        "device_ID": device_id,
                        "serial": 12345
                    },
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()

                device_model = data.get("model")
                device_serial = data.get("serial")

                if device_model and device_serial:
                    user_input[CONF_SERIAL] = device_serial
                    return self.async_create_entry(
                        title=f"Whitelion {device_model}",
                        data=user_input
                    )
                else:
                    errors["base"] = "invalid_response"

            except requests.RequestException:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema({
            vol.Required(CONF_IP_ADDRESS): str,
            vol.Required(CONF_DEVICE_ID): str,
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors
        )
