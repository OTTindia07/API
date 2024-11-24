async def async_step_user(self, user_input=None):
    """Handle the initial step."""
    errors = {}

    if user_input is not None:
        ip_address = user_input[CONF_IP_ADDRESS]
        device_id = user_input[CONF_DEVICE_ID]

        try:
            # Fetch device information
            device_info = await self.hass.async_add_executor_job(self.fetch_device_info, ip_address, device_id)
            if device_info and 'model' in device_info:
                return self.async_create_entry(
                    title=f"Whitelion {device_info['model']}",
                    data={
                        CONF_IP_ADDRESS: ip_address,
                        CONF_DEVICE_ID: device_id,
                        CONF_MODEL: device_info["model"],
                    }
                )
            else:
                errors["base"] = "invalid_response"
        except Exception as e:
            _LOGGER.error(f"Error connecting to device: {e}")
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
