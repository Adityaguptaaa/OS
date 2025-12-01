from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
from backend.config import Config
from backend.models import db
from backend.routes.api import api_bp
import os

# Initialize Flask app
app = Flask(__name__, 
            static_folder='../frontend',
            static_url_path='')
app.config.from_object(Config)

# Initialize extensions
CORS(app)
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Register blueprints
app.register_blueprint(api_bp)

# Create database tables
with app.app_context():
    db.create_all()
    print("Database initialized!")


# ============= WebSocket Events =============

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')


@socketio.on('join_simulation')
def handle_join_simulation(data):
    """Join a simulation room for real-time updates"""
    simulation_id = data.get('simulation_id')
    join_room(f'simulation_{simulation_id}')
    emit('joined_simulation', {'simulation_id': simulation_id})
    print(f'Client joined simulation {simulation_id}')


@socketio.on('process_state_update')
def handle_process_state_update(data):
    """Broadcast process state changes"""
    simulation_id = data.get('simulation_id')
    process_id = data.get('process_id')
    state = data.get('state')
    
    socketio.emit('process_state_changed', {
        'process_id': process_id,
        'state': state
    }, room=f'simulation_{simulation_id}')


@socketio.on('message_sent_event')
def handle_message_sent(data):
    """Broadcast message sent events"""
    simulation_id = data.get('simulation_id')
    
    socketio.emit('message_sent', data, room=f'simulation_{simulation_id}')


@socketio.on('deadlock_alert')
def handle_deadlock_alert(data):
    """Broadcast deadlock detection"""
    simulation_id = data.get('simulation_id')
    
    socketio.emit('deadlock_detected', data, room=f'simulation_{simulation_id}')


@socketio.on('bottleneck_alert')
def handle_bottleneck_alert(data):
    """Broadcast bottleneck detection"""
    simulation_id = data.get('simulation_id')
    
    socketio.emit('bottleneck_detected', data, room=f'simulation_{simulation_id}')


# ============= Frontend Routes =============

@app.route('/')
def index():
    """Serve landing page"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # For client-side routing, return index.html
    return send_from_directory(app.static_folder, 'index.html')


# ============= Helper Functions =============

def broadcast_simulation_update(simulation_id, data):
    """Helper to broadcast simulation updates"""
    socketio.emit('simulation_update', data, room=f'simulation_{simulation_id}')


# ============= Run Application =============

if __name__ == '__main__':
    print("=" * 50)
    print("IPC Debugger Server Starting...")
    print("=" * 50)
    print(f"Frontend: http://localhost:5000")
    print(f"API: http://localhost:5000/api")
    print("=" * 50)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
