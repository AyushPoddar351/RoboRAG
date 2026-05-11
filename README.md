# 🤖 RoboRAG — RAG-Powered Robot Task Planning with Continuous Learning

RoboRAG is a **Retrieval-Augmented Generation (RAG) system for autonomous robot task planning**. It retrieves semantically similar past experiences from a vector knowledge base, feeds them as context to a local LLM, and executes the generated action plan on a real or simulated robot via ROS2. Over time, it **learns from its own execution outcomes** — making it smarter with every run.

---

## How It Works

```
User (natural language task)
         │
         ▼
  ChromaDB Vector DB
  (semantic search → top-2 similar past experiences)
         │
         ▼
  Ollama LLM (gemma4:31b-cloud)
  (generates JSON action plan from retrieved context)
         │
         ▼
  ROS2 Executor Node
  (publishes TwistStamped msgs to /cmd_vel)
         │
         ▼
  TurtleBot3 moves
         │
         ▼
  Outcome Logger  ──────────────────────────────┐
  (user confirms success/failure)               │
         │                                      │
         └──── new experience written back ─────┘
               to ChromaDB (feedback loop)
```

1. **Seed** the knowledge base with past task experiences (once)
2. **Enter a task** in natural language (e.g. *"avoid obstacle on the left"*)
3. **ChromaDB** retrieves the 2 most semantically similar experiences
4. **Ollama LLM** generates a structured JSON action plan using retrieved context
5. **ROS2 executor** parses the plan and drives the robot step-by-step
6. **Outcome is logged back** to ChromaDB — the system learns from every run

---

## Tech Stack

| Component | Technology |
|---|---|
| Robot middleware | ROS2 Jazzy (`rclpy`) |
| Simulator | Gazebo + TurtleBot3 Burger |
| Vector database | ChromaDB (persistent, local) |
| Embeddings | `all-MiniLM-L6-v2` (ChromaDB default) |
| LLM inference | Ollama — `gemma4:31b-cloud` |
| Language | Python 3.10+ |

---

## Project Structure

```
Project-RoboRAG/
├── docs/
│   ├── setup.md              # Full setup and installation guide
│   ├── project_plan.md       # Weekly roadmap and progress tracker
│   └── feedback_loop.md      # Feedback loop design document
├── knowledge_base/
│   ├── task_memory.py        # Seeds ChromaDB with initial experiences
│   ├── outcome_logger.py     # Logs execution outcomes back to ChromaDB
│   └── chroma_store/         # Persistent ChromaDB vector store
├── planner/
│   └── rag_planner.py        # Standalone RAG planner (retrieval + LLM)
├── scripts/
│   ├── robot_mover.py        # Basic hardcoded ROS2 movement node
│   └── roborag_executor.py   # Full end-to-end executor node
├── demos/                    # Demo videos and recordings
└── logs/                     # Execution logs
```

---

## Quick Start

> **Full setup guide:** [`docs/setup.md`](docs/setup.md)

### 1. Install dependencies
```bash
pip install chromadb ollama
```

### 2. Seed the knowledge base
```bash
cd knowledge_base
python task_memory.py
```

### 3. Launch TurtleBot3 in Gazebo
```bash
source /opt/ros/jazzy/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### 4. Run RoboRAG
```bash
source /opt/ros/jazzy/setup.bash
python scripts/roborag_executor.py
```

```
Enter task: move forward slowly
Retrieving experiences and planning...
Raw plan: [{"linear_x": 0.2, "angular_z": 0.0, "duration": 5.0}]
Executing 1 steps...
Task complete. Robot stopped.
```

---

## Knowledge Base

The initial knowledge base is seeded with 5 task experiences:

| ID | Task | Outcome |
|---|---|---|
| `exp_001` | Move forward 1 meter | success |
| `exp_002` | Turn left 90 degrees | success |
| `exp_003` | Navigate to goal avoiding obstacle | success |
| `exp_004` | Patrol area | success |
| `exp_005` | Stop immediately | success |

Each execution run appends a new experience to the database, continuously improving retrieval quality.

---

## Project Status

| Week | Focus | Status |
|---|---|---|
| Week 1 | ROS2 setup, TurtleBot3, first node | ✅ Complete |
| Week 2 | ChromaDB knowledge base, RAG planner | ✅ Complete |
| Week 3 | End-to-end executor, feedback loop, evaluation | 🔄 In Progress |
| Week 4 | Code cleanup, README, GitHub packaging | ⬜ Not Started |

---

## Documentation

- [`docs/setup.md`](docs/setup.md) — Prerequisites, installation, and running instructions
- [`docs/project_plan.md`](docs/project_plan.md) — Full weekly roadmap and architecture breakdown
- [`docs/feedback_loop.md`](docs/feedback_loop.md) — Design doc for the continuous learning feedback loop

---

## Environment Notes

- Designed to run inside **WSL2** (Ubuntu 22.04) with Ollama on the Windows host
- Default Ollama host: `http://172.20.192.1:11434` — update in `rag_planner.py` and `roborag_executor.py` if your setup differs
- ChromaDB data is persisted to `knowledge_base/chroma_store/`
