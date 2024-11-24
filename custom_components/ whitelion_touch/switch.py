class WhitelionSwitch(SwitchEntity):
    """Representation of a Whitelion Touch switch."""

    def __init__(self, device_id, ip_address, switch_id, serial):
        self._device_id = device_id
        self._ip_address = ip_address
        self._switch_id = switch_id
        self._serial = serial
        self._state = False

    @property
    def name(self):
        """Return the name of the switch."""
        return f"Switch {self._switch_id}"  # Uses dynamic naming

    # Other methods remain the same as before...
