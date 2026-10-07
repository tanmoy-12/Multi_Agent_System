# multi_agent_brain/agents/registry.py
from typing import List
from .base import BaseAgent

class AgentRegistry:
    def __init__(self):
        self.agents = {}

    def register(self, agent: BaseAgent):
        self.agents[agent.agent_id] = agent

    def get_by_id(self, agent_id: str) -> BaseAgent:
        return self.agents.get(agent_id)

    def get_all(self) -> List[BaseAgent]:
        return list(self.agents.values())