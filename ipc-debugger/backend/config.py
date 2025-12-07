import os

class Config:
    """Application configuration"""
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database directory - ensure it exists
    DB_DIR = os.path.join(BASE_DIR, "database")
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(DB_DIR, "ipc_debugger.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # CORS settings
    CORS_HEADERS = 'Content-Type'
    
    # SocketIO settings
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    
    # Simulation settings
    MAX_PROCESSES = 10
    MAX_MESSAGE_SIZE = 1024 * 10  # 10KB
    DEFAULT_PIPE_DELAY = (100, 300)  # ms
    DEFAULT_QUEUE_DELAY = (200, 500)  # ms
    DEFAULT_SHMEM_DELAY = (50, 150)  # ms
    DEADLOCK_CHECK_INTERVAL = 500  # ms
    BOTTLENECK_THRESHOLD = 500  # ms
    
    # Admin credentials (simple auth for demo)
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'  # Change in production
