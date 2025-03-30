# LISU Framework Ontology UI

A modern, user-friendly interface for controlling and monitoring VR (Virtual Reality) input devices. The LISU Framework Ontology UI provides a robust platform for managing VR controllers, motion platforms, and haptic devices through an intuitive graphical interface.

## Features

### Device Management
- **Connection Control**: Easy connection to VR controllers, motion platforms, and haptic devices
- **UDP Communication**: Configurable IP and port settings for device communication
- **Real-time Monitoring**: Live device status tracking and heartbeat monitoring
- **Status Indicators**: Visual feedback for connection state, current mode, and command status

### Control Capabilities
- **Three-Axis Control**: Precise control over X, Y, and Z axes
- **Device Operations**: Position reset and device calibration functions
- **Mode Switching**: Toggle between default and calibration modes
- **Command System**: Structured command execution with parameter management

### User Interface
- **Modern Design**: Clean, intuitive interface with dark/light theme support
- **Visual Feedback**: Status indicators with color-coded information
- **Comprehensive Logging**: Detailed operation tracking and error reporting
- **Icon-Based Controls**: Intuitive button layout with visual indicators

### Technical Architecture
- **Observer Pattern**: Real-time updates for device state changes
- **Command-Based Architecture**: Structured approach to device control
- **Modular Design**: Separate components for devices, commands, and modes
- **Cross-Platform**: Compatible with Windows, macOS, and Linux

## Installation

You can install the package directly from PyPI:

```bash
pip install lisu-framework-ontology
```

Or install from source:

```bash
git clone https://github.com/yourusername/MDOF-Ontology
cd MDOF-Ontology
pip install -e .
```

## Usage

After installation, you can run the UI using:

```bash
lisu-ontology
```

Or from Python:

```python
from lisu_framework.run_ui import main
main()
```

## Requirements

- Python 3.8 or higher
- PyQt6
- darkdetect
- qtawesome

## Development

To set up the development environment:

1. Clone the repository
2. Create a virtual environment
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Project Structure

```
MDOF-Ontology/
├── lisu_framework/          # Main package directory
│   ├── ui/                 # UI components
│   ├── resources/          # Application resources
│   └── run_ui.py          # Application entry point
├── setup.py               # Package configuration
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your chosen license]

## Contact

[Your contact information] 

