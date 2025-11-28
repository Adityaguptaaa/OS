from flask import Blueprint, request, jsonify, current_app
from backend.models import db, Simulation, Process, IPCChannel, Message, Event, User
from backend.services.ipc_simulator import IPCSimulator
from backend.services.deadlock_detector import DeadlockDetector
from backend.services.bottleneck_analyzer import BottleneckAnalyzer
from backend.config import Config
from datetime import datetime
import json

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Get socketio instance
def get_socketio():
    """Get socketio instance from app"""
    from flask import current_app
    return current_app.extensions.get('socketio')

# Global instances (in production, use app context)
simulators = {}
deadlock_detectors = {}
bottleneck_analyzers = {}

def get_simulator(simulation_id):
    """Get or create simulator for a simulation"""
    if simulation_id not in simulators:
        simulators[simulation_id] = IPCSimulator(Config())
    return simulators[simulation_id]

def get_deadlock_detector(simulation_id):
    """Get or create deadlock detector"""
    if simulation_id not in deadlock_detectors:
        deadlock_detectors[simulation_id] = DeadlockDetector()
    return deadlock_detectors[simulation_id]

def get_bottleneck_analyzer(simulation_id, threshold=500):
    """Get or create bottleneck analyzer"""
    if simulation_id not in bottleneck_analyzers:
        bottleneck_analyzers[simulation_id] = BottleneckAnalyzer(threshold)
    return bottleneck_analyzers[simulation_id]


# ============= Simulation Endpoints =============

@api_bp.route('/simulation/create', methods=['POST'])
def create_simulation():
    """Create a new simulation"""
    data = request.json
    name = data.get('name', f'Simulation {datetime.now().strftime("%Y%m%d_%H%M%S")}')
    config = data.get('config', {})
    user_id = data.get('user_id')  # Optional for now
    
    simulation = Simulation(
        name=name,
        user_id=user_id,
        config=json.dumps(config),
        status='created'
    )
    
    db.session.add(simulation)
    db.session.commit()
    
    # Log event
    event = Event(
        simulation_id=simulation.id,
        event_type='simulation_created',
        severity='info',
        message=f'Simulation "{name}" created'
    )
    db.session.add(event)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'simulation': simulation.to_dict()
    }), 201


@api_bp.route('/simulation/<int:sim_id>', methods=['GET'])
def get_simulation(sim_id):
    """Get simulation details"""
    simulation = Simulation.query.get_or_404(sim_id)
    
    return jsonify({
        'success': True,
        'simulation': simulation.to_dict(),
        'processes': [p.to_dict() for p in simulation.processes],
        'channels': [c.to_dict() for c in simulation.ipc_channels]
    })


@api_bp.route('/simulation/<int:sim_id>', methods=['DELETE'])
def delete_simulation(sim_id):
    """Delete a simulation"""
    simulation = Simulation.query.get_or_404(sim_id)
    
    # Clean up global instances
    if sim_id in simulators:
        del simulators[sim_id]
    if sim_id in deadlock_detectors:
        del deadlock_detectors[sim_id]
    if sim_id in bottleneck_analyzers:
        del bottleneck_analyzers[sim_id]
    
    db.session.delete(simulation)
    db.session.commit()
    
    return jsonify({'success': True})


@api_bp.route('/simulation/start', methods=['POST'])
def start_simulation():
    """Start a simulation"""
    data = request.json
    sim_id = data.get('simulation_id')
    
    simulation = Simulation.query.get_or_404(sim_id)
    simulation.status = 'running'
    simulation.started_at = datetime.utcnow()
    
    db.session.commit()
    
    # Log event
    event = Event(
        simulation_id=sim_id,
        event_type='simulation_started',
        severity='info',
        message='Simulation started'
    )
    db.session.add(event)
    db.session.commit()
    
    return jsonify({'success': True, 'status': 'running'})


