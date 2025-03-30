# LISU Framework Implementation

This implementation demonstrates how to use the VR Device Ontology with the LISU framework for mapping VR input devices to application actions.

## Overview

The LISU framework provides a mapping matrix process that connects raw input data from VR devices to application actions. It consists of three main components:

1. **Device Layer**: Handles device detection and input collection
2. **Controllers Manager**: Manages controller instances and error handling
3. **Mapping Matrix**: Maps input data to application actions

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your VR Device Ontology file (`VR_Device_Ontology.owx`) in the same directory as the Python files.

2. Basic usage example:
```python
from lisu_framework import LISUFramework

# Initialize the framework
lisu = LISUFramework("VR_Device_Ontology.owx")

# Initialize devices
lisu.initialize_devices()

# Define input set C and action set A
input_set = ['button_press', 'trigger_pull', 'joystick_movement']
action_set = ['grab', 'teleport', 'menu_select']

# Create mapping
lisu.create_mapping(input_set, action_set)

# Process input data
input_data = {
    'button_press': True,
    'trigger_pull': 0.8,
    'joystick_movement': (0.5, 0.3)
}

# Get corresponding actions
actions = lisu.process_input(input_data)
```

## Components

### Device Layer
- Detects USB-connected VR devices
- Manages device properties (polling rate, latency, buffer size)
- Handles device identification using vendor and product IDs

### Controllers Manager
- Initializes and manages controller instances
- Handles controller error states
- Provides real-time controller status updates

### Mapping Matrix
- Creates mappings between input sets and action sets
- Processes input data to trigger corresponding actions
- Supports priority-based action mapping

## Error Handling

The framework includes comprehensive error handling for:
- Device detection failures
- Controller initialization errors
- Input processing errors
- Mapping conflicts

## Performance Considerations

- Polling rate: 1000 Hz
- Input latency: 16ms
- Input buffer size: 64 samples
- Real-time error state tracking

## Contributing

Feel free to submit issues and enhancement requests! 