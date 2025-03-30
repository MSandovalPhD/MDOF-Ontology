import time

class Device:
    def __init__(self, device_id: str, device_type: str, name: str, ip_address: str, port: int):
        self.device_id = device_id
        self.device_type = device_type
        self.name = name
        self.ip_address = ip_address
        self.port = port
        self.is_connected = False
        self.current_mode = None
        self.available_modes = []
        self.command_history = []
        self.last_command_time = None
        self.status = "disconnected"
        self.error_count = 0
        self.last_error = None
        self.connection_attempts = 0
        self.max_connection_attempts = 3
        self.reconnect_delay = 5  # seconds
        self.last_heartbeat = None
        self.heartbeat_interval = 30  # seconds
        self._observers = []

    def add_observer(self, observer):
        """Add an observer to be notified of device state changes"""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        """Remove an observer from the notification list"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self):
        """Notify all observers of state changes"""
        for observer in self._observers:
            observer.on_device_state_changed(self)

    def connect(self) -> bool:
        """Attempt to connect to the device"""
        if self.connection_attempts >= self.max_connection_attempts:
            self.status = "connection_failed"
            self.notify_observers()
            return False

        try:
            # Connection logic would go here
            self.is_connected = True
            self.status = "connected"
            self.connection_attempts = 0
            self.last_heartbeat = time.time()
            self.notify_observers()
            return True
        except Exception as e:
            self.connection_attempts += 1
            self.last_error = str(e)
            self.status = "connection_error"
            self.notify_observers()
            return False

    def disconnect(self):
        """Disconnect from the device"""
        self.is_connected = False
        self.status = "disconnected"
        self.current_mode = None
        self.notify_observers()

    def send_command(self, command: str, params: dict = None) -> bool:
        """Send a command to the device"""
        if not self.is_connected:
            self.status = "not_connected"
            self.notify_observers()
            return False

        try:
            # Command sending logic would go here
            self.command_history.append({
                'command': command,
                'params': params,
                'timestamp': time.time()
            })
            self.last_command_time = time.time()
            self.status = "command_sent"
            self.notify_observers()
            return True
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            self.status = "command_error"
            self.notify_observers()
            return False

    def set_mode(self, mode: str) -> bool:
        """Set the device's operating mode"""
        if mode not in self.available_modes:
            self.status = "invalid_mode"
            self.notify_observers()
            return False

        try:
            self.current_mode = mode
            self.status = "mode_changed"
            self.notify_observers()
            return True
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            self.status = "mode_error"
            self.notify_observers()
            return False

    def update_heartbeat(self):
        """Update the device's heartbeat timestamp"""
        self.last_heartbeat = time.time()
        self.status = "connected"
        self.notify_observers()

    def check_connection(self) -> bool:
        """Check if the device connection is still alive"""
        if not self.is_connected:
            return False

        if time.time() - self.last_heartbeat > self.heartbeat_interval:
            self.status = "connection_lost"
            self.is_connected = False
            self.notify_observers()
            return False

        return True

    def get_status_summary(self) -> dict:
        """Get a summary of the device's current status"""
        return {
            'device_id': self.device_id,
            'name': self.name,
            'type': self.device_type,
            'status': self.status,
            'is_connected': self.is_connected,
            'current_mode': self.current_mode,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'last_heartbeat': self.last_heartbeat,
            'connection_attempts': self.connection_attempts
        } 