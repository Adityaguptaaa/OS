# IPC Debugger - Inter-Process Communication Debugging Tool

A comprehensive web-based tool for simulating, visualizing, and debugging inter-process communication mechanisms.

## 🚀 Features

- **IPC Simulation**: Simulate Pipes, Message Queues, and Shared Memory
- **Real-Time Visualization**: Interactive canvas-based process graphs with animated message flow
- **Deadlock Detection**: Automatic detection of circular wait conditions
- **Bottleneck Analysis**: Identify slow processes and communication channels
- **Comprehensive Logging**: Detailed event logs with filtering and export
- **Statistics Dashboard**: Real-time charts showing latency, throughput, and resource usage

## 📋 Requirements

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Edge, Safari)

## 🛠️ Installation

1. **Clone or download the project**
   ```bash
   cd ipc-debugger
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

4. **Access the application**
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## 📖 Usage Guide

### 1. Create a Simulation
- Navigate to the Dashboard
- Click "New Simulation"
- Enter a simulation name

### 2. Add Processes
- Click "Add Process"
- Enter process name and priority
- Repeat to create multiple processes

### 3. Configure IPC Channels
- Select IPC type (Pipe, Queue, or Shared Memory)
- Choose sender and receiver processes
- Click "Create Channel"

### 4. Start Simulation
- Click "Start Simulation"
- Navigate to Visualization page to see real-time process communication

### 5. Send Messages
- Select a channel
- Enter message content
- Click "Send" to transfer data

### 6. Analyze Results
- View real-time visualization on the Visualization page
- Check logs on the Logs page
- Export data for further analysis

## 🏗️ Project Structure

```
ipc-debugger/
├── backend/
│   ├── app.py                 # Flask application
│   ├── config.py              # Configuration
│   ├── models.py              # Database models
│   ├── routes/
│   │   └── api.py            # REST API endpoints
│   └── services/
│       ├── ipc_simulator.py  # IPC simulation logic
│       ├── deadlock_detector.py
│       └── bottleneck_analyzer.py
├── frontend/
│   ├── index.html            # Landing page
│   ├── dashboard.html        # Main dashboard
│   ├── visualization.html    # Real-time visualization
│   ├── logs.html             # Event logs
│   ├── css/                  # Stylesheets
│   └── js/                   # JavaScript files
├── requirements.txt          # Python dependencies
└── run.py                    # Application launcher
```

## 🔧 API Endpoints

### Simulation
- `POST /api/simulation/create` - Create simulation
- `GET /api/simulation/<id>` - Get simulation details
- `POST /api/simulation/start` - Start simulation
- `POST /api/simulation/stop` - Stop simulation

### Process
- `POST /api/process/create` - Create process
- `PUT /api/process/<id>/state` - Update process state
- `DELETE /api/process/<id>` - Delete process

### IPC
- `POST /api/ipc/create` - Create IPC channel
- `POST /api/ipc/send` - Send message

### Analysis
- `GET /api/deadlock/detect/<sim_id>` - Detect deadlocks
- `GET /api/bottleneck/analyze/<sim_id>` - Analyze bottlenecks
- `GET /api/statistics/<sim_id>` - Get statistics
- `GET /api/events/<sim_id>` - Get event logs

## 🎨 Technology Stack

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- Chart.js for data visualization
- WebSocket for real-time updates
- Canvas API for process visualization

**Backend:**
- Python 3.8+
- Flask web framework
- Flask-SocketIO for WebSocket
- SQLAlchemy ORM
- SQLite database

## 🧪 Testing

1. **Create Test Simulation**
   - Add 3 processes (P1, P2, P3)
   - Create pipe channel: P1 → P2
   - Create queue channel: P2 → P3
   - Start simulation

2. **Test Message Transfer**
   - Send messages through channels
   - Verify visualization updates
   - Check logs for events

3. **Test Deadlock Detection**
   - Create circular dependencies
   - Click "Detect Deadlock"
   - Verify alert appears

4. **Test Bottleneck Analysis**
   - Send multiple messages
   - Click "Analyze Bottleneck"
   - Check for performance warnings

## 📊 Features Explained

### IPC Mechanisms

**Pipes**
- Unidirectional FIFO communication
- Delay: 100-300ms
- Best for simple parent-child communication

**Message Queues**
- Bidirectional, priority-based
- Delay: 200-500ms
- Best for complex multi-process systems

**Shared Memory**
- Direct memory access
- Delay: 50-150ms (fastest)
- Requires synchronization

### Deadlock Detection
Uses Resource Allocation Graph (RAG) with DFS cycle detection to identify circular wait conditions.

### Bottleneck Analysis
Monitors communication delays and identifies processes with average latency > 500ms.

## 🐛 Troubleshooting

**Issue: Port 5000 already in use**
- Solution: Change port in `backend/app.py` or stop the conflicting process

**Issue: Database errors**
- Solution: Delete `backend/database/ipc_debugger.db` and restart

**Issue: WebSocket not connecting**
- Solution: Check if Flask-SocketIO is installed and server is running

## 📝 License

This is an educational project for Operating Systems coursework.

## 👥 Contributors

Operating Systems Project Team

## 📧 Contact

For questions or support, visit the Contact page in the application.

---

**Happy Debugging! 🔍**
