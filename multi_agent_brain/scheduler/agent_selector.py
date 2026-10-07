# multi_agent_brain/scheduler/agent_selector.py
from ..agents.registry import AgentRegistry
from ..models.execution_plan import TaskExecutionDetail

class AgentSelector:
    def __init__(self, agent_registry: AgentRegistry):
        self.registry = agent_registry

    def select_agent(self, task: TaskExecutionDetail):
        required_caps = set(getattr(task, 'required_capabilities', []))
        required_tools = set(getattr(task, 'required_tools', []))
        
        if not required_caps and hasattr(task, 'agent_type'):
            agent = self.registry.get_by_id(task.agent_type)
            if agent: return agent

        best_agent = None
        max_score = -1
        
        for agent in self.registry.get_all():
            agent_caps = set(agent.capabilities)
            agent_tools = set(agent.supported_tools)
            
            if not required_tools.issubset(agent_tools):
                continue
                
            score = len(required_caps.intersection(agent_caps))
            
            if hasattr(task, 'agent_type') and agent.agent_id == task.agent_type:
                score += 10 
                
            if score > max_score:
                max_score = score
                best_agent = agent
                
        return best_agent