import time

class Mode:
    def __init__(self, mode_id: str, name: str, description: str):
        self.mode_id = mode_id
        self.name = name
        self.description = description
        self.allowed_commands = []
        self.required_commands = []
        self.state_variables = {}
        self.transitions = {}
        self.current_state = "initial"
        self._observers = []
        self._history = []

    def add_observer(self, observer):
        """Add an observer to be notified of mode state changes"""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        """Remove an observer from the notification list"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, event: str, data: dict = None):
        """Notify all observers of mode state changes"""
        for observer in self._observers:
            observer.on_mode_state_changed(self, event, data)

    def add_command(self, command_id: str, required: bool = False):
        """Add a command to the mode's allowed commands"""
        if command_id not in self.allowed_commands:
            self.allowed_commands.append(command_id)
            if required:
                self.required_commands.append(command_id)

    def remove_command(self, command_id: str):
        """Remove a command from the mode's allowed commands"""
        if command_id in self.allowed_commands:
            self.allowed_commands.remove(command_id)
        if command_id in self.required_commands:
            self.required_commands.remove(command_id)

    def is_command_allowed(self, command_id: str) -> bool:
        """Check if a command is allowed in the current mode"""
        return command_id in self.allowed_commands

    def add_transition(self, from_state: str, to_state: str, conditions: dict = None):
        """Add a state transition with optional conditions"""
        if from_state not in self.transitions:
            self.transitions[from_state] = []
        self.transitions[from_state].append({
            'to_state': to_state,
            'conditions': conditions or {}
        })

    def can_transition_to(self, to_state: str) -> tuple[bool, str]:
        """Check if transition to the specified state is allowed"""
        if self.current_state not in self.transitions:
            return False, f"No transitions defined from state: {self.current_state}"

        for transition in self.transitions[self.current_state]:
            if transition['to_state'] == to_state:
                # Check conditions
                for condition, value in transition['conditions'].items():
                    if condition in self.state_variables:
                        if self.state_variables[condition] != value:
                            return False, f"Condition not met: {condition} = {value}"
                return True, "Transition allowed"

        return False, f"No transition defined to state: {to_state}"

    def transition_to(self, to_state: str) -> bool:
        """Attempt to transition to the specified state"""
        can_transition, message = self.can_transition_to(to_state)
        if not can_transition:
            self.notify_observers("transition_failed", {"message": message})
            return False

        # Record transition in history
        self._history.append({
            'from_state': self.current_state,
            'to_state': to_state,
            'timestamp': time.time()
        })

        # Update current state
        self.current_state = to_state
        self.notify_observers("state_changed", {
            'from_state': self.current_state,
            'to_state': to_state
        })
        return True

    def set_state_variable(self, name: str, value: any):
        """Set a state variable value"""
        self.state_variables[name] = value
        self.notify_observers("variable_changed", {
            'name': name,
            'value': value
        })

    def get_state_variable(self, name: str) -> any:
        """Get a state variable value"""
        return self.state_variables.get(name)

    def get_transition_history(self) -> list:
        """Get the history of state transitions"""
        return self._history

    def get_current_state_info(self) -> dict:
        """Get information about the current state"""
        return {
            'mode_id': self.mode_id,
            'name': self.name,
            'current_state': self.current_state,
            'state_variables': self.state_variables,
            'allowed_commands': self.allowed_commands,
            'required_commands': self.required_commands
        } 