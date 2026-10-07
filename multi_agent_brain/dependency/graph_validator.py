import networkx as nx
from ..llm.base import LLMProvider
from ..llm.prompts import CYCLE_REPAIR_PROMPT
from ..utils.json_parser import extract_json
import logging

logger = logging.getLogger(__name__)

class GraphValidator:
    def __init__(self, llm_provider: LLMProvider = None):
        self.llm_provider = llm_provider

    def validate(self, graph: nx.DiGraph) -> bool:
        if not nx.is_directed_acyclic_graph(graph): return False
        if list(nx.selfloop_edges(graph)): return False
        return True

    async def repair_cycles(self, graph: nx.DiGraph) -> nx.DiGraph:
        if nx.is_directed_acyclic_graph(graph): return graph
        logger.warning("Attempting to repair cycles using LLM...")
        
        try:
            cycles = list(nx.simple_cycles(graph))
            if not cycles: return graph
                
            cycle = cycles[0]
            cycle_tasks, cycle_edges = [], []
            for i in range(len(cycle)):
                u, v = cycle[i], cycle[(i + 1) % len(cycle)]
                cycle_tasks.append(f"{u}: {graph.nodes[u].get('description', '')}")
                cycle_edges.append(f"{u} -> {v}")
                
            prompt = CYCLE_REPAIR_PROMPT.format(
                cycle_tasks="\n".join(cycle_tasks), cycle_edges="\n".join(cycle_edges))
            
            if self.llm_provider:
                response = await self.llm_provider.generate(prompt)
                data = extract_json(response)
                if "edge_to_remove" in data and data["edge_to_remove"]:
                    u, v = data["edge_to_remove"].get("from"), data["edge_to_remove"].get("to")
                    if graph.has_edge(u, v): graph.remove_edge(u, v)
                elif "edge_to_reverse" in data and data["edge_to_reverse"]:
                    u, v = data["edge_to_reverse"].get("from"), data["edge_to_reverse"].get("to")
                    if graph.has_edge(u, v):
                        graph.remove_edge(u, v)
                        graph.add_edge(v, u, reason="Reversed by LLM repair")
            
            # Deterministic fallback
            while not nx.is_directed_acyclic_graph(graph):
                try:
                    cycle = nx.find_cycle(graph, orientation='original')
                    u, v, _ = cycle[-1]
                    graph.remove_edge(u, v)
                except nx.NetworkXNoCycle: break
        except Exception as e:
            logger.error(f"Cycle repair failed: {e}")
            
        return graph