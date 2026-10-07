from ..models.task import Task
import logging

logger = logging.getLogger(__name__)

class AgentCapabilityRegistry:
    def __init__(self):
        self.registry = {
            "research_agent": ["web_research", "information_extraction", "price_search", "search", "research"],
            "coding_agent": ["python", "software_development", "coding", "scripting"],
            "data_agent": ["pandas", "data_analysis", "statistics", "data_processing", "calculation"],
            "vision_agent": ["image_analysis", "OCR", "computer_vision"],
            "reasoning_agent": ["reasoning", "planning", "comparison", "evaluation", "recommendation"],
            "writing_agent": ["report_generation", "writing", "summarization", "text_generation"]
        }

class AgentSelector:
    def __init__(self):
        self.registry = AgentCapabilityRegistry()

    def select_agent(self, task: Task) -> str:
        required = set([c.lower() for c in task.required_capabilities])
        if not required: return "reasoning_agent"
            
        best_agent, max_score = "reasoning_agent", 0
        for agent_type, caps in self.registry.registry.items():
            score = len(required.intersection(set([c.lower() for c in caps])))
            if score > max_score:
                max_score, best_agent = score, agent_type
        return best_agent