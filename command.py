import time

class Command:
    def __init__(self, command_id: str, name: str, description: str, parameters: dict = None):
        self.command_id = command_id
        self.name = name
        self.description = description
        self.parameters = parameters or {}
        self.required_parameters = []
        self.parameter_types = {}
        self.parameter_ranges = {}
        self.execution_timeout = 5  # seconds
        self.retry_count = 3
        self.retry_delay = 1  # seconds
        self._observers = []

    def add_observer(self, observer):
        """Add an observer to be notified of command execution status"""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        """Remove an observer from the notification list"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, status: str, result: dict = None):
        """Notify all observers of command execution status"""
        for observer in self._observers:
            observer.on_command_executed(self, status, result)

    def validate_parameters(self, params: dict) -> tuple[bool, str]:
        """Validate command parameters against defined requirements"""
        # Check required parameters
        for param in self.required_parameters:
            if param not in params:
                return False, f"Missing required parameter: {param}"

        # Check parameter types
        for param, value in params.items():
            if param in self.parameter_types:
                expected_type = self.parameter_types[param]
                if not isinstance(value, expected_type):
                    return False, f"Invalid type for parameter {param}: expected {expected_type.__name__}"

        # Check parameter ranges
        for param, value in params.items():
            if param in self.parameter_ranges:
                min_val, max_val = self.parameter_ranges[param]
                if not (min_val <= value <= max_val):
                    return False, f"Parameter {param} out of range: {min_val} <= {value} <= {max_val}"

        return True, "Parameters valid"

    def execute(self, device, params: dict = None) -> tuple[bool, dict]:
        """Execute the command on a device with the given parameters"""
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(params or {})
        if not is_valid:
            self.notify_observers("validation_error", {"error": error_msg})
            return False, {"error": error_msg}

        # Execute command with retries
        for attempt in range(self.retry_count):
            try:
                # Command execution logic would go here
                result = {
                    "command_id": self.command_id,
                    "device_id": device.device_id,
                    "parameters": params,
                    "timestamp": time.time(),
                    "attempt": attempt + 1
                }
                
                self.notify_observers("success", result)
                return True, result
            except Exception as e:
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    error_result = {
                        "error": str(e),
                        "command_id": self.command_id,
                        "device_id": device.device_id,
                        "parameters": params,
                        "timestamp": time.time(),
                        "attempts": attempt + 1
                    }
                    self.notify_observers("error", error_result)
                    return False, error_result

    def get_parameter_info(self) -> dict:
        """Get information about command parameters"""
        return {
            "required": self.required_parameters,
            "types": self.parameter_types,
            "ranges": self.parameter_ranges,
            "defaults": self.parameters
        } 