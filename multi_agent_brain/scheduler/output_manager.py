# multi_agent_brain/scheduler/output_manager.py
import os
import json
from typing import Dict, Optional
from ..models.execution_plan import TaskResult

class OutputManager:
    def __init__(self, plan_id: str, base_dir: str = "outputs"):
        self.plan_id = plan_id
        self.base_dir = base_dir
        self.results: Dict[str, TaskResult] = {}
        self.plan_dir = os.path.join(base_dir, plan_id)
        os.makedirs(self.plan_dir, exist_ok=True)

    def store_result(self, result: TaskResult):
        self.results[result.task_id] = result
        path = os.path.join(self.plan_dir, f"{result.task_id}.json")
        with open(path, "w") as f:
            json.dump(result.model_dump(), f, indent=2)

    def get_result(self, task_id: str) -> Optional[TaskResult]:
        return self.results.get(task_id)
        
    def get_all_results(self) -> Dict[str, TaskResult]:
        return self.results