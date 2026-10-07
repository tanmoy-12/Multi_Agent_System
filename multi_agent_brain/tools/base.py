# multi_agent_brain/tools/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    tool_id: str
    name: str
    description: str
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        pass