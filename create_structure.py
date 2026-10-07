from pathlib import Path


# Root directory
ROOT = Path("multi_agent_brain")

# Directories to create
DIRECTORIES = [
    "models",
    "llm",
    "embeddings",
    "decomposition",
    "dependency",
    "planning",
    "agents",
    "utils",
    "tests",
    "outputs",
]

# Files to create
FILES = [
    "README.md",
    "requirements.txt",
    ".env.example",
    "config.py",
    "main.py",

    # models
    "models/__init__.py",
    "models/task.py",
    "models/dependency.py",
    "models/execution_plan.py",

    # llm
    "llm/__init__.py",
    "llm/base.py",
    "llm/ollama.py",
    "llm/prompts.py",

    # embeddings
    "embeddings/__init__.py",
    "embeddings/base.py",
    "embeddings/sentence_transformer.py",

    # decomposition
    "decomposition/__init__.py",
    "decomposition/task_decomposer.py",

    # dependency
    "dependency/__init__.py",
    "dependency/candidate_generator.py",
    "dependency/dependency_reasoner.py",
    "dependency/graph_builder.py",
    "dependency/graph_validator.py",

    # planning
    "planning/__init__.py",
    "planning/execution_planner.py",
    "planning/agent_selector.py",

    # agents
    "agents/__init__.py",
    "agents/base.py",
    "agents/registry.py",

    # utils
    "utils/__init__.py",
    "utils/json_parser.py",
    "utils/logger.py",

    # tests
    "tests/__init__.py",
    "tests/test_decomposition.py",
    "tests/test_dependencies.py",
    "tests/test_graph.py",
    "tests/test_planner.py",
]


def create_project_structure():
    print("=" * 60)
    print("Creating Multi-Agent Brain Project")
    print("=" * 60)

    # Create root directory
    ROOT.mkdir(parents=True, exist_ok=True)
    print(f"[DIR]  {ROOT}/")

    # Create directories
    for directory in DIRECTORIES:
        path = ROOT / directory
        path.mkdir(parents=True, exist_ok=True)
        print(f"[DIR]  {path}/")

    # Create files
    for file in FILES:
        path = ROOT / file

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Create empty file
        if not path.exists():
            path.touch()
            print(f"[FILE] {path}")
        else:
            print(f"[SKIP] {path} already exists")

    print("\n" + "=" * 60)
    print("Project structure created successfully!")
    print("=" * 60)

    print("\nLocation:")
    print(ROOT.resolve())

    print("\nNext step:")
    print("cd multi_agent_brain")


if __name__ == "__main__":
    create_project_structure()