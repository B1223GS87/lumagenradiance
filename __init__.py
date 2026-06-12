"""The Lumagen Radiance integration."""

import logging
from typing import Dict, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .coordinator import LumagenDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Lumagen Radiance from a config entry."""
    host = entry.data["host"]
    port = entry.data.get("port", 10001)

    coordinator = LumagenDataUpdateCoordinator(hass, host, port)
    await coordinator.async_connect()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["switch", "select", "button", "sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator: LumagenDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_close()
    return await hass.config_entries.async_unload_platforms(entry, ["switch", "select", "button", "sensor"])
