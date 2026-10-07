# 🧠 Multi-Agent Orchestration System

A production-grade, two-phase AI orchestration engine designed to take complex, high-level user goals, break them down into atomic tasks, resolve dependencies, and execute them dynamically using autonomous AI agents.

## 🏗️ Architecture Overview

This system strictly separates **Planning** from **Execution** to ensure reliability, observability, and scalability.

### Phase 1: The Brain (Planner)
The Brain receives a complex natural language prompt and acts as an architect.
1. **Decomposition:** Breaks the goal into atomic, executable tasks.
2. **Hybrid Dependency Resolution:** Uses vector embeddings (cosine similarity) to find candidate dependencies, an LLM to reason about actual data flow, and deterministic graph algorithms to validate the structure.
3. **DAG Generation:** Constructs a Directed Acyclic Graph (DAG) using NetworkX.
4. **Self-Healing:** Detects logical cycles and uses the LLM to repair them.
5. **Output:** Generates a strict, machine-readable `execution_plan.json`.

### Phase 2: The Scheduler (Orchestrator)
The Scheduler consumes the `execution_plan.json` and acts as the runtime engine.
1. **Dynamic State Machine:** Tracks tasks through states (`PENDING` -> `READY` -> `RUNNING` -> `SUCCEEDED`/`FAILED`).
2. **Capability-Based Routing:** Ignores hardcoded agent hints and dynamically selects the best available agent based on required capabilities and tool access.
3. **Async Parallel Execution:** Executes independent branches concurrently using `asyncio` and semaphores.
4. **Failure Propagation:** If a task fails permanently, downstream dependent tasks are automatically marked as `BLOCKED`, while unrelated branches continue executing.
5. **Output Management:** Validates agent outputs against schemas and passes resolved data to downstream tasks.

```text
[ USER TASK ] 
      │
      ▼
┌─────────────────────────────┐
│      BRAIN / PLANNER        │  <-- LLM + Embeddings + NetworkX
│  (Decompose -> DAG -> JSON) │
└─────────────┬───────────────┘
              │ execution_plan.json
              ▼
┌─────────────────────────────┐
│    SCHEDULER / ORCHESTRATOR │  <-- Asyncio + State Machine
│ (Route -> Execute -> Store) │
└─────────────┬───────────────┘
              │
      ┌───────┴───────┬───────────────┐
      ▼               ▼               ▼
[Research Agent] [Coding Agent] [Data Agent]