@api_bp.route('/simulation/stop', methods=['POST'])
def stop_simulation():
    """Stop a simulation"""
    data = request.json
    sim_id = data.get('simulation_id')
    
    simulation = Simulation.query.get_or_404(sim_id)
    simulation.status = 'stopped'
    simulation.ended_at = datetime.utcnow()
    
    db.session.commit()
    
    # Log event
    event = Event(
        simulation_id=sim_id,
        event_type='simulation_stopped',
        severity='info',
        message='Simulation stopped'
    )
    db.session.add(event)
    db.session.commit()
    
    return jsonify({'success': True, 'status': 'stopped'})


# ============= Process Endpoints =============

@api_bp.route('/process/create', methods=['POST'])
def create_process():
    """Create a new process"""
    data = request.json
    sim_id = data.get('simulation_id')
    name = data.get('name', f'Process_{datetime.now().strftime("%H%M%S")}')
    priority = data.get('priority', 0)
    
    process = Process(
        simulation_id=sim_id,
        process_name=name,
        priority=priority,
        state='ready'
    )
    
    db.session.add(process)
    db.session.commit()
    
    # Log event
    event = Event(
        simulation_id=sim_id,
        process_id=process.id,
        event_type='process_created',
        severity='info',
        message=f'Process "{name}" created'
    )
    db.session.add(event)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'process': process.to_dict()
    }), 201


@api_bp.route('/process/<int:proc_id>/state', methods=['PUT'])
def update_process_state(proc_id):
    """Update process state"""
    data = request.json
    new_state = data.get('state')
    
    process = Process.query.get_or_404(proc_id)
    old_state = process.state
    process.state = new_state
    
    db.session.commit()
    
    # Log event
    event = Event(
        simulation_id=process.simulation_id,
        process_id=proc_id,
        event_type='process_state_changed',
        severity='info',
        message=f'Process "{process.process_name}" state: {old_state} → {new_state}'
    )
    db.session.add(event)
    db.session.commit()
    
    # Emit WebSocket event for real-time visualization
    socketio = get_socketio()
    if socketio:
        socketio.emit('process_state_changed', {
            'process_id': proc_id,
            'state': new_state,
            'process_name': process.process_name
        }, room=f'simulation_{process.simulation_id}')
    
    return jsonify({
        'success': True,
        'process_id': proc_id,
        'new_state': new_state
    })


@api_bp.route('/process/<int:proc_id>', methods=['DELETE'])
def delete_process(proc_id):
    """Delete a process and all associated channels"""
    process = Process.query.get_or_404(proc_id)
    sim_id = process.simulation_id
    process_name = process.process_name
    
    # Find and delete all channels where this process is sender or receiver
    channels_to_delete = IPCChannel.query.filter(
        (IPCChannel.sender_id == proc_id) | (IPCChannel.receiver_id == proc_id)
    ).all()
    
    channel_count = len(channels_to_delete)
    
    # Delete all associated channels
    for channel in channels_to_delete:
        db.session.delete(channel)
    
    # Delete the process
    db.session.delete(process)
    db.session.commit()
    
    # Log event
    message = f'Process "{process_name}" deleted'
    if channel_count > 0:
        message += f' (and {channel_count} associated channel{"s" if channel_count > 1 else ""})'
    
    event = Event(
        simulation_id=sim_id,
        event_type='process_deleted',
        severity='info',
        message=message
    )
    db.session.add(event)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'deleted_channels': channel_count
    })


# ============= IPC Channel Endpoints =============

@api_bp.route('/ipc/create', methods=['POST'])
def create_ipc_channel():
    """Create an IPC channel"""
    data = request.json
    sim_id = data.get('simulation_id')
    ipc_type = data.get('type')  # pipe, queue, shmem
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    config = data.get('config', {})
    
    channel = IPCChannel(
        simulation_id=sim_id,
        ipc_type=ipc_type,
        sender_id=sender_id,
        receiver_id=receiver_id,
        config=json.dumps(config)
    )
    
    db.session.add(channel)
    db.session.commit()
    
    # Log event
    sender = Process.query.get(sender_id)
    receiver = Process.query.get(receiver_id)
    event = Event(
        simulation_id=sim_id,
        event_type='channel_created',
        severity='info',
        message=f'{ipc_type.upper()} channel: {sender.process_name} → {receiver.process_name}'
    )
    db.session.add(event)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'channel': channel.to_dict()
    }), 201


