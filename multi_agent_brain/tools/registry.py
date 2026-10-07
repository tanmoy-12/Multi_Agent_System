# multi_agent_brain/tools/registry.py
from typing import List
from .base import BaseTool

class ToolRegistry:
    def __init__(self):
        self.tools = {}
        
    def register(self, tool: BaseTool):
        self.tools[tool.tool_id] = tool
        
    def get(self, tool_id: str) -> BaseTool:
        return self.tools.get(tool_id)
        
    def get_tools(self, tool_ids: List[str]) -> List[BaseTool]:
        return [self.tools[tid] for tid in tool_ids if tid in self.tools]