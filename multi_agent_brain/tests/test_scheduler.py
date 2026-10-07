# multi_agent_brain/tests/test_scheduler.py
import pytest
import asyncio
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from multi_agent_brain.models.execution_plan import ExecutionPlan, TaskExecutionDetail
from multi_agent_brain.scheduler.scheduler import Scheduler
from multi_agent_brain.scheduler.task_executor import TaskExecutor
from multi_agent_brain.scheduler.agent_selector import AgentSelector
from multi_agent_brain.scheduler.input_resolver import InputResolver
from multi_agent_brain.scheduler.output_manager import OutputManager
from multi_agent_brain.scheduler.retry_manager import RetryManager
from multi_agent_brain.agents.registry import AgentRegistry
from multi_agent_brain.agents.base import BaseAgent
from multi_agent_brain.scheduler.execution_context import ExecutionContext
from multi_agent_brain.tools.registry import ToolRegistry
from multi_agent_brain.models.execution_plan import TaskResult

class MockAgent(BaseAgent):
    agent_id = "mock_agent"
    agent_name = "Mock Agent"
    capabilities = ["mock", "test", "research", "reasoning", "writing"]
    supported_tools = ["web_search"]
    
    def __init__(self, fail_times=0, invalid_output=False):
        self.fail_times = fail_times
        self.invalid_output = invalid_output
        self.call_count = 0

    async def execute(self, context: ExecutionContext):
        self.call_count += 1
        if self.call_count <= self.fail_times:
            raise Exception("Mock transient failure")
            
        out = f"Output for {context.task_id}"
        if self.invalid_output:
            out = None 
            
        return TaskResult(task_id=context.task_id, status="success", output=out)

def create_plan(tasks_data, edges_data):
    tasks = [TaskExecutionDetail(**t) for t in tasks_data]
    plan_data = {
        "plan_id": "test_plan",
        "user_goal": "test",
        "tasks": [t.model_dump() for t in tasks],
        "dependency_graph": {"edges": edges_data},
        "execution_stages": []
    }
    return ExecutionPlan.model_validate(plan_data)

def setup_scheduler(plan, agent):
    registry = AgentRegistry()
    registry.register(agent)
    selector = AgentSelector(registry)
    out_mgr = OutputManager(plan.plan_id, base_dir="test_outputs")
    in_res = InputResolver(out_mgr)
    retry_mgr = RetryManager()
    tool_reg = ToolRegistry()
    executor = TaskExecutor(selector, in_res, out_mgr, retry_mgr, tool_reg)
    return Scheduler(plan, executor, max_concurrent=5)

@pytest.mark.asyncio
async def test_single_task():
    plan = create_plan([{"task_id": "T1", "description": "test"}], [])
    agent = MockAgent()
    sched = setup_scheduler(plan, agent)
    res = await sched.run()
    assert res.status == "completed"
    assert "T1" in res.completed_tasks

@pytest.mark.asyncio
async def test_parallel_tasks():
    plan = create_plan([
        {"task_id": "T1", "description": "t1"},
        {"task_id": "T2", "description": "t2"}
    ], [])
    agent = MockAgent()
    sched = setup_scheduler(plan, agent)
    res = await sched.run()
    assert len(res.completed_tasks) == 2

@pytest.mark.asyncio
async def test_dependency_chain():
    plan = create_plan([
        {"task_id": "T1", "description": "t1"},
        {"task_id": "T2", "description": "t2"},
        {"task_id": "T3", "description": "t3"}
    ], [{"from": "T1", "to": "T2"}, {"from": "T2", "to": "T3"}])
    agent = MockAgent()
    sched = setup_scheduler(plan, agent)
    res = await sched.run()
    assert res.completed_tasks == ["T1", "T2", "T3"]

@pytest.mark.asyncio
async def test_parallel_branches():
    plan = create_plan([
        {"task_id": "T1", "description": "t1"},
        {"task_id": "T2", "description": "t2"},
        {"task_id": "T3", "description": "t3"}
    ], [{"from": "T1", "to": "T3"}, {"from": "T2", "to": "T3"}])
    agent = MockAgent()
    sched = setup_scheduler(plan, agent)
    res = await sched.run()
    assert "T3" in res.completed_tasks

@pytest.mark.asyncio
async def test_failure_propagation():
    plan = create_plan([
        {"task_id": "T1", "description": "t1"},
        {"task_id": "T2", "description": "t2"},
        {"task_id": "T3", "description": "t3"}
    ], [{"from": "T1", "to": "T3"}, {"from": "T2", "to": "T3"}])
    
    class FailAgent(MockAgent):
        async def execute(self, context):
            if context.task_id == "T1":
                raise Exception("Permanent failure")
            return await super().execute(context)
            
    agent = FailAgent()
    sched = setup_scheduler(plan, agent)
    res = await sched.run()
    
    assert "T1" in res.failed_tasks
    assert "T3" in res.blocked_tasks
    assert "T2" in res.completed_tasks

@pytest.mark.asyncio
async def test_retry_mechanism():
    plan = create_plan([{"task_id": "T1", "description": "t1", "max_retries": 3}], [])
    agent = MockAgent(fail_times=2)
    sched = setup_scheduler(plan, agent)
    res = await sched.run()
    assert "T1" in res.completed_tasks
    assert agent.call_count == 3

@pytest.mark.asyncio
async def test_invalid_output_retry():
    plan = create_plan([{
        "task_id": "T1", 
        "description": "t1", 
        "max_retries": 2,
        "output_schema": {"type": "string"}
    }], [])
    agent = MockAgent(invalid_output=True)
    sched = setup_scheduler(plan, agent)
    res = await sched.run()
    assert "T1" in res.failed_tasks

@pytest.mark.asyncio
async def test_capability_mismatch():
    plan = create_plan([{
        "task_id": "T1", 
        "description": "t1",
        "required_capabilities": ["quantum_computing"]
    }], [])
    agent = MockAgent()
    sched = setup_scheduler(plan, agent)
    res = await sched.run()
    assert "T1" in res.failed_tasks

@pytest.mark.asyncio
async def test_concurrency_limit():
    tasks = [{"task_id": f"T{i}", "description": f"t{i}"} for i in range(10)]
    plan = create_plan(tasks, [])
    
    active = 0
    max_active = 0
    
    class ConcurrencyAgent(MockAgent):
        async def execute(self, context):
            nonlocal active, max_active
            active += 1
            if active > max_active: max_active = active
            await asyncio.sleep(0.1)
            active -= 1
            return TaskResult(task_id=context.task_id, status="success", output="ok")
            
    agent = ConcurrencyAgent()
    sched = setup_scheduler(plan, agent)
    sched.resource_manager.semaphore = asyncio.Semaphore(3)
    
    res = await sched.run()
    assert max_active <= 3
    assert len(res.completed_tasks) == 10