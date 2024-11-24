"""Config flow for Whitelion Touch integration."""
from homeassistant import config_entries
import requests
from .const import DOMAIN

class WhitelionTouchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Whitelion Touch."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            ip_address = user_input["ip_address"]
            device_id = user_input["device_id"]

            # Fetch device info using DL command
            device_info = await self.hass.async_add_executor_job(fetch_device_info, ip_address, device_id)
            if device_info is None:
                errors["base"] = "cannot_connect"
            elif "model" not in device_info:
                errors["base"] = "invalid_response"
            else:
                return self.async_create_entry(
                    title=f"Whitelion {device_info['model']}",
                    data={
                        "ip_address": ip_address,
                        "device_id": device_id,
                        "model": device_info["model"]
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address"): str,
                vol.Required("device_id"): str,
            }),
            errors=errors,
        )

def fetch_device_info(ip_address, device_id):
    """Fetch device information using DL command."""
    try:
        response = requests.post(
            f"http://{ip_address}/api",
            json={"cmd": "DL", "device_ID": device_id, "serial": 12345},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None
