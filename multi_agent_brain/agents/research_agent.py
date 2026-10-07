# multi_agent_brain/agents/research_agent.py
import asyncio
from .base import BaseAgent
from ..scheduler.execution_context import ExecutionContext
from ..models.execution_plan import TaskResult

class ResearchAgent(BaseAgent):
    agent_id = "research_agent"
    agent_name = "Research Agent"
    capabilities = ["web_research", "information_retrieval", "fact_extraction", "summarization", "search"]
    supported_tools = ["web_search", "webpage_reader"]
    
    async def execute(self, context: ExecutionContext) -> TaskResult:
        await asyncio.sleep(0.5)
        search_tool = next((t for t in context.available_tools if t.tool_id == "web_search"), None)
        search_res = await search_tool.execute({"query": context.task_description}) if search_tool else {}
        output = f"Researched: {context.task_description}. Findings: {search_res}"
        return TaskResult(task_id=context.task_id, status="success", output=output)