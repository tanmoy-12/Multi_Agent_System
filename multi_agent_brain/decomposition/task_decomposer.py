from ..llm.base import LLMProvider
from ..llm.prompts import DECOMPOSE_PROMPT
from ..models.task import Task, TaskDecompositionResult
from ..utils.json_parser import parse_and_validate
import logging

logger = logging.getLogger(__name__)

class TaskDecomposer:
    def __init__(self, llm_provider: LLMProvider, max_retries: int = 2):
        self.llm_provider = llm_provider
        self.max_retries = max_retries

    async def decompose(self, user_task: str) -> list[Task]:
        prompt = DECOMPOSE_PROMPT.format(user_task=user_task)
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Decomposing task (Attempt {attempt + 1})...")
                response = await self.llm_provider.generate(prompt)
                result = parse_and_validate(response, TaskDecompositionResult)
                logger.info(f"Decomposer generated {len(result.tasks)} atomic tasks.")
                return result.tasks
            except Exception as e:
                logger.error(f"Decomposition failed on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries:
                    raise ValueError(f"Failed to decompose task after {self.max_retries} attempts.") from e