import random
import requests
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

class TouchPanelSwitch(SwitchEntity):
    """Representation of a Touch Panel switch."""

    def __init__(self, coordinator, config, switch_number):
        self._coordinator = coordinator
        self._config = config
        self._switch_number = switch_number
        self._state = False

    @property
    def name(self):
        return f"{self._config['device_id']} Switch {self._switch_number}"

    @property
    def is_on(self):
        return self._state

    def turn_on(self, **kwargs):
        self._send_command("1")

    def turn_off(self, **kwargs):
        self._send_command("0")

    def update(self):
        """Update switch state."""
        self._state = self._coordinator.data.get(f"{self._switch_number}XX1N", False)

    def _send_command(self, state):
        serial = random.randint(1, 65535)
        cmd_data = f"0{self._switch_number}XX{state}"
        payload = {
            "cmd": "ST",
            "device_ID": self._config["device_id"],
            "data": cmd_data,
            "serial": serial,
        }
        headers = {"Content-Type": "application/json"}
        try:
            requests.post(f"http://{self._config['host']}/api", json=payload, headers=headers)
        except Exception as e:
            print(f"Error sending command for {self.name}: {e}")
