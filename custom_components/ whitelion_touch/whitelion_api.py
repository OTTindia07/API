import random
import requests


class WhitelionAPI:
    def __init__(self, device_id, ip_address):
        self.device_id = device_id
        self.ip_address = ip_address
        self.logged_in = False
        self.switch_states = {}  # To store the real-time states of switches

    def _generate_serial(self):
        """Generate a random serial number."""
        return random.randint(0, 65535)

    def send_command(self, cmd, data=None, sub_cmd=None):
        """Send a command to the device."""
        payload = {
            "cmd": cmd,
            "device_ID": self.device_id,
            "serial": self._generate_serial(),
        }
        if data:
            payload["data"] = data
        if sub_cmd:
            payload["sub_cmd"] = sub_cmd

        response = requests.post(f"http://{self.ip_address}/api", json=payload)
        response.raise_for_status()
        return response.json()

    def login(self, username="admin", password="1234"):
        """Login to the device."""
        response = self.send_command("LN", [username, password])
        if response.get("error") == 0:
            self.logged_in = True
        else:
            raise Exception("Login failed.")
        return response

    def get_details(self):
        """Fetch device details."""
        return self.send_command("DL")

    def get_status(self):
        """
        Fetch the current status of all switches.
        Updates the `switch_states` dictionary with the latest state.
        """
        response = self.send_command("DS")
        if response.get("error") == 0:
            self._update_switch_states(response.get("data", []))
        else:
            raise Exception("Failed to fetch switch status.")
        return self.switch_states

    def _update_switch_states(self, status_data):
        """
        Parse the `DS` command response to update switch states.
        Example status data: ["01XX1", "02XX0"]
        """
        for status in status_data:
            switch_number = int(status[:2])  # Extract switch number (e.g., "01")
            state = status[-1] == "1"  # Determine if ON ("1") or OFF ("0")
            self.switch_states[switch_number] = state

    def set_switch(self, switch_number, state):
        """Set the state of a specific switch."""
        data = f"{switch_number:02}XX{state}"
        response = self.send_command("ST", data=data)
        if response.get("error") == 0:
            # Update state immediately if the command was successful
            self.switch_states[switch_number] = (state == 1)
        else:
            raise Exception(f"Failed to set switch {switch_number} to state {state}.")
        return response

    def check_touch_event(self):
        """
        Check for touch events on the device using the `HW` command.
        Updates `switch_states` based on touch data.
        """
        response = self.send_command("HW")
        if response.get("error") == 0:
            touch_data = response.get("data", [])
            self._update_switch_states(touch_data)
        else:
            raise Exception("Failed to check touch events.")
        return self.switch_states

    def check_online_status(self):
        """Check if the device is online."""
        response = self.send_command("SM", sub_cmd="info")
        if response.get("error") != 0:
            raise Exception("Device is offline.")
        return response.get("s_data", ["offline"])[-1] == "01"  # Check online status
