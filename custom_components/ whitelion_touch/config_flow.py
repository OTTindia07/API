import random
import voluptuous as vol
from homeassistant import config_entries
from aiohttp import ClientError
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
                # Validate device information by logging in
                await self._validate_device(ip_address, device_id)
                return self.async_create_entry(
                    title=f"Whitelion Touch {device_id}",
                    data={CONF_IP_ADDRESS: ip_address, CONF_DEVICE_ID: device_id},
                )
            except ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        data_schema = vol.Schema({
            vol.Required(CONF_IP_ADDRESS): str,
            vol.Required(CONF_DEVICE_ID): str,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def _validate_device(self, ip_address, device_id):
        """Validate the device by logging in using the LN command."""
        import aiohttp

        serial_number = random.randint(0, 65536)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{ip_address}/api",
                json={
                    "cmd": "LN",
                    "device_ID": device_id,
                    "data": ["admin", "1234"],
                    "serial": serial_number
                },
                timeout=10,
            ) as resp:
                resp.raise_for_status()
                result = await resp.json()
                if result.get("serial") is None:
                    raise ValueError("Invalid response from device.")
