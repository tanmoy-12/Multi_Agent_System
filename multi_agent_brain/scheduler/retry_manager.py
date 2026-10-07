# multi_agent_brain/scheduler/retry_manager.py
import asyncio

class RetryManager:
    def __init__(self):
        self.attempts = {}

    def get_attempt(self, task_id: str) -> int:
        return self.attempts.get(task_id, 1)

    def increment(self, task_id: str):
        self.attempts[task_id] = self.attempts.get(task_id, 1) + 1

    async def backoff(self, task_id: str):
        attempt = self.get_attempt(task_id)
        delay = 2 ** (attempt - 1)
        await asyncio.sleep(delay)
        
    def reset(self, task_id: str):
        self.attempts.pop(task_id, None)