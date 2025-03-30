"""Mode module for LISU Framework."""

class Mode:
    """Mode class representing a device operating mode."""
    
    def __init__(self, mode_id: str, name: str, description: str):
        self.mode_id = mode_id
        self.name = name
        self.description = description
        self.observers = []
        
    def add_observer(self, observer):
        """Add an observer to the mode."""
        if observer not in self.observers:
            self.observers.append(observer)
            
    def remove_observer(self, observer):
        """Remove an observer from the mode."""
        if observer in self.observers:
            self.observers.remove(observer)
            
    def notify_observers(self, event: str, data: dict):
        """Notify all observers of mode state change."""
        for observer in self.observers:
            observer.on_mode_state_changed(self, event, data) 