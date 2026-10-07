import numpy as np
from ..models.task import Task
from ..embeddings.base import EmbeddingProvider
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class CandidateGenerator:
    def __init__(self, embedding_provider: EmbeddingProvider):
        self.embedding_provider = embedding_provider
        self.threshold = settings.SIMILARITY_THRESHOLD
        self.max_candidates_total = settings.MAX_CANDIDATES_PER_TASK * 10  # Buffer

    def generate_embeddings(self, tasks: list[Task]) -> dict[str, list[float]]:
        embeddings = {}
        for task in tasks:
            text = f"{task.description} {task.objective} {' '.join(task.inputs)} {task.expected_output}"
            embeddings[task.task_id] = self.embedding_provider.embed(text)
        return embeddings

    def generate_candidates(self, tasks: list[Task], embeddings: dict[str, list[float]]) -> list[tuple[str, str, float]]:
        task_ids = [t.task_id for t in tasks]
        candidates = []
        
        for i in range(len(task_ids)):
            id_a = task_ids[i]
            vec_a = np.array(embeddings[id_a])
            
            for j in range(i + 1, len(task_ids)):
                id_b = task_ids[j]
                vec_b = np.array(embeddings[id_b])
                
                norm_a = np.linalg.norm(vec_a)
                norm_b = np.linalg.norm(vec_b)
                if norm_a == 0 or norm_b == 0: continue
                
                sim = np.dot(vec_a, vec_b) / (norm_a * norm_b)
                if sim >= self.threshold:
                    candidates.append((id_a, id_b, sim))
                    
        candidates.sort(key=lambda x: x[2], reverse=True)
        candidates = candidates[:self.max_candidates_total]
            
        logger.info(f"Generated {len(candidates)} candidate dependency pairs.")
        return candidates