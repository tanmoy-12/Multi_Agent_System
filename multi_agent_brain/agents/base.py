# multi_agent_brain/agents/base.py
from abc import ABC, abstractmethod
from typing import List
from ..scheduler.execution_context import ExecutionContext
from ..models.execution_plan import TaskResult

class BaseAgent(ABC):
    agent_id: str
    agent_name: str
    capabilities: List[str]
    supported_tools: List[str]
    max_concurrency: int = 1

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> TaskResult:
        pass