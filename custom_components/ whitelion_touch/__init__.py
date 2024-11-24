from homeassistant.core import HomeAssistant

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Whitelion Touch integration."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up Whitelion Touch from a config entry."""
    hass.data.setdefault("whitelion_touch", {})
    hass.data["whitelion_touch"][entry.entry_id] = entry.data
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload a config entry."""
    hass.data["whitelion_touch"].pop(entry.entry_id)
    return True
