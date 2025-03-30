from owlready2 import *
import numpy as np
import usb.core
import usb.util
from typing import Dict, List, Any, Optional
import time
from datetime import datetime

class LISUFramework:
    def __init__(self, ontology_path: str):
        """Initialize the LISU framework with an ontology."""
        self.ontology = get_ontology(ontology_path).load()
        self.device_layer = DeviceLayer()
        self.controllers_manager = ControllersManager()
        self.mapping_matrix = MappingMatrix()
        
    def initialize_devices(self):
        """Initialize and detect all VR devices."""
        self.device_layer.detect_devices()
        self.controllers_manager.initialize_controllers()
        
    def create_mapping(self, input_set: List[str], action_set: List[str]):
        """Create a mapping between input set C and action set A."""
        self.mapping_matrix.create_mapping(input_set, action_set)
        
    def process_input(self, input_data: Dict[str, Any]):
        """Process input data and map it to corresponding actions."""
        return self.mapping_matrix.map_input_to_action(input_data)

class DeviceLayer:
    def __init__(self):
        self.devices = {}
        self.polling_rate = 1000  # Hz
        self.input_latency = 0.016  # seconds
        self.input_buffer_size = 64
        
    def detect_devices(self):
        """Detect USB devices and create device instances."""
        for device in usb.core.find(find_all=True):
            if self._is_vr_device(device):
                self._create_device_instance(device)
                
    def _is_vr_device(self, device) -> bool:
        """Check if the device is a VR device based on vendor and product IDs."""
        try:
            # Query the ontology for known VR device IDs
            vr_devices = list(self.ontology.search(type=self.ontology.InputMethod))
            for vr_device in vr_devices:
                if (device.idVendor == int(vr_device.vendorID, 16) and 
                    device.idProduct == int(vr_device.productID, 16)):
                    return True
            return False
        except:
            return False
            
    def _create_device_instance(self, device):
        """Create a device instance based on the ontology."""
        device_type = self._get_device_type(device)
        if device_type:
            self.devices[device.idVendor] = {
                'device': device,
                'type': device_type,
                'last_update': datetime.now(),
                'is_detected': True
            }
            
    def _get_device_type(self, device) -> Optional[str]:
        """Get the device type from the ontology."""
        try:
            for vr_device in self.ontology.search(type=self.ontology.InputMethod):
                if (device.idVendor == int(vr_device.vendorID, 16) and 
                    device.idProduct == int(vr_device.productID, 16)):
                    return vr_device.name
            return None
        except:
            return None

class ControllersManager:
    def __init__(self):
        self.controllers = {}
        self.error_states = {}
        
    def initialize_controllers(self):
        """Initialize all detected controllers."""
        for device_id, device_info in self.device_layer.devices.items():
            if self._is_controller(device_info['type']):
                self._create_controller(device_id, device_info)
                
    def _is_controller(self, device_type: str) -> bool:
        """Check if the device is a controller based on the ontology."""
        return device_type in ['VR_Controller', 'Wired_Controller', 'Wireless_Controller']
        
    def _create_controller(self, device_id: int, device_info: Dict):
        """Create a controller instance with error handling."""
        try:
            controller = {
                'device': device_info['device'],
                'type': device_info['type'],
                'state': 'initialized',
                'error_state': None,
                'last_update': datetime.now()
            }
            self.controllers[device_id] = controller
        except Exception as e:
            self._handle_controller_error(device_id, str(e))
            
    def _handle_controller_error(self, device_id: int, error_message: str):
        """Handle controller errors and update error state."""
        self.error_states[device_id] = {
            'error_code': 1001,
            'error_message': error_message,
            'last_error_time': datetime.now(),
            'recovery_attempts': 0
        }

class MappingMatrix:
    def __init__(self):
        self.mappings = {}
        self.input_config = {}
        self.mapping_config = {}
        
    def create_mapping(self, input_set: List[str], action_set: List[str]):
        """Create a mapping between input set C and action set A."""
        for action in action_set:
            self.mappings[action] = {
                'inputs': input_set,
                'priority': 1,
                'enabled': True
            }
            
    def map_input_to_action(self, input_data: Dict[str, Any]) -> List[str]:
        """Map input data to corresponding actions."""
        triggered_actions = []
        for action, mapping in self.mappings.items():
            if self._check_input_matches(input_data, mapping['inputs']):
                triggered_actions.append(action)
        return triggered_actions
        
    def _check_input_matches(self, input_data: Dict[str, Any], 
                           required_inputs: List[str]) -> bool:
        """Check if the input data matches the required inputs."""
        return all(input_name in input_data for input_name in required_inputs)

def main():
    # Example usage
    lisu = LISUFramework("VR_Device_Ontology.owx")
    
    # Initialize devices
    lisu.initialize_devices()
    
    # Example input set C and action set A
    input_set = ['button_press', 'trigger_pull', 'joystick_movement']
    action_set = ['grab', 'teleport', 'menu_select']
    
    # Create mapping
    lisu.create_mapping(input_set, action_set)
    
    # Example input data
    input_data = {
        'button_press': True,
        'trigger_pull': 0.8,
        'joystick_movement': (0.5, 0.3)
    }
    
    # Process input and get actions
    actions = lisu.process_input(input_data)
    print(f"Triggered actions: {actions}")

if __name__ == "__main__":
    main() 