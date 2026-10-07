DECOMPOSE_PROMPT = """You are an expert task decomposer for a multi-agent AI system.
Break down the user task into atomic, executable, and independent tasks.

RULES:
1. Every task must represent one meaningful executable operation.
2. Avoid unnecessarily tiny tasks or combining independent operations.
3. A task should have clear inputs and expected outputs.
4. Do not create dependencies during decomposition unless absolutely obvious.

Return STRICT JSON matching this schema:
{{
  "tasks": [
    {{
      "task_id": "T1",
      "description": "Brief description",
      "objective": "Goal of task",
      "inputs": ["List of inputs"],
      "expected_output": "Output produced",
      "required_capabilities": ["capability1"],
      "priority": "high|medium|low",
      "input_schema": "String description OR JSON object of input data structure",
      "output_schema": "String description OR JSON object of output data structure"
    }}
  ]
}}

User Task: {user_task}
"""

DEPENDENCY_REASONING_PROMPT = """You are a dependency reasoning engine for a DAG.
Given TASK A and TASK B, determine if a true execution dependency exists.

TASK A:
ID: {task_a_id}
Description: {task_a_desc}
Expected Output: {task_a_out}
Output Schema: {task_a_out_schema}

TASK B:
ID: {task_b_id}
Description: {task_b_desc}
Inputs: {task_b_in}
Input Schema: {task_b_in_schema}

Distinguish between semantic similarity (independent) and actual execution dependency.
Return STRICT JSON:
{{
  "relationship": "A_DEPENDS_ON_B" | "B_DEPENDS_ON_A" | "INDEPENDENT",
  "confidence": 0.0 to 1.0,
  "reason": "Explanation",
  "required_output": "Specific information flowing from parent to child (if dependent)"
}}
"""

CYCLE_REPAIR_PROMPT = """A cycle was detected in a task dependency graph.
Cycle tasks:
{cycle_tasks}

Current edges in cycle:
{cycle_edges}

Determine which edge is logically incorrect and should be removed or reversed to break the cycle.
Return STRICT JSON:
{{
  "edge_to_remove": {{"from": "T?", "to": "T?"}} or null,
  "edge_to_reverse": {{"from": "T?", "to": "T?"}} or null,
  "reason": "Explanation"
}}
"""