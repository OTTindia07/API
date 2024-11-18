import requests

class WhitelionTouchAPI:
    def __init__(self, host, device_id):
        self.host = host
        self.device_id = device_id

    def send_command(self, cmd, data=None):
        """Send a command to the touch panel."""
        payload = {
            "cmd": cmd,
            "device_ID": self.device_id,
            "data": data,
            "serial": 12345  # Example serial number, could be dynamic
        }
        try:
            response = requests.post(f"http://{self.host}/command", json=payload, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Request failed: {e}"}

    def login(self, username, password):
        """Login to the touch panel."""
        return self.send_command("LN", [username, password])

    def get_details(self):
        """Get details of the touch panel."""
        return self.send_command("DL")

    def get_status(self):
        """Get status of the touch panel."""
        return self.send_command("SS")

    def set_switch(self, switch_id, state):
        """Turn a switch ON/OFF."""
        data = f"0{switch_id}XX{1 if state else 0}"
        return self.send_command("ST", data)
