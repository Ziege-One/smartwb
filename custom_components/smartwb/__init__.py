import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, PLATFORMS, DEFAULT_SCAN_INTERVAL
from .api import SmartWBApi

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up SmartWB from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    ip = entry.data["ip_address"]
    port = entry.data["port"]
    name = entry.data["name"]

    session = async_get_clientsession(hass)
    api = SmartWBApi(session, ip, port)

    async def async_update_data():
        return await api.get_parameters()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="smartwb",
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "config": entry.data,
        "unique_id": f"{ip}:{port}",
        "options": entry.options,
    }

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{ip}:{port}")},
        name=name,
        manufacturer="SmartWB",
        model="SimpleEVSE-WiFi",
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True