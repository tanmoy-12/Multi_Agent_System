from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import os

class TaskExecutionDetail(BaseModel):
    task_id: str
    description: str
    agent_type: str = "reasoning_agent"
    dependencies: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    required_capabilities: List[str] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)
    # Allow both dict and str
    input_schema: Optional[Union[dict, str]] = None
    output_schema: Optional[Union[dict, str]] = None
    priority: str = "medium"
    timeout: int = 120
    max_retries: int = 2

class ExecutionStage(BaseModel):
    stage: int
    parallel: bool
    tasks: List[str]

class ExecutionPlan(BaseModel):
    plan_id: str
    user_goal: str
    tasks: List[TaskExecutionDetail]
    dependency_graph: dict
    execution_stages: List[ExecutionStage] = Field(default_factory=list)

    def to_json(self) -> str:
        return self.model_dump_json(indent=2, by_alias=True)

    def save(self, path: str):
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(path, "w") as f:
            f.write(self.to_json())

class TaskResult(BaseModel):
    task_id: str
    status: str
    output: Any = None
    artifacts: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    execution_time: float = 0.0
    agent_id: str = ""
    error: Optional[str] = None
    attempt: int = 1

class ExecutionResult(BaseModel):
    plan_id: str
    status: str
    completed_tasks: List[str]
    failed_tasks: List[str]
    blocked_tasks: List[str]
    task_results: Dict[str, TaskResult]
    final_output: Any = None
    total_execution_time: float = 0.0