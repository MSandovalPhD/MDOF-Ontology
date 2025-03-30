from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QComboBox, QLineEdit,
                             QTextEdit, QStatusBar, QGroupBox, QGridLayout,
                             QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPen, QColor, QPainterPath
import qtawesome as qta
import darkdetect
from pathlib import Path
import time
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from device import Device
from command import Command
from mode import Mode

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LISU Framework - Ontology Demo")
        self.setMinimumSize(1000, 700)
        
        # Initialize ontology components
        self.device = Device(
            device_id="demo_device_1",
            device_type="vr_controller",
            name="Demo VR Controller",
            ip_address="127.0.0.1",
            port=5000
        )
        
        # Add some demo commands
        self.commands = {
            "connect": Command(
                command_id="connect",
                name="Connect Device",
                description="Establish connection with the device",
                parameters={"timeout": 5}
            ),
            "disconnect": Command(
                command_id="disconnect",
                name="Disconnect Device",
                description="Close connection with the device"
            ),
            "set_mode": Command(
                command_id="set_mode",
                name="Set Mode",
                description="Change device operating mode",
                parameters={"mode": "default"}
            ),
            "control_x": Command(
                command_id="control_x",
                name="X-Axis Control",
                description="Control X-axis movement",
                parameters={"value": 0.0}
            ),
            "control_y": Command(
                command_id="control_y",
                name="Y-Axis Control",
                description="Control Y-axis movement",
                parameters={"value": 0.0}
            ),
            "control_z": Command(
                command_id="control_z",
                name="Z-Axis Control",
                description="Control Z-axis movement",
                parameters={"value": 0.0}
            ),
            "reset": Command(
                command_id="reset",
                name="Reset Position",
                description="Reset device position",
                parameters={}
            ),
            "calibrate": Command(
                command_id="calibrate",
                name="Calibrate",
                description="Calibrate device",
                parameters={}
            )
        }
        
        # Add some demo modes
        self.modes = {
            "default": Mode(
                mode_id="default",
                name="Default Mode",
                description="Standard operating mode"
            ),
            "calibration": Mode(
                mode_id="calibration",
                name="Calibration Mode",
                description="Device calibration mode"
            )
        }
        
        # Set up observers
        self.device.add_observer(self)
        for cmd in self.commands.values():
            cmd.add_observer(self)
        for mode in self.modes.values():
            mode.add_observer(self)
        
        # Create UI first
        self.setup_ui()
        
        # Then set up heartbeat timer
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.check_device_heartbeat)
        self.heartbeat_timer.start(1000)  # Check every second
        
    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create status bar first
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Header with logo and welcome message
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Logo container (25% width)
        logo_container = QWidget()
        logo_container.setFixedWidth(200)
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.setContentsMargins(10, 10, 10, 10)
        
        # Logo
        logo_label = QLabel()
        logo_label.setFixedSize(75, 75)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("QLabel { background-color: transparent; }")
        
        # Load logo from resources
        logo_svg = Path("resources/logo.svg")
        logo_png = Path("resources/Logo.png")  # Note the capital L
        
        if logo_png.exists():
            pixmap = QPixmap(str(logo_png))
            scaled_pixmap = pixmap.scaled(
                75, 75,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(scaled_pixmap)
        elif logo_svg.exists():
            try:
                pixmap = QPixmap(str(logo_svg))
                scaled_pixmap = pixmap.scaled(
                    75, 75,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                logo_label.setPixmap(scaled_pixmap)
            except:
                self.statusBar.showMessage("Error loading SVG logo")
                return
        else:
            self.statusBar.showMessage("Logo file not found")
            return
            
        logo_layout.addWidget(logo_label)
        
        # Welcome message container (75% width)
        welcome_container = QWidget()
        welcome_layout = QHBoxLayout(welcome_container)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        welcome_layout.setContentsMargins(20, 10, 10, 10)
        
        # Welcome message
        welcome_text = QLabel(
            "Welcome to the Layered Interaction System for User-Modes (LISU) \n"
            "Control VR visualisations, manipulate 3D models and navigate virtual environments"
        )
        welcome_text.setWordWrap(False)  # Prevent text wrapping
        welcome_font = QFont()
        welcome_font.setPointSize(11)
        welcome_font.setBold(True)
        welcome_text.setFont(welcome_font)
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        welcome_layout.addWidget(welcome_text)
        
        # Add containers to header layout
        header_layout.addWidget(logo_container)
        header_layout.addWidget(welcome_container, 1)  # 1 is stretch factor
        header_layout.setSpacing(0)  # Remove spacing between containers
        header_layout.setContentsMargins(0, 0, 0, 0)  # Remove container margins
        
        # Add header to main layout
        main_layout.addWidget(header_container)
        main_layout.addSpacing(10)
        
        # Device Selection and Configuration
        device_group = QGroupBox("Device Selection and Configuration")
        device_layout = QGridLayout()
        
        # Device Type Selection
        device_type_label = QLabel("Device Type:")
        self.device_type_combo = QComboBox()
        self.device_type_combo.addItems(["VR Controller", "Motion Platform", "Haptic Device"])
        device_layout.addWidget(device_type_label, 0, 0)
        device_layout.addWidget(self.device_type_combo, 0, 1)
        
        # UDP Configuration
        udp_label = QLabel("UDP Configuration:")
        self.udp_ip = QLineEdit("127.0.0.1")
        self.udp_port = QLineEdit("5000")
        device_layout.addWidget(udp_label, 1, 0)
        device_layout.addWidget(QLabel("IP:"), 1, 1)
        device_layout.addWidget(self.udp_ip, 1, 2)
        device_layout.addWidget(QLabel("Port:"), 1, 3)
        device_layout.addWidget(self.udp_port, 1, 4)
        
        # Connection Controls
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setIcon(qta.icon('fa5s.plug'))
        self.connect_btn.clicked.connect(self.connect_device)
        
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setIcon(qta.icon('fa5s.unlink'))
        self.disconnect_btn.clicked.connect(self.disconnect_device)
        
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.disconnect_btn)
        device_layout.addLayout(button_layout, 2, 0, 1, 5)
        
        device_group.setLayout(device_layout)
        main_layout.addWidget(device_group)
        
        # Control Section
        control_group = QGroupBox("Device Control")
        control_layout = QGridLayout()
        
        # Add control buttons with icons
        self.buttons = {}
        button_configs = [
            ("X-Axis Control", "fa5s.arrows-alt-h", self.control_x_axis),
            ("Y-Axis Control", "fa5s.arrows-alt-v", self.control_y_axis),
            ("Z-Axis Control", "fa5s.arrows-alt", self.control_z_axis),
            ("Reset Position", "fa5s.undo", self.reset_position),
            ("Calibrate", "fa5s.crosshairs", self.calibrate_device)
        ]
        
        for i, (text, icon, callback) in enumerate(button_configs):
            btn = QPushButton(text)
            btn.setIcon(qta.icon(icon))
            btn.setEnabled(False)
            btn.clicked.connect(callback)
            self.buttons[text] = btn
            control_layout.addWidget(btn, i // 2, i % 2)
            
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # Status Monitoring
        monitor_group = QGroupBox("Device Status")
        monitor_layout = QGridLayout()
        
        # Add monitoring labels
        self.status_labels = {}
        monitor_items = [
            ("Connection Status", "fa5s.plug"),
            ("Current Mode", "fa5s.cog"),
            ("Command Status", "fa5s.check-circle"),
            ("Error Count", "fa5s.exclamation-triangle")
        ]
        
        for i, (item, icon) in enumerate(monitor_items):
            # Create a horizontal layout for each status item
            item_layout = QHBoxLayout()
            
            # Create icon button
            icon_btn = QPushButton()
            icon_btn.setIcon(qta.icon(icon))
            icon_btn.setFixedSize(24, 24)
            icon_btn.setEnabled(False)  # Make it look like a label
            icon_btn.setStyleSheet("border: none;")
            
            # Create label
            label = QLabel(f"{item}:")
            value = QLabel("N/A")
            value.setStyleSheet("color: gray;")
            
            # Add widgets to horizontal layout
            item_layout.addWidget(icon_btn)
            item_layout.addWidget(label)
            item_layout.addWidget(value)
            item_layout.addStretch()
            
            # Add the layout to the grid
            monitor_layout.addLayout(item_layout, i, 0)
            self.status_labels[item] = value
        
        monitor_group.setLayout(monitor_layout)
        main_layout.addWidget(monitor_group)
        
        # Status Log
        log_group = QGroupBox("Status Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # Apply theme
        self.apply_theme()
        
    def apply_theme(self):
        """Apply the current system theme"""
        if darkdetect.isDark():
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    background-color: #3b3b3b;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #4b4b4b;
                    color: #ffffff;
                    border: 1px solid #5b5b5b;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #5b5b5b;
                }
                QPushButton:disabled {
                    background-color: #2b2b2b;
                    color: #666666;
                }
                QLabel {
                    color: #ffffff;
                }
                QTextEdit {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                QGroupBox {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: #000000;
                    border: 1px solid #cccccc;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QPushButton:disabled {
                    background-color: #f0f0f0;
                    color: #999999;
                }
                QLabel {
                    color: #000000;
                }
                QTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                }
            """)
            
    def connect_device(self):
        """Connect to the device"""
        try:
            # Update device with current UDP settings
            self.device.ip_address = self.udp_ip.text()
            self.device.port = int(self.udp_port.text())
            
            success = self.device.connect()
            if success:
                self.log_message("Device connected successfully")
                for btn in self.buttons.values():
                    btn.setEnabled(True)
                self.status_labels["Connection Status"].setText("Connected")
                self.status_labels["Connection Status"].setStyleSheet("color: green;")
            else:
                self.log_message(f"Failed to connect: {self.device.last_error}")
                self.status_labels["Connection Status"].setText("Connection Failed")
                self.status_labels["Connection Status"].setStyleSheet("color: red;")
        except Exception as e:
            self.log_message(f"Error connecting: {str(e)}")
            
    def disconnect_device(self):
        """Disconnect from the device"""
        try:
            self.device.disconnect()
            self.log_message("Device disconnected")
            for btn in self.buttons.values():
                btn.setEnabled(False)
            self.status_labels["Connection Status"].setText("Disconnected")
            self.status_labels["Connection Status"].setStyleSheet("color: red;")
        except Exception as e:
            self.log_message(f"Error disconnecting: {str(e)}")
            
    def control_x_axis(self):
        """Control X-axis"""
        try:
            success, result = self.commands["control_x"].execute(self.device, {"value": 1.0})
            if success:
                self.log_message("X-axis control activated")
            else:
                self.log_message(f"Failed to activate X-axis control: {result.get('error', 'Unknown error')}")
        except Exception as e:
            self.log_message(f"Error controlling X-axis: {str(e)}")
            
    def control_y_axis(self):
        """Control Y-axis"""
        try:
            success, result = self.commands["control_y"].execute(self.device, {"value": 1.0})
            if success:
                self.log_message("Y-axis control activated")
            else:
                self.log_message(f"Failed to activate Y-axis control: {result.get('error', 'Unknown error')}")
        except Exception as e:
            self.log_message(f"Error controlling Y-axis: {str(e)}")
            
    def control_z_axis(self):
        """Control Z-axis"""
        try:
            success, result = self.commands["control_z"].execute(self.device, {"value": 1.0})
            if success:
                self.log_message("Z-axis control activated")
            else:
                self.log_message(f"Failed to activate Z-axis control: {result.get('error', 'Unknown error')}")
        except Exception as e:
            self.log_message(f"Error controlling Z-axis: {str(e)}")
            
    def reset_position(self):
        """Reset device position"""
        try:
            success, result = self.commands["reset"].execute(self.device)
            if success:
                self.log_message("Position reset successful")
            else:
                self.log_message(f"Failed to reset position: {result.get('error', 'Unknown error')}")
        except Exception as e:
            self.log_message(f"Error resetting position: {str(e)}")
            
    def calibrate_device(self):
        """Calibrate device"""
        try:
            success, result = self.commands["calibrate"].execute(self.device)
            if success:
                self.log_message("Calibration successful")
            else:
                self.log_message(f"Failed to calibrate: {result.get('error', 'Unknown error')}")
        except Exception as e:
            self.log_message(f"Error calibrating device: {str(e)}")
            
    def check_device_heartbeat(self):
        """Check device connection status"""
        try:
            if hasattr(self, 'status_labels'):
                if self.device.check_connection():
                    self.status_labels["Connection Status"].setText("Connected")
                    self.status_labels["Connection Status"].setStyleSheet("color: green;")
                else:
                    self.status_labels["Connection Status"].setText("Disconnected")
                    self.status_labels["Connection Status"].setStyleSheet("color: red;")
                    
                # Update other status labels
                self.status_labels["Current Mode"].setText(self.device.current_mode or "None")
                self.status_labels["Command Status"].setText("Ready")
                self.status_labels["Error Count"].setText(str(self.device.error_count))
        except Exception as e:
            self.log_message(f"Error checking device heartbeat: {str(e)}")
            
    def log_message(self, message: str):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        
    # Observer methods
    def on_device_state_changed(self, device: Device):
        """Handle device state changes"""
        self.log_message(f"Device state changed: {device.status}")
        
    def on_command_executed(self, command: Command, status: str, result: dict):
        """Handle command execution status"""
        self.log_message(f"Command {command.name} {status}")
        if result and "error" in result:
            self.log_message(f"Error: {result['error']}")
            
    def on_mode_state_changed(self, mode: Mode, event: str, data: dict):
        """Handle mode state changes"""
        self.log_message(f"Mode {mode.name} {event}")
        if data:
            self.log_message(f"Details: {data}") 