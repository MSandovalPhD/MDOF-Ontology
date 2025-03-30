#!/usr/bin/env python3
"""
LISU Framework Ontology UI
Main entry point for the application.
"""

import sys
from PyQt6.QtWidgets import QApplication
from lisu_framework.ui import MainWindow

def main():
    """Main entry point for the LISU Framework UI."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 