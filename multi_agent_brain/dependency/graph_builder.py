import networkx as nx
from ..models.task import Task
from ..models.dependency import DependencyEdge
import logging

logger = logging.getLogger(__name__)

class GraphBuilder:
    def build_graph(self, tasks: list[Task], edges: list[DependencyEdge]) -> nx.DiGraph:
        G = nx.DiGraph()
        for task in tasks:
            G.add_node(task.task_id, **task.model_dump())
            
        for edge in edges:
            if G.has_node(edge.from_task) and G.has_node(edge.to_task):
                if not G.has_edge(edge.from_task, edge.to_task):
                    G.add_edge(edge.from_task, edge.to_task, 
                               reason=edge.reason, confidence=edge.confidence, score=edge.score)
        return G