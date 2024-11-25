"""Config flow for Touch Panel integration."""
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
import requests
import random

from .const import DOMAIN, CONF_DEVICE_ID, CONF_API_URL, CONF_NAME

class TouchPanelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Touch Panel."""

    VERSION = 1

    def _generate_serial(self):
        """Generate a unique random serial number."""
        return random.randint(0, 65535)

    def _test_connection(self, api_url, device_id):
        """Test connectivity to the device."""
        headers = {"Content-Type": "application/json"}
        serial = self._generate_serial()
        payload = {"cmd": "DS", "device_ID": device_id, "serial": serial}

        try:
            response = requests.post(f"http://{api_url}/api", json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("error") == 0:  # Connection successful
                    return True
            return False
        except requests.RequestException:
            return False

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            # Validate the connection to the device
            api_url = user_input[CONF_API_URL]
            device_id = user_input[CONF_DEVICE_ID]

            if self._test_connection(api_url, device_id):
                # Create the entry if the connection is successful
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_API_URL: api_url,
                        CONF_DEVICE_ID: device_id,
                    },
                )
            else:
                errors = {"base": "cannot_connect"}
                return self.async_show_form(step_id="user", data_schema=self._get_schema(), errors=errors)

        return self.async_show_form(step_id="user", data_schema=self._get_schema())

    @callback
    def _get_schema(self):
        """Return the schema for user input."""
        return vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_API_URL): str,
                vol.Required(CONF_DEVICE_ID): str,
            }
        )

    async def async_step_import(self, import_data):
        """Handle import from YAML configuration."""
        return await self.async_step_user(user_input=import_data)

