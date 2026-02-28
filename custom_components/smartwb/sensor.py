import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, AVAILABLE_ENTITIES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    config = data["config"]
    unique_id = data["unique_id"]
    options = entry.options or {}

    ip = config["ip_address"]
    port = config["port"]
    device_name = config["name"]

    sensor_definitions = [
        ("actualCurrent", "Actual Current", "A", "mdi:current-ac"),
        ("actualPower", "Actual Power", "kW", "mdi:lightning-bolt"),
        ("duration", "Duration", "min", "mdi:clock-time-eight-outline"),
        ("vehicleState", "Vehicle State", None, None),
        ("maxCurrent", "Max Current", "A", "mdi:current-ac"),
        ("actualCurrentMA", "Actual Current (mA)", "mA", "mdi:current-ac"),
        ("alwaysActive", "Always Active", None, "mdi:clock-time-eight-outline"),
        ("lastActionUser", "Last Action User", None, None),
        ("lastActionUID", "Last Action UID", None, None),
        ("energy", "Energy", "kWh", "mdi:lightning-bolt"),
        ("mileage", "Mileage", "km", "mdi:map-marker-distance"),
        ("meterReading", "Meter Reading", UnitOfEnergy.KILO_WATT_HOUR, "mdi:meter-electric"),
        ("currentP1", "Current Phase 1", "A", "mdi:current-ac"),
        ("currentP2", "Current Phase 2", "A", "mdi:current-ac"),
        ("currentP3", "Current Phase 3", "A", "mdi:current-ac"),
        ("voltageP1", "Voltage Phase 1", "V", "mdi:lightning-bolt"),
        ("voltageP2", "Voltage Phase 2", "V", "mdi:lightning-bolt"),
        ("voltageP3", "Voltage Phase 3", "V", "mdi:lightning-bolt"),
        ("useMeter", "Use Meter", None, None),
        ("RFIDUID", "RFID UID", None, None),
    ]

    entities = []

    for attribute, name, unit, icon in sensor_definitions:
        if attribute in AVAILABLE_ENTITIES and options.get(attribute, True):
            entities.append(
                SmartWBSensor(
                    coordinator,
                    unique_id,
                    device_name,
                    ip,
                    port,
                    attribute,
                    name,
                    unit,
                    icon,
                )
            )

    async_add_entities(entities)


class SmartWBSensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator,
        unique_id,
        device_name,
        ip,
        port,
        attribute,
        name,
        unit,
        icon,
    ):
        super().__init__(coordinator)
        self._attr_unique_id = f"{unique_id}_{attribute}"
        self._device_name = device_name
        self._ip = ip
        self._port = port
        self._attribute = attribute
        self._attr_name = name
        self._icon = icon

        if attribute == "meterReading":
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_state_class = SensorStateClass.TOTAL
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
            self._attr_suggested_display_precision = 2
        else:
            self._attr_native_unit_of_measurement = unit

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._attr_unique_id.split("_")[0])},
            "name": self._device_name,
            "manufacturer": "SmartWB",
            "model": "SimpleEVSE-WiFi",
            "configuration_url": f"http://{self._ip}:{self._port}",
        }

    @property
    def native_value(self):
        value = self.coordinator.data.get(self._attribute)
        if self._attribute == "vehicleState":
            return self._map_vehicle_state(value)
        return value

    @property
    def icon(self):
        if self._attribute == "vehicleState":
            return self._vehicle_state_icon()
        return self._icon

    def _map_vehicle_state(self, value):
        try:
            value = int(value)
        except Exception:
            return "Unknown"
        return {
            1: "Ready",
            2: "Connected",
            3: "Charging",
            5: "Error",
        }.get(value, "Unknown")

    def _vehicle_state_icon(self):
        return {
            "Ready": "mdi:ev-station",
            "Connected": "mdi:car-connected",
            "Charging": "mdi:car-electric",
            "Error": "mdi:alert-circle",
            "Unknown": "mdi:help-circle",
        }.get(self.native_value, "mdi:help-circle")