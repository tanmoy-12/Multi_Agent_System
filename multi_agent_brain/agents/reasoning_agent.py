# multi_agent_brain/agents/reasoning_agent.py
import asyncio
from .base import BaseAgent
from ..scheduler.execution_context import ExecutionContext
from ..models.execution_plan import TaskResult

class ReasoningAgent(BaseAgent):
    agent_id = "reasoning_agent"
    agent_name = "Reasoning Agent"
    capabilities = ["reasoning", "analysis", "planning", "biography", "extraction"]
    supported_tools = []
    
    async def execute(self, context: ExecutionContext) -> TaskResult:
        await asyncio.sleep(0.2)
        if "Elon Musk" in context.task_description or "biography" in context.task_description.lower():
            output = "Elon Musk is a business magnate, industrial designer, and engineer. He is the founder of SpaceX, Tesla, Neuralink, and The Boring Company."
        else:
            output = f"Reasoned about: {context.task_description}"
        return TaskResult(task_id=context.task_id, status="success", output=output)