import logging
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SERIAL
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class TouchPanelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self.host = None
        self.name = None
        self.serial = None

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.host = user_input[CONF_HOST]
            self.name = user_input[CONF_NAME]
            self.serial = user_input[CONF_SERIAL]
            # We assume that "device" is already verified at this point
            return self.async_create_entry(
                title=self.name,
                data={
                    CONF_HOST: self.host,
                    CONF_NAME: self.name,
                    CONF_SERIAL: self.serial
                }
            )
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema()
        )

    def _get_schema(self):
        """Return schema for the user input form."""
        from homeassistant.helpers import config_validation as cv
        import voluptuous as vol
        return vol.Schema({
            vol.Required(CONF_HOST): cv.string,
            vol.Required(CONF_NAME): cv.string,
            vol.Required(CONF_SERIAL): cv.string,
        })
