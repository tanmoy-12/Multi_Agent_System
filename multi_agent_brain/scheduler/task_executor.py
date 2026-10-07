# multi_agent_brain/scheduler/task_executor.py
import asyncio
import time
from .agent_selector import AgentSelector
from .input_resolver import InputResolver
from .output_manager import OutputManager
from .execution_context import ExecutionContext
from .events import EventSystem
from .retry_manager import RetryManager
from ..models.execution_plan import TaskExecutionDetail, TaskResult
from ..tools.registry import ToolRegistry

class TaskExecutor:
    def __init__(self, agent_selector: AgentSelector, input_resolver: InputResolver, 
                 output_manager: OutputManager, retry_manager: RetryManager, tool_registry: ToolRegistry):
        self.agent_selector = agent_selector
        self.input_resolver = input_resolver
        self.output_manager = output_manager
        self.retry_manager = retry_manager
        self.tool_registry = tool_registry

    async def execute(self, task: TaskExecutionDetail, user_goal: str) -> TaskResult:
        max_retries = getattr(task, 'max_retries', 2)
        timeout = getattr(task, 'timeout', 120)
        error_msg = "Unknown error"
        
        for attempt in range(1, max_retries + 1):
            start_time = time.time()
            try:
                if attempt > 1:
                    EventSystem.emit("TASK_RETRYING", task.task_id, f"Attempt {attempt}")
                    delay = 2 ** (attempt - 1)
                    await asyncio.sleep(delay)
                    
                agent = self.agent_selector.select_agent(task)
                if not agent:
                    raise ValueError("No capable agent found")
                    
                EventSystem.emit("AGENT_ASSIGNED", task.task_id, agent.agent_id)
                tools = self.tool_registry.get_tools(getattr(task, 'required_tools', []))
                resolved_inputs = self.input_resolver.resolve(task)
                
                context = ExecutionContext(
                    task_id=task.task_id,
                    user_goal=user_goal,
                    task_description=task.description,
                    resolved_inputs=resolved_inputs,
                    available_tools=tools
                )
                
                EventSystem.emit("TASK_STARTED", task.task_id)
                result = await asyncio.wait_for(agent.execute(context), timeout=timeout)
                
                if getattr(task, 'output_schema', None) and not self._validate_output(result.output, task.output_schema):
                    raise ValueError("Output validation failed against schema")
                    
                result.execution_time = time.time() - start_time
                result.agent_id = agent.agent_id
                result.attempt = attempt
                result.status = "success"
                
                EventSystem.emit("TASK_SUCCEEDED", task.task_id)
                return result
                
            except asyncio.TimeoutError:
                error_msg = "Execution timed out"
                EventSystem.emit("TASK_FAILED", task.task_id, error_msg)
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                EventSystem.emit("TASK_FAILED", task.task_id, error_msg)
                
        return TaskResult(
            task_id=task.task_id,
            status="failed",
            output=None,
            error=error_msg,
            execution_time=time.time() - start_time,
            attempt=max_retries
        )

    def _validate_output(self, output, schema):
        if isinstance(schema, dict):
            if 'type' in schema and type(output).__name__ != schema['type']:
                return False
        return True