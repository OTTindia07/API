from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .api import WhitelionTouchAPI

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Whitelion Touch integration."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = WhitelionTouchAPI(
        entry.data["host"],
        entry.data["device_id"],
        entry.data["username"],
        entry.data["password"],
    )

    hass.config_entries.async_setup_platforms(entry, ["switch", "sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, ["switch", "sensor"])
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