@api_bp.route('/ipc/<int:channel_id>', methods=['DELETE'])
def delete_ipc_channel(channel_id):
    """Delete an IPC channel"""
    channel = IPCChannel.query.get_or_404(channel_id)
    sim_id = channel.simulation_id
    
    db.session.delete(channel)
    db.session.commit()
    
    # Log event
    event = Event(
        simulation_id=sim_id,
        event_type='channel_deleted',
        severity='info',
        message=f'IPC channel deleted'
    )
    db.session.add(event)
    db.session.commit()
    
    return jsonify({'success': True})



@api_bp.route('/ipc/send', methods=['POST'])
def send_message():
    """Send a message through IPC channel"""
    data = request.json
    channel_id = data.get('channel_id')
    content = data.get('content', '')
    
    channel = IPCChannel.query.get_or_404(channel_id)
    channel_config = json.loads(channel.config) if channel.config else {}
    
    # Get simulator
    simulator = get_simulator(channel.simulation_id)
    
    # Simulate message transfer
    success, delay_ms, info = simulator.send_message(
        channel.ipc_type,
        content,
        channel_config
    )
    
    if not success:
        return jsonify({
            'success': False,
            'error': info
        }), 400
    
    # Create message record
    message = Message(
        channel_id=channel_id,
        content=content,
        size_bytes=len(content.encode('utf-8')),
        delay_ms=delay_ms
    )
    
    db.session.add(message)
    db.session.commit()
    
    # Update process states
    sender = channel.sender
    receiver = channel.receiver
    sender.state = 'running'
    receiver.state = 'waiting'
    db.session.commit()
    
    # Record for bottleneck analysis
    analyzer = get_bottleneck_analyzer(channel.simulation_id)
    analyzer.record_delay(sender.id, channel_id, delay_ms)
    analyzer.record_delay(receiver.id, channel_id, delay_ms)
    
    # Log event
    event = Event(
        simulation_id=channel.simulation_id,
        process_id=sender.id,
        event_type='message_sent',
        severity='info',
        message=f'{sender.process_name} → {receiver.process_name} ({delay_ms}ms)',
        event_metadata=json.dumps({'channel_id': channel_id, 'delay': delay_ms})
    )
    db.session.add(event)
    db.session.commit()
    
    # Emit WebSocket event for real-time visualization
    socketio = get_socketio()
    if socketio:
        socketio.emit('message_sent', {
            'simulation_id': channel.simulation_id,
            'sender_id': sender.id,
            'receiver_id': receiver.id,
            'sender': sender.process_name,
            'receiver': receiver.process_name,
            'channel_id': channel_id,
            'delay_ms': delay_ms,
            'ipc_type': channel.ipc_type
        }, room=f'simulation_{channel.simulation_id}')
    
    return jsonify({
        'success': True,
        'message_id': message.id,
        'delay_ms': delay_ms,
        'info': info
    })


# ============= Event/Log Endpoints =============

@api_bp.route('/events/<int:sim_id>', methods=['GET'])
def get_events(sim_id):
    """Get simulation events"""
    severity = request.args.get('severity')
    event_type = request.args.get('type')
    limit = request.args.get('limit', 100, type=int)
    
    query = Event.query.filter_by(simulation_id=sim_id)
    
    if severity:
        query = query.filter_by(severity=severity)
    if event_type:
        query = query.filter_by(event_type=event_type)
    
    events = query.order_by(Event.timestamp.desc()).limit(limit).all()
    
    return jsonify({
        'success': True,
        'events': [e.to_dict() for e in events]
    })


# ============= Statistics Endpoints =============

