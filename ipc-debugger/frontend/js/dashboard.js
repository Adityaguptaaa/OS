// Dashboard JavaScript

let currentSimulation = null;
let processes = [];
let channels = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadOrCreateSimulation();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    document.getElementById('createSimBtn').addEventListener('click', () => showModal('createSimModal'));
    document.getElementById('addProcessBtn').addEventListener('click', () => showModal('addProcessModal'));

    document.getElementById('createSimForm').addEventListener('submit', handleCreateSimulation);
    document.getElementById('addProcessForm').addEventListener('submit', handleAddProcess);
    document.getElementById('ipcConfigForm').addEventListener('submit', handleCreateChannel);
    document.getElementById('sendMessageForm').addEventListener('submit', handleSendMessage);

    document.getElementById('startSimBtn').addEventListener('click', startSimulation);
    document.getElementById('stopSimBtn').addEventListener('click', stopSimulation);
    document.getElementById('resetSimBtn').addEventListener('click', resetSimulation);
}

// Load or create simulation
async function loadOrCreateSimulation() {
    const simId = localStorage.getItem('currentSimulationId');

    if (simId) {
        try {
            const response = await apiRequest(`/simulation/${simId}`);
            if (response.success) {
                currentSimulation = response.simulation;
                processes = response.processes || [];
                channels = response.channels || [];
                updateDashboard();
                return;
            }
        } catch (error) {
            console.log('Simulation not found, creating new one');
        }
    }

    // Create new simulation
    createNewSimulation();
}

// Load simulation by ID
async function loadSimulation(simId) {
    try {
        const response = await apiRequest(`/simulation/${simId}`);
        if (response.success) {
            currentSimulation = response.simulation;
            processes = response.processes || [];
            channels = response.channels || [];
            updateDashboard();
        }
    } catch (error) {
        console.error('Failed to load simulation');
    }
}

async function createNewSimulation(name = null) {
    try {
        const simName = name || `Simulation_${new Date().toISOString().slice(0, 10)}`;
        const response = await apiRequest('/simulation/create', {
            method: 'POST',
            body: JSON.stringify({ name: simName })
        });

        if (response.success) {
            currentSimulation = response.simulation;
            // Reset processes and channels for the new simulation
            processes = [];
            channels = [];
            localStorage.setItem('currentSimulationId', currentSimulation.id);
            document.getElementById('simId').textContent = currentSimulation.id;
            showToast('Simulation created successfully', 'success');
            updateDashboard();
        }
    } catch (error) {
        showToast('Failed to create simulation', 'error');
    }
}

// Handle create simulation form
async function handleCreateSimulation(e) {
    e.preventDefault();
    const name = document.getElementById('simName').value;
    await createNewSimulation(name);
    closeModal('createSimModal');
    document.getElementById('createSimForm').reset();
}

// Handle add process
async function handleAddProcess(e) {
    e.preventDefault();

    if (!currentSimulation) {
        showToast('Please create a simulation first', 'warning');
        return;
    }

    const name = document.getElementById('processName').value;
    const priority = parseInt(document.getElementById('processPriority').value);

    try {
        const response = await apiRequest('/process/create', {
            method: 'POST',
            body: JSON.stringify({
                simulation_id: currentSimulation.id,
                name: name,
                priority: priority
            })
        });

        if (response.success) {
            processes.push(response.process);
            updateDashboard();
            showToast(`Process "${name}" created`, 'success');
            closeModal('addProcessModal');
            document.getElementById('addProcessForm').reset();
        }
    } catch (error) {
        showToast('Failed to create process', 'error');
    }
}

