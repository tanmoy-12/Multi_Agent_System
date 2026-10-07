# multi_agent_brain/scheduler/task_queue.py
import heapq
from typing import List, Tuple

class ReadyQueue:
    def __init__(self):
        self._queue: List[Tuple[int, int, str]] = []
        self._counter = 0
        
    def push(self, task_id: str, priority: str):
        p_map = {"high": 0, "medium": 1, "low": 2}
        p_val = p_map.get(priority.lower(), 1)
        heapq.heappush(self._queue, (p_val, self._counter, task_id))
        self._counter += 1
        
    def pop(self) -> str:
        return heapq.heappop(self._queue)[2]
        
    def is_empty(self) -> bool:
        return len(self._queue) == 0