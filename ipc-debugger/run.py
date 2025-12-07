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

from backend.app import app, socketio

# Export app for gunicorn
# Gunicorn will use: gunicorn run:app
app = socketio  # For gunicorn with eventlet worker

if __name__ == '__main__':
    # Development mode only
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting in DEVELOPMENT mode on port {port}")
    socketio.run(app, debug=True, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
