from collections import defaultdict
from datetime import datetime, timedelta

class BottleneckAnalyzer:
    """Analyzes communication patterns to identify bottlenecks"""
    
    def __init__(self, threshold_ms=500):
        self.threshold_ms = threshold_ms
        self.process_delays = defaultdict(list)  # process_id -> [delays]
        self.channel_delays = defaultdict(list)  # channel_id -> [delays]
    
    def record_delay(self, process_id, channel_id, delay_ms):
        """Record a communication delay"""
        self.process_delays[process_id].append(delay_ms)
        self.channel_delays[channel_id].append(delay_ms)
    
    def get_average_delay(self, delays):
        """Calculate average delay"""
        if not delays:
            return 0
        return sum(delays) / len(delays)
    
    def analyze_processes(self, processes):
        """
        Analyze processes for bottlenecks
        Returns: [{
            'process_id': int,
            'process_name': str,
            'avg_delay': float,
            'max_delay': int,
            'is_bottleneck': bool
        }]
        """
        results = []
        
        for process in processes:
            delays = self.process_delays.get(process.id, [])
            
            if delays:
                avg_delay = self.get_average_delay(delays)
                max_delay = max(delays)
                is_bottleneck = avg_delay > self.threshold_ms
                
                results.append({
                    'process_id': process.id,
                    'process_name': process.process_name,
                    'avg_delay': round(avg_delay, 2),
                    'max_delay': max_delay,
                    'message_count': len(delays),
                    'is_bottleneck': is_bottleneck
                })
        
        # Sort by average delay (descending)
        results.sort(key=lambda x: x['avg_delay'], reverse=True)
        return results
    
    def analyze_channels(self, channels):
        """
        Analyze IPC channels for bottlenecks
        Returns: [{
            'channel_id': int,
            'ipc_type': str,
            'avg_delay': float,
            'is_slow': bool
        }]
        """
        results = []
        
        for channel in channels:
            delays = self.channel_delays.get(channel.id, [])
            
            if delays:
                avg_delay = self.get_average_delay(delays)
                is_slow = avg_delay > self.threshold_ms
                
                results.append({
                    'channel_id': channel.id,
                    'ipc_type': channel.ipc_type,
                    'sender': channel.sender.process_name,
                    'receiver': channel.receiver.process_name,
                    'avg_delay': round(avg_delay, 2),
                    'message_count': len(delays),
                    'is_slow': is_slow
                })
        
        results.sort(key=lambda x: x['avg_delay'], reverse=True)
        return results
    
    def get_suggestions(self, bottlenecks):
        """Generate optimization suggestions"""
        suggestions = []
        
        for bottleneck in bottlenecks:
            if bottleneck['is_bottleneck']:
                process_name = bottleneck['process_name']
                avg_delay = bottleneck['avg_delay']
                
                suggestions.append({
                    'process': process_name,
                    'issue': f'High average delay: {avg_delay}ms',
                    'suggestions': [
                        'Consider using shared memory instead of pipes/queues',
                        'Reduce message size',
                        'Implement asynchronous communication',
                        'Check for resource contention'
                    ]
                })
        
        return suggestions
    
    def reset(self):
        """Reset analyzer state"""
        self.process_delays.clear()
        self.channel_delays.clear()
