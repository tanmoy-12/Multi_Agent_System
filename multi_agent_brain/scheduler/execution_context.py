from pydantic import BaseModel, ConfigDict  # Import ConfigDict
from typing import Dict, Any, List
from ..tools.base import BaseTool

class ExecutionContext(BaseModel):
    # Replace the old class Config with this:
    model_config = ConfigDict(arbitrary_types_allowed=True)

    task_id: str
    user_goal: str
    task_description: str
    resolved_inputs: Dict[str, Any]
    available_tools: List[BaseTool]
    metadata: Dict[str, Any] = {}