@api_bp.route('/statistics/<int:sim_id>', methods=['GET'])
def get_statistics(sim_id):
    """Get simulation statistics"""
    simulation = Simulation.query.get_or_404(sim_id)
    
    # Count messages
    total_messages = db.session.query(Message).join(IPCChannel).filter(
        IPCChannel.simulation_id == sim_id
    ).count()
    
    # Calculate average latency
    avg_latency = db.session.query(db.func.avg(Message.delay_ms)).join(IPCChannel).filter(
        IPCChannel.simulation_id == sim_id
    ).scalar() or 0
    
    # Count deadlocks
    deadlock_count = Event.query.filter_by(
        simulation_id=sim_id,
        event_type='deadlock_detected'
    ).count()
    
    # IPC type distribution
    ipc_distribution = {}
    for channel in simulation.ipc_channels:
        ipc_type = channel.ipc_type
        ipc_distribution[ipc_type] = ipc_distribution.get(ipc_type, 0) + 1
    
    return jsonify({
        'success': True,
        'statistics': {
            'total_processes': len(simulation.processes),
            'total_channels': len(simulation.ipc_channels),
            'total_messages': total_messages,
            'avg_latency_ms': round(avg_latency, 2),
            'deadlock_count': deadlock_count,
            'ipc_distribution': ipc_distribution
        }
    })


# ============= Deadlock Detection =============

@api_bp.route('/deadlock/detect/<int:sim_id>', methods=['GET'])
def detect_deadlock(sim_id):
    """Detect deadlocks in simulation based on channel structure"""
    simulation = Simulation.query.get_or_404(sim_id)
    detector = get_deadlock_detector(sim_id)
    
    # Reset detector state
    detector.reset()
    
    # Build dependency graph from channels
    # Each channel represents: sender waits for receiver to consume
    for channel in simulation.ipc_channels:
        # Model as: sender process waits for the channel (resource)
        # and the channel is held by the receiver process
        detector.add_wait(channel.sender_id, channel.id)
        detector.add_hold(channel.receiver_id, channel.id)
    
    # Analyze for deadlock
    result = detector.analyze_deadlock(simulation.processes)
    
    # Log if deadlock found
    if result['deadlock_found']:
        event = Event(
            simulation_id=sim_id,
            event_type='deadlock_detected',
            severity='error',
            message=f'Deadlock detected: {", ".join(result["cycle"])}',
            event_metadata=json.dumps(result)
        )
        db.session.add(event)
        db.session.commit()
    
    return jsonify({
        'success': True,
        **result
    })


# ============= Bottleneck Analysis =============

@api_bp.route('/bottleneck/analyze/<int:sim_id>', methods=['GET'])
def analyze_bottleneck(sim_id):
    """Analyze bottlenecks in simulation"""
    simulation = Simulation.query.get_or_404(sim_id)
    analyzer = get_bottleneck_analyzer(sim_id)
    
    process_analysis = analyzer.analyze_processes(simulation.processes)
    channel_analysis = analyzer.analyze_channels(simulation.ipc_channels)
    
    bottlenecks = [p for p in process_analysis if p['is_bottleneck']]
    suggestions = analyzer.get_suggestions(bottlenecks)
    
    # Log bottlenecks
    for bottleneck in bottlenecks:
        event = Event(
            simulation_id=sim_id,
            process_id=bottleneck['process_id'],
            event_type='bottleneck_detected',
            severity='warning',
            message=f'Bottleneck: {bottleneck["process_name"]} ({bottleneck["avg_delay"]}ms avg)'
        )
        db.session.add(event)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'process_analysis': process_analysis,
        'channel_analysis': channel_analysis,
        'suggestions': suggestions
    })


# ============= Export Endpoints =============

@api_bp.route('/export/logs/<int:sim_id>', methods=['GET'])
def export_logs(sim_id):
    """Export logs as JSON"""
    format_type = request.args.get('format', 'json')
    
    events = Event.query.filter_by(simulation_id=sim_id).order_by(Event.timestamp).all()
    
    if format_type == 'json':
        return jsonify({
            'simulation_id': sim_id,
            'exported_at': datetime.utcnow().isoformat(),
            'events': [e.to_dict() for e in events]
        })
    
    # CSV format
    elif format_type == 'csv':
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Timestamp', 'Type', 'Severity', 'Message', 'Process ID'])
        
        for event in events:
            writer.writerow([
                event.id,
                event.timestamp.isoformat(),
                event.event_type,
                event.severity,
                event.message,
                event.process_id or ''
            ])
        
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=simulation_{sim_id}_logs.csv'
        }
