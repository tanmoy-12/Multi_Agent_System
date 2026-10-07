import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
import networkx as nx
from multi_agent_brain.planning.execution_planner import ExecutionPlanner

def test_execution_stages():
    G = nx.DiGraph()
    G.add_edges_from([
        ("T1", "T4"), ("T2", "T4"),
        ("T3", "T5"),
        ("T4", "T6"), ("T5", "T6")
    ])
    
    planner = ExecutionPlanner()
    stages = planner.generate_stages(G)
    
    assert len(stages) == 3
    assert sorted(stages[0].tasks) == ["T1", "T2", "T3"]
    assert stages[0].parallel is True
    assert sorted(stages[1].tasks) == ["T4", "T5"]
    assert stages[2].tasks == ["T6"]