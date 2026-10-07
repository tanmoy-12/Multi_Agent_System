# multi_agent_brain/scheduler/resource_manager.py
import asyncio

class ResourceManager:
    def __init__(self, max_concurrent_tasks: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.running_agents = {}

    async def acquire(self):
        await self.semaphore.acquire()

    def release(self):
        self.semaphore.release()