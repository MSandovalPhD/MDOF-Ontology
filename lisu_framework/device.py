"""Device module for LISU Framework."""

class Device:
    """Device class representing a VR input device."""
    
    def __init__(self, device_id: str, device_type: str, name: str, ip_address: str, port: int):
        self.device_id = device_id
        self.device_type = device_type
        self.name = name
        self.ip_address = ip_address
        self.port = port
        self.state = "disconnected"
        self.last_heartbeat = 0
        self.observers = []
        
    def add_observer(self, observer):
        """Add an observer to the device."""
        if observer not in self.observers:
            self.observers.append(observer)
            
    def remove_observer(self, observer):
        """Remove an observer from the device."""
        if observer in self.observers:
            self.observers.remove(observer)
            
    def notify_observers(self):
        """Notify all observers of state change."""
        for observer in self.observers:
            observer.on_device_state_changed(self) 