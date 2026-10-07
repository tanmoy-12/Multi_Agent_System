# multi_agent_brain/scheduler_main.py
import asyncio
import argparse
import json
import sys
import os

# Add the PROJECT ROOT (the folder that CONTAINS multi_agent_brain/) to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from multi_agent_brain.models.execution_plan import ExecutionPlan
from multi_agent_brain.scheduler.scheduler import Scheduler
from multi_agent_brain.scheduler.task_executor import TaskExecutor
from multi_agent_brain.scheduler.agent_selector import AgentSelector
from multi_agent_brain.scheduler.input_resolver import InputResolver
from multi_agent_brain.scheduler.output_manager import OutputManager
from multi_agent_brain.scheduler.retry_manager import RetryManager
from multi_agent_brain.agents.registry import AgentRegistry
from multi_agent_brain.agents.research_agent import ResearchAgent
from multi_agent_brain.agents.reasoning_agent import ReasoningAgent
from multi_agent_brain.agents.writing_agent import WritingAgent
from multi_agent_brain.tools.registry import ToolRegistry
from multi_agent_brain.tools.web_search import WebSearchTool

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan_file", help="Path to execution_plan.json")
    args = parser.parse_args()
    
    with open(args.plan_file, 'r') as f:
        data = json.load(f)
        
    plan = ExecutionPlan.model_validate(data)
    
    agent_reg = AgentRegistry()
    agent_reg.register(ResearchAgent())
    agent_reg.register(ReasoningAgent())
    agent_reg.register(WritingAgent())
    
    tool_reg = ToolRegistry()
    tool_reg.register(WebSearchTool())
    
    selector = AgentSelector(agent_reg)
    out_mgr = OutputManager(plan.plan_id)
    in_resolver = InputResolver(out_mgr)
    retry_mgr = RetryManager()
    
    executor = TaskExecutor(selector, in_resolver, out_mgr, retry_mgr, tool_reg)
    scheduler = Scheduler(plan, executor, max_concurrent=5)
    
    print("\n========================================")
    print("MULTI-AGENT SCHEDULER")
    print("========================================")
    print(f"Plan: {plan.plan_id}")
    print(f"Goal: {plan.user_goal}\n")
    
    result = await scheduler.run()
    
    print("\n----------------------------------------")
    print("EXECUTION COMPLETE")
    print("----------------------------------------")
    print(f"Completed: {len(result.completed_tasks)}")
    print(f"Failed: {len(result.failed_tasks)}")
    print(f"Blocked: {len(result.blocked_tasks)}")
    print(f"\nFinal Output:\n{result.final_output}")
    
    os.makedirs("outputs", exist_ok=True)
    with open(f"outputs/{plan.plan_id}_result.json", "w") as f:
        json.dump(result.model_dump(), f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())