#!/usr/bin/env python3
"""
IPC Debugger - Development Server Launcher
Run this file to start the application
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.app import app, socketio

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
