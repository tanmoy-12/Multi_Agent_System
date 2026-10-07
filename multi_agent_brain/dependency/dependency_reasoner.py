from ..llm.base import LLMProvider
from ..llm.prompts import DEPENDENCY_REASONING_PROMPT
from ..models.task import Task
from ..models.dependency import DependencyDecision, DependencyEdge, DependencyScore
from ..utils.json_parser import parse_and_validate
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class DependencyReasoner:
    def __init__(self, llm_provider: LLMProvider, max_retries: int = 2):
        self.llm_provider = llm_provider
        self.max_retries = max_retries
        self.weights = settings.DEPENDENCY_WEIGHTS

    def calculate_io_match(self, task_a: Task, task_b: Task) -> float:
        score = 0.0
        if task_a.output_schema and task_b.input_schema:
            # Safely convert to string whether it's a dict or a str
            out_a = str(task_a.output_schema).lower()
            in_b = str(task_b.input_schema).lower()
            
            if out_a in in_b or in_b in out_a:
                score = 1.0
            else:
                words_a = set(out_a.split())
                words_b = set(in_b.split())
                if words_a and words_b:
                    overlap = len(words_a.intersection(words_b))
                    score = overlap / max(len(words_a), len(words_b))
                    
        if task_a.expected_output and task_b.inputs:
            for inp in task_b.inputs:
                if task_a.expected_output.lower() in inp.lower() or inp.lower() in task_a.expected_output.lower():
                    score = max(score, 1.0)
        return score

    async def reason_pair(self, task_a: Task, task_b: Task, semantic_sim: float) -> DependencyEdge | None:
        prompt = DEPENDENCY_REASONING_PROMPT.format(
            task_a_id=task_a.task_id, task_a_desc=task_a.description,
            task_a_out=task_a.expected_output, task_a_out_schema=str(task_a.output_schema or ""),
            task_b_id=task_b.task_id, task_b_desc=task_b.description,
            task_b_in=", ".join(task_b.inputs), task_b_in_schema=str(task_b.input_schema or "")
        )

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.llm_provider.generate(prompt)
                decision = parse_and_validate(response, DependencyDecision)
                
                if decision.relationship == "INDEPENDENT":
                    return None
                
                io_match = self.calculate_io_match(task_a, task_b)
                w = self.weights
                total = (w['semantic'] * semantic_sim +
                         w['io'] * io_match +
                         w['llm'] * decision.confidence)

                if decision.relationship == "A_DEPENDS_ON_B":
                    return DependencyEdge(from_task=task_b.task_id, to_task=task_a.task_id,
                                          reason=decision.reason, confidence=decision.confidence, score=total)
                elif decision.relationship == "B_DEPENDS_ON_A":
                    return DependencyEdge(from_task=task_a.task_id, to_task=task_b.task_id,
                                          reason=decision.reason, confidence=decision.confidence, score=total)
            except Exception as e:
                logger.error(f"Reasoning failed for {task_a.task_id}-{task_b.task_id}: {e}")
                if attempt == self.max_retries: return None
        return None