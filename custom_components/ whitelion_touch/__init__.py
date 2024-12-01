from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Whitelion Touch from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Replace the deprecated method with the recommended one
    await hass.config_entries.async_forward_entry_setups(entry, ["switch"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    if await hass.config_entries.async_unload_platforms(entry, ["switch"]):
        hass.data[DOMAIN].pop(entry.entry_id)
        return True

    return False
