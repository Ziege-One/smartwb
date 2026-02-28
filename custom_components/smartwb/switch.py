import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]
    config = data["config"]
    unique_id = data["unique_id"]
    options = entry.options or {}

    if not options.get("alwaysActive", True):
        return

    ip = config["ip_address"]
    port = config["port"]
    device_name = config["name"]

    async_add_entities(
        [
            SmartWBAlwaysActiveSwitch(
                coordinator,
                api,
                f"{device_name} Always Active",
                ip,
                port,
                unique_id,
                device_name,
            )
        ]
    )


class SmartWBAlwaysActiveSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(
        self,
        coordinator,
        api,
        name,
        ip,
        port,
        unique_id,
        device_name,
    ):
        super().__init__(coordinator)
        self._api = api
        self._attr_name = name
        self._ip = ip
        self._port = port
        self._device_name = device_name
        self._attr_unique_id = f"{unique_id}_always_active"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._attr_unique_id.split("_")[0])},
            "manufacturer": "SmartWB",
            "model": "SimpleEVSE-WiFi",
            "name": self._device_name,
        }

    @property
    def is_on(self):
        return bool(self.coordinator.data.get("alwaysActive"))

    async def async_turn_on(self, **kwargs):
        try:
            text = await self._api.set_always_active(True)
            _LOGGER.debug("setAlwaysActive ON response: %s", text)
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error("Error turning alwaysActive on: %s", e)

    async def async_turn_off(self, **kwargs):
        try:
            text = await self._api.set_always_active(False)
            _LOGGER.debug("setAlwaysActive OFF response: %s", text)
            await self.coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error("Error turning alwaysActive off: %s", e)