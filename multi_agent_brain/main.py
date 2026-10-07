import os
# Define absolute paths based on the script's actual location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

import asyncio
import argparse
import logging
import sys
import os
from typing import List
import networkx as nx
import matplotlib.pyplot as plt

# Add parent directory to path to allow absolute imports when running as script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from multi_agent_brain.config import settings
from multi_agent_brain.models.task import Task
from multi_agent_brain.models.dependency import DependencyEdge
from multi_agent_brain.models.execution_plan import ExecutionPlan, TaskExecutionDetail
from multi_agent_brain.llm.ollama import OllamaLLMProvider
from multi_agent_brain.embeddings.sentence_transformer import SentenceTransformerEmbeddingProvider
from multi_agent_brain.decomposition.task_decomposer import TaskDecomposer
from multi_agent_brain.dependency.candidate_generator import CandidateGenerator
from multi_agent_brain.dependency.dependency_reasoner import DependencyReasoner
from multi_agent_brain.dependency.graph_builder import GraphBuilder
from multi_agent_brain.dependency.graph_validator import GraphValidator
from multi_agent_brain.planning.execution_planner import ExecutionPlanner
from multi_agent_brain.planning.agent_selector import AgentSelector
from multi_agent_brain.utils.logger import setup_logger

logger = setup_logger()

class AgentBrain:
    def __init__(self):
        self.llm_provider = OllamaLLMProvider()
        self.embedding_provider = SentenceTransformerEmbeddingProvider()
        self.decomposer = TaskDecomposer(self.llm_provider)
        self.candidate_generator = CandidateGenerator(self.embedding_provider)
        self.reasoner = DependencyReasoner(self.llm_provider)
        self.graph_builder = GraphBuilder()
        self.validator = GraphValidator(self.llm_provider)
        self.planner = ExecutionPlanner()
        self.agent_selector = AgentSelector()

    async def plan(self, user_goal: str) -> ExecutionPlan:
        print("\n========================================")
        print("MULTI-AGENT BRAIN")
        print("========================================")
        
        print("\n[1/6] Decomposing task...")
        tasks = await self.decomposer.decompose(user_goal)
        logger.info(f"[DECOMPOSER] Generated {len(tasks)} atomic tasks.")

        print("[2/6] Generating embeddings...")
        embeddings = self.candidate_generator.generate_embeddings(tasks)
        logger.info(f"[EMBEDDING] Generated embeddings for {len(tasks)} tasks.")

        print("[3/6] Finding candidate dependencies...")
        candidates = self.candidate_generator.generate_candidates(tasks, embeddings)
        logger.info(f"[DEPENDENCY] Generated {len(candidates)} candidate edges.")

        print("[4/6] Reasoning about dependencies...")
        task_map = {t.task_id: t for t in tasks}
        edges: List[DependencyEdge] = []
        
        # Async concurrent LLM calls for candidate reasoning
        reasoning_tasks = [
            self.reasoner.reason_pair(task_map[id_a], task_map[id_b], sim) 
            for id_a, id_b, sim in candidates
        ]
        results = await asyncio.gather(*reasoning_tasks)
        for res in results:
            if res:
                edges.append(res)
                logger.info(f"[REASONER] {res.from_task} -> {res.to_task} (Score: {res.score:.2f})")

        print("[5/6] Building and validating DAG...")
        graph = self.graph_builder.build_graph(tasks, edges)
        
        if not self.validator.validate(graph):
            logger.warning("[GRAPH] Initial graph has cycles. Attempting repair...")
            graph = await self.validator.repair_cycles(graph)
            if not self.validator.validate(graph):
                raise ValueError("Failed to produce a valid DAG after repair.")
                
        logger.info(f"[GRAPH] Nodes: {graph.number_of_nodes()} | Edges: {graph.number_of_edges()} | DAG: VALID")

        print("[6/6] Generating execution plan...")
        stages = self.planner.generate_stages(graph)
        
        plan_tasks = []
        for t in tasks:
            agent = self.agent_selector.select_agent(t)
            deps = [e.from_task for e in edges if e.to_task == t.task_id]
            plan_tasks.append(TaskExecutionDetail(
                task_id=t.task_id, description=t.description,
                agent_type=agent, dependencies=deps, outputs=[t.expected_output]
            ))
            
        plan = ExecutionPlan(
            plan_id="plan_001", user_goal=user_goal,
            tasks=plan_tasks,
            dependency_graph={"edges": [e.model_dump(by_alias=True) for e in edges]},
            execution_stages=stages
        )
        
        self._print_plan(plan)
        self._save_graph(graph)
        return plan

    def _print_plan(self, plan: ExecutionPlan):
        print("\n========================================")
        print("EXECUTION PLAN")
        print("========================================")
        for stage in plan.execution_stages:
            mode = "PARALLEL" if stage.parallel else "SEQUENTIAL"
            print(f"\nStage {stage.stage} [{mode}]")
            for tid in stage.tasks:
                desc = next((t.description for t in plan.tasks if t.task_id == tid), "")
                print(f" - {tid}: {desc}")
                
    def _save_graph(self, graph: nx.DiGraph):
        try:
            plt.figure(figsize=(10, 6))
            pos = nx.spring_layout(graph)
            nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=2000, 
                    font_size=10, font_weight='bold', arrows=True)
            plt.title("Dependency Graph")
            
            # Use the absolute OUTPUT_DIR
            graph_path = os.path.join(OUTPUT_DIR, "dependency_graph.png")
            plt.savefig(graph_path)
            plt.close()
            logger.info(f"Saved dependency graph to {graph_path}")
        except Exception as e:
            logger.error(f"Failed to save graph visualization: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Brain Orchestrator")
    parser.add_argument("task", type=str, help="The complex user task to plan.")
    parser.add_argument("--output", type=str, default="execution_plan.json", help="Output JSON file name.")
    args = parser.parse_args()
    
    brain = AgentBrain()
    plan = await brain.plan(args.task)
    
    # Save strictly inside the multi_agent_brain/outputs/ folder
    output_path = os.path.join(OUTPUT_DIR, args.output)
    plan.save(output_path)
    print(f"\nPlan saved to: {output_path}")

if __name__ == "__main__":
    asyncio.run(main())