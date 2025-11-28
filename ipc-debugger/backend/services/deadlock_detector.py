from collections import defaultdict, deque

class DeadlockDetector:
    """Detects deadlocks using Resource Allocation Graph (RAG) cycle detection"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset the detector state"""
        self.waiting_for = {}  # process_id -> resource_id (what process is waiting for)
        self.held_by = defaultdict(list)  # resource_id -> [process_ids] (who holds the resource)
    
    def add_wait(self, process_id, resource_id):
        """Record that a process is waiting for a resource"""
        self.waiting_for[process_id] = resource_id
    
    def add_hold(self, process_id, resource_id):
        """Record that a process holds a resource"""
        if process_id not in self.held_by[resource_id]:
            self.held_by[resource_id].append(process_id)
    
    def release_resource(self, process_id, resource_id):
        """Release a resource held by a process"""
        if process_id in self.held_by[resource_id]:
            self.held_by[resource_id].remove(process_id)
        if process_id in self.waiting_for:
            del self.waiting_for[process_id]
    
    def detect_cycle(self):
        """
        Detect cycles in the resource allocation graph using DFS
        Returns: (has_deadlock, cycle_processes)
        """
        # Build adjacency list for process-resource graph
        graph = defaultdict(list)
        
        # Process -> Resource edges (waiting)
        for process_id, resource_id in self.waiting_for.items():
            graph[f"P{process_id}"].append(f"R{resource_id}")
        
        # Resource -> Process edges (allocated)
        for resource_id, process_ids in self.held_by.items():
            for process_id in process_ids:
                graph[f"R{resource_id}"].append(f"P{process_id}")
        
        # DFS to find cycles
        visited = set()
        rec_stack = set()
        cycle = []
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle.extend(path[cycle_start:])
                    return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        # Check all nodes - use list() to avoid RuntimeError
        for node in list(graph.keys()):
            if node not in visited:
                if dfs(node, []):
                    # Extract process IDs from cycle
                    process_cycle = [int(n[1:]) for n in cycle if n.startswith('P')]
                    return True, list(set(process_cycle))
        
        return False, []
    
    def analyze_deadlock(self, processes):
        """
        Analyze current state for deadlock
        Returns: {
            'deadlock_found': bool,
            'processes': [process_ids],
            'cycle': [process_names],
            'suggestion': str
        }
        """
        has_deadlock, cycle_processes = self.detect_cycle()
        
        if has_deadlock:
            process_names = [p.process_name for p in processes if p.id in cycle_processes]
            return {
                'deadlock_found': True,
                'processes': cycle_processes,
                'cycle': process_names,
                'suggestion': 'Break the circular wait by releasing resources or using timeouts'
            }
        
        return {
            'deadlock_found': False,
            'processes': [],
            'cycle': [],
            'suggestion': None
        }
