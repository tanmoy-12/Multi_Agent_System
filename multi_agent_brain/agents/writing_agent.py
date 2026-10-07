# multi_agent_brain/agents/writing_agent.py
import asyncio
from .base import BaseAgent
from ..scheduler.execution_context import ExecutionContext
from ..models.execution_plan import TaskResult

class WritingAgent(BaseAgent):
    agent_id = "writing_agent"
    agent_name = "Writing Agent"
    capabilities = ["writing", "report_generation", "text_generation", "summarization"]
    supported_tools = ["file_writer"]
    
    async def execute(self, context: ExecutionContext) -> TaskResult:
        await asyncio.sleep(0.3)
        deps = context.resolved_inputs
        content = " ".join([str(v) for v in deps.values()])
        output = f"Final Report:\n{content}"
        return TaskResult(task_id=context.task_id, status="success", output=output)