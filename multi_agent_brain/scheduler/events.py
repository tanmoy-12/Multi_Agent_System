# multi_agent_brain/scheduler/events.py
import logging
import time

logger = logging.getLogger("scheduler.events")

class EventSystem:
    @staticmethod
    def emit(event: str, task_id: str = "", details: str = ""):
        timestamp = time.strftime("%H:%M:%S")
        msg = f"[{timestamp}] {event}"
        if task_id: msg += f" {task_id}"
        if details: msg += f" -> {details}"
        print(msg)
        logger.info(msg)