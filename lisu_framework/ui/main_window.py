"""
LISU Framework Ontology UI
Main window implementation.
"""

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

from lisu_framework.device import Device
from lisu_framework.command import Command
from lisu_framework.mode import Mode

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
        logo_svg = Path(__file__).parent.parent / "resources/logo.svg"
        logo_png = Path(__file__).parent.parent / "resources/Logo.png"
        
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
            "Welcome to the Layered Interaction System for User-Modes (LISU) - "
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
        
        for i, (label, icon, callback) in enumerate(button_configs):
            btn = QPushButton(label)
            btn.setIcon(qta.icon(icon))
            btn.clicked.connect(callback)
            self.buttons[label] = btn
            control_layout.addWidget(btn, i // 2, i % 2)
        
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # Status Section
        status_group = QGroupBox("Device Status")
        status_layout = QGridLayout()
        
        # Status indicators with icons
        status_items = [
            ("Connection Status:", "Disconnected", "fa5s.plug", Qt.GlobalColor.red),
            ("Current Mode:", "None", "fa5s.cog", Qt.GlobalColor.gray),
            ("Command Status:", "Ready", "fa5s.terminal", Qt.GlobalColor.green),
            ("Error Count:", "0", "fa5s.exclamation-triangle", Qt.GlobalColor.yellow)
        ]
        
        self.status_labels = {}
        for i, (label, initial_value, icon, color) in enumerate(status_items):
            # Create horizontal layout for each status item
            item_layout = QHBoxLayout()
            
            # Icon
            icon_btn = QPushButton()
            icon_btn.setIcon(qta.icon(icon, color=color))
            icon_btn.setFixedSize(24, 24)
            icon_btn.setEnabled(False)
            icon_btn.setStyleSheet("QPushButton { border: none; }")
            item_layout.addWidget(icon_btn)
            
            # Label
            label_widget = QLabel(label)
            item_layout.addWidget(label_widget)
            
            # Value
            value_label = QLabel(initial_value)
            value_label.setStyleSheet(f"color: {color.name}")
            self.status_labels[label] = value_label
            item_layout.addWidget(value_label)
            
            # Add to grid
            status_layout.addLayout(item_layout, i, 0)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # Status Log
        log_group = QGroupBox("Status Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # Apply theme based on system settings
        self.apply_theme()

    def apply_theme(self):
        """Apply dark/light theme based on system settings."""
        if darkdetect.isDark():
            # Dark theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid #404040;
                    border-radius: 5px;
                    margin-top: 1em;
                    padding-top: 1em;
                    color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #404040;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QPushButton:pressed {
                    background-color: #353535;
                }
                QComboBox {
                    background-color: #404040;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    color: #ffffff;
                }
                QLineEdit {
                    background-color: #404040;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    color: #ffffff;
                }
                QTextEdit {
                    background-color: #404040;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                    color: #ffffff;
                }
            """)
        else:
            # Light theme
            self.setStyleSheet("")

    def connect_device(self):
        """Handle device connection."""
        try:
            ip = self.udp_ip.text()
            port = int(self.udp_port.text())
            self.device.ip_address = ip
            self.device.port = port
            
            # Execute connect command
            cmd = self.commands["connect"]
            cmd.execute()
            
            self.status_labels["Connection Status:"].setText("Connected")
            self.status_labels["Connection Status:"].setStyleSheet("color: green")
            self.log_message(f"Connected to device at {ip}:{port}")
            
        except Exception as e:
            self.log_message(f"Connection failed: {str(e)}")
            self.status_labels["Connection Status:"].setText("Error")
            self.status_labels["Connection Status:"].setStyleSheet("color: red")

    def disconnect_device(self):
        """Handle device disconnection."""
        try:
            # Execute disconnect command
            cmd = self.commands["disconnect"]
            cmd.execute()
            
            self.status_labels["Connection Status:"].setText("Disconnected")
            self.status_labels["Connection Status:"].setStyleSheet("color: red")
            self.log_message("Disconnected from device")
            
        except Exception as e:
            self.log_message(f"Disconnection failed: {str(e)}")

    def control_x_axis(self):
        """Handle X-axis control."""
        try:
            cmd = self.commands["control_x"]
            cmd.execute()
            self.log_message("X-axis control command sent")
        except Exception as e:
            self.log_message(f"X-axis control failed: {str(e)}")

    def control_y_axis(self):
        """Handle Y-axis control."""
        try:
            cmd = self.commands["control_y"]
            cmd.execute()
            self.log_message("Y-axis control command sent")
        except Exception as e:
            self.log_message(f"Y-axis control failed: {str(e)}")

    def control_z_axis(self):
        """Handle Z-axis control."""
        try:
            cmd = self.commands["control_z"]
            cmd.execute()
            self.log_message("Z-axis control command sent")
        except Exception as e:
            self.log_message(f"Z-axis control failed: {str(e)}")

    def reset_position(self):
        """Handle position reset."""
        try:
            cmd = self.commands["reset"]
            cmd.execute()
            self.log_message("Reset position command sent")
        except Exception as e:
            self.log_message(f"Reset position failed: {str(e)}")

    def calibrate_device(self):
        """Handle device calibration."""
        try:
            cmd = self.commands["calibrate"]
            cmd.execute()
            self.log_message("Calibration command sent")
        except Exception as e:
            self.log_message(f"Calibration failed: {str(e)}")

    def check_device_heartbeat(self):
        """Check device heartbeat and update status."""
        try:
            # Simulate heartbeat check
            if self.status_labels["Connection Status:"].text() == "Connected":
                self.device.last_heartbeat = time.time()
                self.statusBar.showMessage("Device heartbeat OK", 2000)
        except Exception as e:
            self.log_message(f"Heartbeat check failed: {str(e)}")

    def log_message(self, message: str):
        """Add a message to the status log."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.statusBar.showMessage(message, 3000)

    def on_device_state_changed(self, device: Device):
        """Handle device state changes."""
        self.log_message(f"Device state changed: {device.state}")

    def on_command_executed(self, command: Command, status: str, result: dict):
        """Handle command execution results."""
        self.log_message(f"Command '{command.name}' executed with status: {status}")
        self.status_labels["Command Status:"].setText(status)

    def on_mode_state_changed(self, mode: Mode, event: str, data: dict):
        """Handle mode state changes."""
        self.log_message(f"Mode '{mode.name}' state changed: {event}")
        self.status_labels["Current Mode:"].setText(mode.name) 