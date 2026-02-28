import logging

from homeassistant.components.number import NumberEntity
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

    if not options.get("setCurrentSlider", True):
        return

    ip = config["ip_address"]
    port = config["port"]
    device_name = config["name"]

    async_add_entities(
        [
            EVSECurrentSlider(
                coordinator,
                api,
                f"{device_name} Set Current",
                ip,
                port,
                unique_id,
                device_name,
            )
        ]
    )


class EVSECurrentSlider(CoordinatorEntity, NumberEntity):
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
        self._attr_unique_id = f"{unique_id}_set_current"

        self._attr_native_unit_of_measurement = "A"
        self._attr_native_min_value = 6
        self._attr_native_step = 1

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._attr_unique_id.split("_")[0])},
            "manufacturer": "SmartWB",
            "model": "SimpleEVSE-WiFi",
            "name": self._device_name,
        }

    @property
    def native_value(self):
        return self.coordinator.data.get("actualCurrent")

    @property
    def native_max_value(self):
        return self.coordinator.data.get("maxCurrent", 32)

    async def async_set_native_value(self, value):
        current = int(value)
        try:
            text = await self._api.set_current(current)
            if text.startswith("S0_"):
                _LOGGER.info("Set current to %s A", current)
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Unexpected response from setCurrent: %s", text)
        except Exception as e:
            _LOGGER.error("Error setting current: %s", e)