# multi_agent_brain/scheduler/dependency_manager.py
import networkx as nx
from typing import Dict, List
from ..models.execution_plan import ExecutionPlan
from .task_state import TaskState

class DependencyManager:
    def __init__(self, plan: ExecutionPlan):
        self.plan = plan
        self.graph = nx.DiGraph()
        self.states: Dict[str, TaskState] = {}
        
        for task in plan.tasks:
            self.graph.add_node(task.task_id)
            self.states[task.task_id] = TaskState.PENDING
            
        edges = plan.dependency_graph.get("edges", [])
        for edge in edges:
            u = edge.get("from") if isinstance(edge, dict) else getattr(edge, "from_task", None)
            v = edge.get("to") if isinstance(edge, dict) else getattr(edge, "to_task", None)
            if u and v:
                self.graph.add_edge(u, v)
                
        self._initialize_states()

    def _initialize_states(self):
        for task_id in self.graph.nodes:
            if self.graph.in_degree(task_id) == 0:
                self.states[task_id] = TaskState.READY
            else:
                self.states[task_id] = TaskState.WAITING_FOR_DEPENDENCIES

    def get_ready_tasks(self) -> List[str]:
        return [tid for tid, state in self.states.items() if state == TaskState.READY]

    def mark_succeeded(self, task_id: str):
        self.states[task_id] = TaskState.SUCCEEDED
        for successor in self.graph.successors(task_id):
            if self.states[successor] == TaskState.WAITING_FOR_DEPENDENCIES:
                preds = list(self.graph.predecessors(successor))
                if all(self.states[p] == TaskState.SUCCEEDED for p in preds):
                    self.states[successor] = TaskState.READY

    def mark_failed(self, task_id: str):
        self.states[task_id] = TaskState.FAILED
        self._block_descendants(task_id)

    def _block_descendants(self, task_id: str):
        for descendant in nx.descendants(self.graph, task_id):
            if self.states[descendant] not in [TaskState.SUCCEEDED, TaskState.FAILED, TaskState.BLOCKED]:
                self.states[descendant] = TaskState.BLOCKED

    def mark_running(self, task_id: str):
        self.states[task_id] = TaskState.RUNNING

    def is_plan_complete(self) -> bool:
        active_states = {TaskState.PENDING, TaskState.WAITING_FOR_DEPENDENCIES, 
                         TaskState.READY, TaskState.ASSIGNED, TaskState.RUNNING, TaskState.RETRYING}
        return not any(state in active_states for state in self.states.values())
        
    def get_final_tasks(self) -> List[str]:
        return [n for n in self.graph.nodes if self.graph.out_degree(n) == 0]