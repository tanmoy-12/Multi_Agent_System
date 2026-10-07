from pydantic import BaseModel, Field
from typing import List, Optional, Union

class Task(BaseModel):
    task_id: str
    description: str
    objective: str = ""
    inputs: List[str] = Field(default_factory=list)
    expected_output: str = ""
    required_capabilities: List[str] = Field(default_factory=list)
    priority: str = "medium"
    timeout: int = 120
    max_retries: int = 2
    # Allow both dict (strict JSON) and str (LLM natural language description)
    input_schema: Optional[Union[dict, str]] = None
    output_schema: Optional[Union[dict, str]] = None

class TaskDecompositionResult(BaseModel):
    tasks: List[Task]