import logging
import random
import requests
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class WhitelionTouchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Whitelion Touch Panel."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            api_url = user_input["api_url"]
            device_id = user_input["device_id"]

            try:
                # Test the connection to the device
                await self.hass.async_add_executor_job(self._test_connection, api_url, device_id)
                
                # Create the entry
                return self.async_create_entry(
                    title=f"Whitelion Panel ({device_id})", data=user_input
                )
            except requests.exceptions.RequestException as err:
                _LOGGER.error("Network error: %s", err)
                errors["base"] = "cannot_connect"
            except ValueError as err:
                _LOGGER.error("Unexpected response format: %s", err)
                errors["base"] = "invalid_response"
            except Exception as err:
                _LOGGER.exception("Unexpected error: %s", err)
                errors["base"] = "unknown"

        # Show the form again with errors if connection failed
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_form_schema(),
            errors=errors
        )

    def _test_connection(self, api_url, device_id):
        """Test connectivity to the device."""
        headers = {"Content-Type": "application/json"}
        serial = self._generate_serial()
        payload = {"cmd": "DS", "device_ID": device_id, "serial": serial}

        try:
            response = requests.post(
                f"http://{api_url}/api", json=payload, headers=headers, timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # Validate the response
            if data.get("error", 1) != 0:
                _LOGGER.error("Device error: %s", data.get("error"))
                raise ValueError(f"Device returned an error: {data.get('error')}")
        except requests.exceptions.ConnectionError as ex:
            _LOGGER.error("Connection failed: %s", ex)
            raise requests.exceptions.RequestException("Failed to connect to the device.")
        except requests.exceptions.Timeout as ex:
            _LOGGER.error("Request timed out: %s", ex)
            raise requests.exceptions.RequestException("Device timeout.")
        except requests.exceptions.JSONDecodeError as ex:
            _LOGGER.error("Invalid JSON response: %s", ex)
            raise ValueError("Invalid JSON received from the device.")

    @staticmethod
    def _generate_serial():
        """Generate a unique random serial number."""
        return random.randint(0, 65536)

    @staticmethod
    def _get_form_schema():
        """Return the form schema for user input."""
        import voluptuous as vol
        return vol.Schema(
            {
                vol.Required("api_url", description="API URL of the touch panel"): str,
                vol.Required("device_id", description="Device ID (e.g., WL-29EA18)"): str,
            }
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the integration."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self._get_options_schema(),
        )

    def _get_options_schema(self):
        """Return options schema."""
        import voluptuous as vol
        return vol.Schema({})
