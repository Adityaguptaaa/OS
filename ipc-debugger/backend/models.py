from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    simulations = db.relationship('Simulation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }


class Simulation(db.Model):
    """Simulation session model"""
    __tablename__ = 'simulations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='created')  # created, running, stopped, completed
    started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    config = db.Column(db.Text, default='{}')  # JSON config
    
    # Relationships
    processes = db.relationship('Process', backref='simulation', lazy=True, cascade='all, delete-orphan')
    ipc_channels = db.relationship('IPCChannel', backref='simulation', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('Event', backref='simulation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'config': json.loads(self.config) if self.config else {},
            'process_count': len(self.processes),
            'channel_count': len(self.ipc_channels)
        }


class Process(db.Model):
    """Process model"""
    __tablename__ = 'processes'
    
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=False)
    process_name = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(20), default='ready')  # ready, running, waiting, blocked, terminated
    priority = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sent_channels = db.relationship('IPCChannel', foreign_keys='IPCChannel.sender_id', backref='sender', lazy=True)
    received_channels = db.relationship('IPCChannel', foreign_keys='IPCChannel.receiver_id', backref='receiver', lazy=True)
    events = db.relationship('Event', backref='process', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'simulation_id': self.simulation_id,
            'process_name': self.process_name,
            'state': self.state,
            'priority': self.priority,
            'created_at': self.created_at.isoformat()
        }


class IPCChannel(db.Model):
    """IPC Channel model"""
    __tablename__ = 'ipc_channels'
    
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=False)
    ipc_type = db.Column(db.String(20), nullable=False)  # pipe, queue, shmem
    sender_id = db.Column(db.Integer, db.ForeignKey('processes.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('processes.id'), nullable=False)
    config = db.Column(db.Text, default='{}')  # JSON config (buffer size, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='channel', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'simulation_id': self.simulation_id,
            'ipc_type': self.ipc_type,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'sender_name': self.sender.process_name if self.sender else None,
            'receiver_name': self.receiver.process_name if self.receiver else None,
            'config': json.loads(self.config) if self.config else {},
            'message_count': len(self.messages)
        }


class Message(db.Model):
    """Message model"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('ipc_channels.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    size_bytes = db.Column(db.Integer, default=0)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    received_at = db.Column(db.DateTime, nullable=True)
    delay_ms = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'content': self.content,
            'size_bytes': self.size_bytes,
            'sent_at': self.sent_at.isoformat(),
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'delay_ms': self.delay_ms
        }


class Event(db.Model):
    """Event/Log model"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=False)
    process_id = db.Column(db.Integer, db.ForeignKey('processes.id'), nullable=True)
    event_type = db.Column(db.String(50), nullable=False)  # process_created, message_sent, deadlock, etc.
    severity = db.Column(db.String(20), default='info')  # info, warning, error, debug
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event_metadata = db.Column(db.Text, default='{}')  # JSON metadata
    
    def to_dict(self):
        return {
            'id': self.id,
            'simulation_id': self.simulation_id,
            'process_id': self.process_id,
            'event_type': self.event_type,
            'severity': self.severity,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'metadata': json.loads(self.event_metadata) if self.event_metadata else {}
        }
