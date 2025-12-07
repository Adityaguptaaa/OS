#!/usr/bin/env python3
"""
IPC Debugger - Application Entry Point
For production: gunicorn uses this to import the app
For development: run this file directly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.app import app as flask_app, socketio

# Export the Flask app wrapped by SocketIO for gunicorn
# Gunicorn command: gunicorn --worker-class eventlet -w 1 run:app
app = flask_app

if __name__ == '__main__':
    # Development mode only
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting in DEVELOPMENT mode on port {port}")
    socketio.run(flask_app, debug=True, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
