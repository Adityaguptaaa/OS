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
    # Get port from environment variable (Render provides this)
    port = int(os.environ.get('PORT', 5000))
    
    # Detect if running in production
    is_production = os.environ.get('RENDER') or os.environ.get('RAILWAY_ENVIRONMENT')
    
    if is_production:
        # Production settings
        print(f"Starting in PRODUCTION mode on port {port}")
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
    else:
        # Development settings
        print(f"Starting in DEVELOPMENT mode on port {port}")
        socketio.run(app, debug=True, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