// Handle create channel
async function handleCreateChannel(e) {
    e.preventDefault();

    if (!currentSimulation) {
        showToast('Please create a simulation first', 'warning');
        return;
    }

    const ipcType = document.getElementById('ipcType').value;
    const senderId = parseInt(document.getElementById('senderProcess').value);
    const receiverId = parseInt(document.getElementById('receiverProcess').value);

    if (!senderId || !receiverId) {
        showToast('Please select both sender and receiver', 'warning');
        return;
    }

    if (senderId === receiverId) {
        showToast('Sender and receiver must be different', 'warning');
        return;
    }

    try {
        const response = await apiRequest('/ipc/create', {
            method: 'POST',
            body: JSON.stringify({
                simulation_id: currentSimulation.id,
                type: ipcType,
                sender_id: senderId,
                receiver_id: receiverId,
                config: {}
            })
        });

        if (response.success) {
            channels.push(response.channel);
            updateDashboard();
            showToast('Channel created successfully', 'success');
        }
    } catch (error) {
        showToast('Failed to create channel', 'error');
    }
}

// Handle send message
async function handleSendMessage(e) {
    e.preventDefault();

    const channelId = parseInt(document.getElementById('messageChannel').value);
    const content = document.getElementById('messageContent').value;

    if (!channelId || !content) {
        showToast('Please select channel and enter message', 'warning');
        return;
    }

    try {
        const response = await apiRequest('/ipc/send', {
            method: 'POST',
            body: JSON.stringify({
                channel_id: channelId,
                content: content
            })
        });

        if (response.success) {
            showToast(`Message sent (${response.delay_ms}ms delay)`, 'success');
            document.getElementById('messageContent').value = '';
            updateStatistics();
        }
    } catch (error) {
        showToast('Failed to send message', 'error');
    }
}

// Start simulation
async function startSimulation() {
    if (!currentSimulation) return;

    try {
        const response = await apiRequest('/simulation/start', {
            method: 'POST',
            body: JSON.stringify({ simulation_id: currentSimulation.id })
        });

        if (response.success) {
            // Reload simulation to get updated status
            await loadSimulation(currentSimulation.id);
            showToast('Simulation started', 'success');
        }
    } catch (error) {
        showToast('Failed to start simulation', 'error');
    }
}

// Stop simulation
async function stopSimulation() {
    if (!currentSimulation) return;

    try {
        const response = await apiRequest('/simulation/stop', {
            method: 'POST',
            body: JSON.stringify({ simulation_id: currentSimulation.id })
        });

        if (response.success) {
            // Reload simulation to get updated status
            await loadSimulation(currentSimulation.id);
            showToast('Simulation stopped', 'info');
        }
    } catch (error) {
        showToast('Failed to stop simulation', 'error');
    }
}

// Reset simulation
async function resetSimulation() {
    if (confirm('Are you sure you want to reset? This will delete all processes and channels.')) {
        if (currentSimulation) {
            try {
                await apiRequest(`/simulation/${currentSimulation.id}`, { method: 'DELETE' });
            } catch (error) {
                console.log('Error deleting simulation');
            }
        }

        localStorage.removeItem('currentSimulationId');
        currentSimulation = null;
        processes = [];
        channels = [];
        await createNewSimulation();
    }
}

// Update dashboard UI
function updateDashboard() {
    updateProcessList();
    updateChannelsList();
    updateProcessSelects();
    updateChannelSelect();
    updateStatistics();

    if (currentSimulation) {
        document.getElementById('simId').textContent = currentSimulation.id;

        // Update status badge
        const status = currentSimulation.status || 'idle';
        const statusEl = document.getElementById('simStatus');
        statusEl.textContent = status.charAt(0).toUpperCase() + status.slice(1);

        // Update status badge class
        if (status === 'running') {
            statusEl.className = 'badge badge-success';
            document.getElementById('startSimBtn').disabled = true;
            document.getElementById('stopSimBtn').disabled = false;
        } else {
            statusEl.className = 'badge badge-secondary';
            document.getElementById('startSimBtn').disabled = false;
            document.getElementById('stopSimBtn').disabled = true;
        }
    }
}

