import networkx as nx
from ..models.execution_plan import ExecutionStage
import logging

logger = logging.getLogger(__name__)

class ExecutionPlanner:
    def generate_stages(self, graph: nx.DiGraph) -> list[ExecutionStage]:
        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("Cannot generate stages for a graph with cycles.")
            
        generations = list(nx.topological_generations(graph))
        stages = []
        for i, gen in enumerate(generations):
            stages.append(ExecutionStage(
                stage=i + 1,
                parallel=len(gen) > 1,
                tasks=list(gen)
            ))
        return stages