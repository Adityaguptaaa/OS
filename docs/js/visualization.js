// Visualization JavaScript

let canvas, ctx;
let processes = [];
let channels = [];
let messages = [];
let socket;
let currentSimulationId;

// Charts
let timelineChart, latencyChart, ipcDistChart;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initCanvas();
    initCharts();
    initWebSocket();
    loadSimulationData();
    setupEventListeners();
    startAnimation();
});

function setupEventListeners() {
    document.getElementById('detectDeadlockBtn').addEventListener('click', detectDeadlock);
    document.getElementById('analyzeBottleneckBtn').addEventListener('click', analyzeBottleneck);
}

// Initialize canvas
function initCanvas() {
    canvas = document.getElementById('processCanvas');
    ctx = canvas.getContext('2d');
}

// Initialize charts
function initCharts() {
    // Timeline Chart
    const timelineCtx = document.getElementById('timelineChart').getContext('2d');
    timelineChart = new Chart(timelineCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Messages',
                data: [],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Latency Chart
    const latencyCtx = document.getElementById('latencyChart').getContext('2d');
    latencyChart = new Chart(latencyCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Avg Latency (ms)',
                data: [],
                backgroundColor: '#8b5cf6'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            }
        }
    });

    // IPC Distribution Chart
    const ipcDistCtx = document.getElementById('ipcDistChart').getContext('2d');
    ipcDistChart = new Chart(ipcDistCtx, {
        type: 'doughnut',
        data: {
            labels: ['Pipe', 'Queue', 'Shared Memory'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#6366f1', '#8b5cf6', '#ec4899']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Initialize WebSocket
function initWebSocket() {
    // Auto-detect environment for WebSocket connection
    const wsUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:5000'
        : 'https://YOUR_RENDER_APP_NAME.onrender.com'; // Replace with your Render URL after deployment

    socket = io(wsUrl);

    socket.on('connect', () => {
        console.log('WebSocket connected');
        if (currentSimulationId) {
            socket.emit('join_simulation', { simulation_id: currentSimulationId });
        }
    });

    socket.on('process_state_changed', (data) => {
        updateProcessState(data.process_id, data.state);
        addLiveEvent(`Process state changed: ${data.state}`);
    });

    socket.on('message_sent', (data) => {
        animateMessage(data);
        addLiveEvent(`Message sent: ${data.sender} → ${data.receiver}`);
        updateCharts();
    });

    socket.on('deadlock_detected', (data) => {
        showDeadlockAlert(data);
        addLiveEvent(`⚠️ DEADLOCK DETECTED: ${data.cycle.join(' → ')}`);
    });

    socket.on('bottleneck_detected', (data) => {
        showBottleneckAlert(data);
        addLiveEvent(`⚡ Bottleneck: ${data.process_name} (${data.avg_delay}ms)`);
    });
}

// Load simulation data
async function loadSimulationData() {
    currentSimulationId = localStorage.getItem('currentSimulationId');

    if (!currentSimulationId) {
        addLiveEvent('No active simulation. Please create one in the dashboard.');
        return;
    }

    try {
        const response = await apiRequest(`/simulation/${currentSimulationId}`);
        if (response.success) {
            processes = response.processes || [];
            channels = response.channels || [];
            updateCharts();

            if (socket && socket.connected) {
                socket.emit('join_simulation', { simulation_id: currentSimulationId });
            }
        }
    } catch (error) {
        console.error('Failed to load simulation data');
    }
}

// Draw canvas
function drawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (processes.length === 0) {
        ctx.fillStyle = '#94a3b8';
        ctx.font = '16px Inter';
        ctx.textAlign = 'center';
        ctx.fillText('No processes to visualize', canvas.width / 2, canvas.height / 2);
        return;
    }

    // Draw channels (edges)
    channels.forEach(channel => {
        const sender = processes.find(p => p.id === channel.sender_id);
        const receiver = processes.find(p => p.id === channel.receiver_id);

        if (sender && receiver) {
            const senderPos = getProcessPosition(processes.indexOf(sender));
            const receiverPos = getProcessPosition(processes.indexOf(receiver));

            drawArrow(senderPos.x, senderPos.y, receiverPos.x, receiverPos.y, channel.ipc_type);
        }
    });

    // Draw processes (nodes)
    processes.forEach((process, index) => {
        const pos = getProcessPosition(index);
        drawProcess(pos.x, pos.y, process);
    });

    // Draw messages
    messages.forEach((msg, index) => {
        if (msg.progress < 1) {
            drawMessage(msg);
            msg.progress += 0.02;
        } else {
            messages.splice(index, 1);
        }
    });
}

function getProcessPosition(index) {
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) / 3;
    const angle = (index / processes.length) * 2 * Math.PI - Math.PI / 2;

    return {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
    };
}

function drawProcess(x, y, process) {
    const radius = 40;

    // State color
    const stateColors = {
        'ready': '#3b82f6',
        'running': '#10b981',
        'waiting': '#f59e0b',
        'blocked': '#ef4444',
        'terminated': '#6b7280'
    };

    const color = stateColors[process.state] || '#6b7280';

    // Draw circle
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.fillStyle = color + '33';
    ctx.fill();
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.stroke();

    // Draw name
    ctx.fillStyle = '#f1f5f9';
    ctx.font = 'bold 14px Inter';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(process.process_name, x, y);

    // Draw state
    ctx.font = '10px Inter';
    ctx.fillStyle = '#cbd5e1';
    ctx.fillText(process.state, x, y + 20);
}

function drawArrow(x1, y1, x2, y2, ipcType) {
    const colors = {
        'pipe': '#6366f1',
        'queue': '#8b5cf6',
        'shmem': '#ec4899'
    };

    ctx.strokeStyle = colors[ipcType] || '#6366f1';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);

    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();

    ctx.setLineDash([]);

    // Arrow head
    const angle = Math.atan2(y2 - y1, x2 - x1);
    const headLength = 15;

    ctx.beginPath();
    ctx.moveTo(x2, y2);
    ctx.lineTo(
        x2 - headLength * Math.cos(angle - Math.PI / 6),
        y2 - headLength * Math.sin(angle - Math.PI / 6)
    );
    ctx.lineTo(
        x2 - headLength * Math.cos(angle + Math.PI / 6),
        y2 - headLength * Math.sin(angle + Math.PI / 6)
    );
    ctx.closePath();
    ctx.fillStyle = colors[ipcType] || '#6366f1';
    ctx.fill();
}

function drawMessage(msg) {
    const x = msg.startX + (msg.endX - msg.startX) * msg.progress;
    const y = msg.startY + (msg.endY - msg.startY) * msg.progress;

    ctx.beginPath();
    ctx.arc(x, y, 8, 0, 2 * Math.PI);
    ctx.fillStyle = '#10b981';
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.stroke();
}

function animateMessage(data) {
    const sender = processes.find(p => p.id === data.sender_id);
    const receiver = processes.find(p => p.id === data.receiver_id);

    if (sender && receiver) {
        const senderPos = getProcessPosition(processes.indexOf(sender));
        const receiverPos = getProcessPosition(processes.indexOf(receiver));

        messages.push({
            startX: senderPos.x,
            startY: senderPos.y,
            endX: receiverPos.x,
            endY: receiverPos.y,
            progress: 0
        });
    }
}

function updateProcessState(processId, state) {
    const process = processes.find(p => p.id === processId);
    if (process) {
        process.state = state;
    }
}

// Animation loop
function startAnimation() {
    function animate() {
        drawCanvas();
        requestAnimationFrame(animate);
    }
    animate();
}

// Update charts
async function updateCharts() {
    if (!currentSimulationId) return;

    try {
        const response = await apiRequest(`/statistics/${currentSimulationId}`);
        if (response.success) {
            const stats = response.statistics;

            // Update IPC distribution
            const dist = stats.ipc_distribution || {};
            ipcDistChart.data.datasets[0].data = [
                dist.pipe || 0,
                dist.queue || 0,
                dist.shmem || 0
            ];
            ipcDistChart.update();
        }
    } catch (error) {
        console.error('Failed to update charts');
    }
}

// Detect deadlock
async function detectDeadlock() {
    if (!currentSimulationId) return;

    try {
        const response = await apiRequest(`/deadlock/detect/${currentSimulationId}`);
        if (response.deadlock_found) {
            showDeadlockAlert(response);
        } else {
            showToast('No deadlock detected', 'success');
        }
    } catch (error) {
        showToast('Failed to detect deadlock', 'error');
    }
}

// Analyze bottleneck
async function analyzeBottleneck() {
    if (!currentSimulationId) return;

    try {
        const response = await apiRequest(`/bottleneck/analyze/${currentSimulationId}`);
        if (response.process_analysis && response.process_analysis.length > 0) {
            const bottlenecks = response.process_analysis.filter(p => p.is_bottleneck);
            if (bottlenecks.length > 0) {
                showBottleneckAlert(bottlenecks[0]);
            } else {
                showToast('No bottlenecks detected', 'success');
            }
        } else {
            showToast('No bottleneck analysis available', 'info');
        }
    } catch (error) {
        showToast('Failed to analyze bottleneck', 'error');
    }
}

// Show deadlock alert
function showDeadlockAlert(data) {
    const alertsContainer = document.getElementById('alertsContainer');
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger fade-in';
    alert.innerHTML = `
        <strong>🔴 DEADLOCK DETECTED!</strong><br>
        <strong>Cycle:</strong> ${data.cycle ? data.cycle.join(' → ') : 'Unknown'}<br>
        <strong>Processes Involved:</strong> ${data.processes_involved || 'N/A'}<br>
        <strong>Time:</strong> ${new Date().toLocaleTimeString()}
    `;
    alertsContainer.appendChild(alert);

    // Highlight deadlocked processes
    if (data.cycle) {
        data.cycle.forEach(processName => {
            const process = processes.find(p => p.process_name === processName);
            if (process) {
                process.state = 'blocked';
            }
        });
    }
}

// Show bottleneck alert
function showBottleneckAlert(data) {
    const alertsContainer = document.getElementById('alertsContainer');
    const alert = document.createElement('div');
    alert.className = 'alert alert-warning fade-in';
    alert.innerHTML = `
        <strong>⚡ BOTTLENECK DETECTED!</strong><br>
        <strong>Process:</strong> ${data.process_name || 'Unknown'}<br>
        <strong>Average Delay:</strong> ${data.avg_delay ? data.avg_delay.toFixed(2) + 'ms' : 'N/A'}<br>
        <strong>Message Count:</strong> ${data.message_count || 0}<br>
        <strong>Time:</strong> ${new Date().toLocaleTimeString()}
    `;
    alertsContainer.appendChild(alert);
}

// Add live event
function addLiveEvent(message) {
    const container = document.getElementById('liveEvents');

    // Clear placeholder if exists
    if (container.querySelector('.text-secondary')) {
        container.innerHTML = '';
    }

    const event = document.createElement('div');
    event.className = 'event-item fade-in';
    event.innerHTML = `
        <div class="event-timestamp">${new Date().toLocaleTimeString()}</div>
        <div class="event-message">${message}</div>
    `;

    container.insertBefore(event, container.firstChild);

    // Keep only last 20 events
    while (container.children.length > 20) {
        container.removeChild(container.lastChild);
    }
}

// Auto-refresh
setInterval(() => {
    if (currentSimulationId) {
        loadSimulationData();
    }
}, 10000);