// Update process list
function updateProcessList() {
    const container = document.getElementById('processList');

    if (processes.length === 0) {
        container.innerHTML = '<p class="text-secondary">No processes created yet.</p>';
        return;
    }

    container.innerHTML = processes.map(proc => `
        <div class="process-item">
            <div class="process-info">
                <div class="process-name">${proc.process_name}</div>
                <div class="process-meta">
                    State: <span class="badge badge-${getStateBadgeClass(proc.state)}">${proc.state}</span>
                    Priority: ${proc.priority}
                </div>
            </div>
            <div class="process-actions">
                <button class="btn btn-sm btn-error" onclick="deleteProcess(${proc.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

// Update channels list
function updateChannelsList() {
    const container = document.getElementById('channelsList');

    if (channels.length === 0) {
        container.innerHTML = '<p class="text-secondary">No channels created yet.</p>';
        return;
    }

    container.innerHTML = channels.map(channel => `
        <div class="channel-item">
            <div>
                <div class="channel-type">${channel.ipc_type}</div>
                <div class="channel-route">${channel.sender_name} → ${channel.receiver_name}</div>
            </div>
            <button class="btn btn-sm btn-error" onclick="deleteChannel(${channel.id})">Delete</button>
        </div>
    `).join('');
}

// Update process selects
function updateProcessSelects() {
    const senderSelect = document.getElementById('senderProcess');
    const receiverSelect = document.getElementById('receiverProcess');

    const options = processes.map(p =>
        `<option value="${p.id}">${p.process_name}</option>`
    ).join('');

    senderSelect.innerHTML = '<option value="">Select sender...</option>' + options;
    receiverSelect.innerHTML = '<option value="">Select receiver...</option>' + options;
}

// Update channel select for messaging
function updateChannelSelect() {
    const select = document.getElementById('messageChannel');

    const options = channels.map(c =>
        `<option value="${c.id}">${c.ipc_type.toUpperCase()}: ${c.sender_name} → ${c.receiver_name}</option>`
    ).join('');

    select.innerHTML = '<option value="">Select channel...</option>' + options;
}

// Update statistics
async function updateStatistics() {
    if (!currentSimulation) return;

    try {
        const response = await apiRequest(`/statistics/${currentSimulation.id}`);
        if (response.success) {
            const stats = response.statistics;
            document.getElementById('totalProcesses').textContent = stats.total_processes;
            document.getElementById('totalChannels').textContent = stats.total_channels;
            document.getElementById('totalMessages').textContent = stats.total_messages;
            document.getElementById('avgLatency').textContent = `${stats.avg_latency_ms}ms`;
        }
    } catch (error) {
        console.error('Failed to load statistics');
    }
}

// Delete process
async function deleteProcess(processId) {
    if (!confirm('Delete this process? This will also delete all associated IPC channels.')) return;

    try {
        const response = await apiRequest(`/process/${processId}`, { method: 'DELETE' });

        // Remove process from local array
        processes = processes.filter(p => p.id !== processId);

        // Remove associated channels from local array
        channels = channels.filter(c => c.sender_id !== processId && c.receiver_id !== processId);

        updateDashboard();

        // Show appropriate message
        const deletedChannels = response.deleted_channels || 0;
        if (deletedChannels > 0) {
            showToast(`Process deleted (${deletedChannels} channel${deletedChannels > 1 ? 's' : ''} also removed)`, 'info');
        } else {
            showToast('Process deleted', 'info');
        }
    } catch (error) {
        showToast('Failed to delete process', 'error');
    }
}

// Delete channel
async function deleteChannel(channelId) {
    if (!confirm('Delete this channel?')) return;

    try {
        await apiRequest(`/ipc/${channelId}`, { method: 'DELETE' });
        channels = channels.filter(c => c.id !== channelId);
        updateDashboard();
        showToast('Channel deleted', 'info');
    } catch (error) {
        showToast('Failed to delete channel', 'error');
    }
}

// Helper functions
function getStateBadgeClass(state) {
    const classes = {
        'ready': 'info',
        'running': 'success',
        'waiting': 'warning',
        'blocked': 'error',
        'terminated': 'secondary'
    };
    return classes[state] || 'secondary';
}

function showModal(modalId) {
    document.getElementById(modalId).style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Auto-refresh statistics
setInterval(() => {
    if (currentSimulation) {
        updateStatistics();
    }
}, 5000);
