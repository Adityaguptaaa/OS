import random
import time
from datetime import datetime
import json

class IPCSimulator:
    """Simulates different IPC mechanisms"""
    
    def __init__(self, config):
        self.config = config
        self.pipe_delay_range = config.DEFAULT_PIPE_DELAY
        self.queue_delay_range = config.DEFAULT_QUEUE_DELAY
        self.shmem_delay_range = config.DEFAULT_SHMEM_DELAY
        
    def simulate_pipe(self, message, channel_config):
        """
        Simulate pipe communication (unidirectional FIFO)
        Returns: (success, delay_ms, info)
        """
        buffer_size = channel_config.get('buffer_size', 4096)
        message_size = len(message.encode('utf-8'))
        
        if message_size > buffer_size:
            return False, 0, f"Message size ({message_size}) exceeds buffer size ({buffer_size})"
        
        # Simulate blocking delay
        delay = random.randint(*self.pipe_delay_range)
        
        return True, delay, "Pipe transfer successful"
    
    def simulate_message_queue(self, message, channel_config):
        """
        Simulate message queue (bidirectional, priority-based)
        Returns: (success, delay_ms, info)
        """
        priority = channel_config.get('priority', 0)
        max_queue_size = channel_config.get('max_queue_size', 100)
        
        # Simulate queue processing delay
        base_delay = random.randint(*self.queue_delay_range)
        
        # Higher priority = lower delay
        priority_factor = max(0.5, 1 - (priority * 0.1))
        delay = int(base_delay * priority_factor)
        
        return True, delay, f"Message queued with priority {priority}"
    
    def simulate_shared_memory(self, message, channel_config):
        """
        Simulate shared memory (fastest, but needs synchronization)
        Returns: (success, delay_ms, info)
        """
        use_mutex = channel_config.get('use_mutex', True)
        
        # Shared memory is fast
        base_delay = random.randint(*self.shmem_delay_range)
        
        # Mutex adds overhead
        if use_mutex:
            mutex_overhead = random.randint(10, 30)
            delay = base_delay + mutex_overhead
            info = "Shared memory write with mutex"
        else:
            delay = base_delay
            info = "Shared memory write (no mutex - potential race condition)"
        
        return True, delay, info
    
    def send_message(self, ipc_type, message, channel_config):
        """
        Send message through specified IPC mechanism
        Returns: (success, delay_ms, info)
        """
        if ipc_type == 'pipe':
            return self.simulate_pipe(message, channel_config)
        elif ipc_type == 'queue':
            return self.simulate_message_queue(message, channel_config)
        elif ipc_type == 'shmem':
            return self.simulate_shared_memory(message, channel_config)
        else:
            return False, 0, f"Unknown IPC type: {ipc_type}"
