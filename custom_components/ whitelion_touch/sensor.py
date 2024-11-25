import random
import requests
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

class TouchPanelStatusSensor(SensorEntity):
    """Representation of the Touch Panel status."""

    def __init__(self, config):
        self._config = config
        self._state = None

    @property
    def name(self):
        return f"{self._config['device_id']} Status"

    @property
    def state(self):
        return self._state

    def update(self):
        """Fetch the status from the device."""
        serial = random.randint(1, 65535)
        payload = {
            "cmd": "DS",
            "device_ID": self._config["device_id"],
            "serial": serial,
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(f"http://{self._config['host']}/api", json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("serial") == serial:  # Ensure response matches request
                    self._state = data
            else:
                self._state = None
        except Exception as e:
            self._state = None
            print(f"Error updating status sensor: {e}")
