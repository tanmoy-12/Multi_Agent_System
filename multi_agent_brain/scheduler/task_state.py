# multi_agent_brain/scheduler/task_state.py
from enum import Enum

class TaskState(str, Enum):
    PENDING = "PENDING"
    WAITING_FOR_DEPENDENCIES = "WAITING_FOR_DEPENDENCIES"
    READY = "READY"
    ASSIGNED = "ASSIGNED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"