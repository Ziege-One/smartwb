DOMAIN = "smartwb"

PLATFORMS = ["sensor", "number", "switch"]

DEFAULT_SCAN_INTERVAL = 20  # Sekunden

AVAILABLE_ENTITIES = {
    "actualCurrent": "Actual Current",
    "actualPower": "Actual Power",
    "duration": "Duration",
    "vehicleState": "Vehicle State",
    "maxCurrent": "Max Current",
    "actualCurrentMA": "Actual Current (mA)",
    "alwaysActive": "Always Active",
    "lastActionUser": "Last Action User",
    "lastActionUID": "Last Action UID",
    "energy": "Energy",
    "mileage": "Mileage",
    "meterReading": "Meter Reading",
    "currentP1": "Current Phase 1",
    "currentP2": "Current Phase 2",
    "currentP3": "Current Phase 3",
    "voltageP1": "Voltage Phase 1",
    "voltageP2": "Voltage Phase 2",
    "voltageP3": "Voltage Phase 3",
    "useMeter": "Use Meter",
    "RFIDUID": "RFID UID",
    "setCurrentSlider": "Set Current Slider",
}