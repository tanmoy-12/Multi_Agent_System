# multi_agent_brain/scheduler/scheduler.py
import asyncio
import time
from ..models.execution_plan import ExecutionPlan, ExecutionResult
from .dependency_manager import DependencyManager
from .task_queue import ReadyQueue
from .resource_manager import ResourceManager
from .task_executor import TaskExecutor
from .output_manager import OutputManager
from .events import EventSystem
from .task_state import TaskState

class Scheduler:
    def __init__(self, plan: ExecutionPlan, executor: TaskExecutor, max_concurrent: int = 5):
        self.plan = plan
        self.dep_manager = DependencyManager(plan)
        self.queue = ReadyQueue()
        self.resource_manager = ResourceManager(max_concurrent)
        self.executor = executor
        self.output_manager = OutputManager(plan.plan_id)
        self.is_paused = False
        self.is_cancelled = False
        self.task_map = {t.task_id: t for t in plan.tasks}

    async def run(self) -> ExecutionResult:
        start_time = time.time()
        EventSystem.emit("PLAN_STARTED", details=self.plan.plan_id)
        
        for task_id in self.dep_manager.get_ready_tasks():
            self.queue.push(task_id, self.task_map[task_id].priority)
            
        running_tasks = set()
        
        while not self.dep_manager.is_plan_complete() and not self.is_cancelled:
            if self.is_paused:
                await asyncio.sleep(0.5)
                continue
                
            while not self.queue.is_empty() and len(running_tasks) < self.resource_manager.semaphore._value:
                task_id = self.queue.pop()
                if self.dep_manager.states[task_id] == TaskState.READY:
                    self.dep_manager.mark_running(task_id)
                    task = asyncio.create_task(self._run_task(task_id))
                    running_tasks.add(task)
                    
            if not running_tasks:
                break
                
            done, running_tasks = await asyncio.wait(running_tasks, return_when=asyncio.FIRST_COMPLETED)
            
            for task in done:
                result = task.result()
                self.output_manager.store_result(result)
                
                if result.status == "success":
                    self.dep_manager.mark_succeeded(result.task_id)
                else:
                    self.dep_manager.mark_failed(result.task_id)
                    
                for ready_id in self.dep_manager.get_ready_tasks():
                    if self.dep_manager.states[ready_id] == TaskState.READY:
                        self.queue.push(ready_id, self.task_map[ready_id].priority)

        EventSystem.emit("PLAN_COMPLETED", details=self.plan.plan_id)
        return self._generate_result(time.time() - start_time)

    async def _run_task(self, task_id: str):
        await self.resource_manager.acquire()
        try:
            task = self.task_map[task_id]
            return await self.executor.execute(task, self.plan.user_goal)
        finally:
            self.resource_manager.release()

    def _generate_result(self, total_time: float) -> ExecutionResult:
        completed = [tid for tid, st in self.dep_manager.states.items() if st == TaskState.SUCCEEDED]
        failed = [tid for tid, st in self.dep_manager.states.items() if st == TaskState.FAILED]
        blocked = [tid for tid, st in self.dep_manager.states.items() if st == TaskState.BLOCKED]
        
        final_output = None
        terminal_tasks = self.dep_manager.get_final_tasks()
        if terminal_tasks:
            for tid in terminal_tasks:
                res = self.output_manager.get_result(tid)
                if res and res.status == "success":
                    final_output = res.output
                    break
                    
        status = "completed" if not failed and not blocked else "partial_success" if completed else "failed"
        
        return ExecutionResult(
            plan_id=self.plan.plan_id,
            status=status,
            completed_tasks=completed,
            failed_tasks=failed,
            blocked_tasks=blocked,
            task_results=self.output_manager.get_all_results(),
            final_output=final_output,
            total_execution_time=total_time
        )

    def pause(self): self.is_paused = True
    def resume(self): self.is_paused = False
    def cancel(self): self.is_cancelled = True