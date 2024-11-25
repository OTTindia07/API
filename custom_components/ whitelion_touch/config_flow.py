from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_DEVICE_ID, CONF_HOST

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_DEVICE_ID): str,
})

class TouchPanelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for touch panel integration."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Touch Panel", data=user_input)
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)
