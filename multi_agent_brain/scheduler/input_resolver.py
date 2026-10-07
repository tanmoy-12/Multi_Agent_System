# multi_agent_brain/scheduler/input_resolver.py
from typing import Dict, Any
from ..models.execution_plan import TaskExecutionDetail
from .output_manager import OutputManager

class InputResolver:
    def __init__(self, output_manager: OutputManager):
        self.output_manager = output_manager

    def resolve(self, task: TaskExecutionDetail) -> Dict[str, Any]:
        inputs = {}
        for dep_id in task.dependencies:
            dep_result = self.output_manager.get_result(dep_id)
            if dep_result and dep_result.output:
                inputs[dep_id] = dep_result.output
        return inputs