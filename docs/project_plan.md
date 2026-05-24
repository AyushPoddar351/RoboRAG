# RoboRAG — Project Plan & Status

## Goal
Build a RAG-powered robot task planner that retrieves past task experiences from a vector knowledge base, uses an LLM to generate action plans, executes them via ROS2, and **learns from outcomes over time via a feedback loop**.

---

## Weekly Roadmap

### Week 1 — ROS2 & Robot Setup ✅ COMPLETE
- [x] ROS2 Jazzy installed and verified
- [x] TurtleBot3 running in Gazebo simulation
- [x] Sensor topics confirmed active: `/scan`, `/odom`, `/imu`, `/cmd_vel`
- [x] First ROS2 Python node written (`scripts/robot_mover.py`)

### Week 2 — RAG Knowledge Base ✅ COMPLETE
- [x] ChromaDB knowledge base seeded with 5 task experiences
- [x] Semantic retrieval working (model: `all-MiniLM-L6-v2` embeddings via ChromaDB default)
- [x] RAG planner connecting ChromaDB + Ollama (`planner/rag_planner.py`)
- [x] Full pipeline tested: NL task → retrieval → LLM plan generation

### Week 3 — Execution & Feedback Loop ✅ COMPLETE
- [x] ROS2 executor node built (`scripts/roborag_executor.py`)
- [x] Full end-to-end pipeline working: NL → ChromaDB → LLM → ROS2 → Robot moves
- [x] **Feedback loop** — log execution outcomes back to ChromaDB (completed)
- [x] **Evaluation** — RAG vs zero-shot planning comparison (10 test tasks)

### Week 4 — Polish & Publication 🔄 IN PROGRESS
- [x] Clean up code, add docstrings throughout
- [x] Complete README with architecture diagram
- [x] GitHub packaging (proper repo structure, `.gitignore`, `requirements.txt`)
- [ ] Demo video recording
- [ ] LinkedIn post
- [ ] Resume bullet finalized

---

## Architecture Summary

```
User (NL Task)
     │
     ▼
ChromaDB (vector search → top-2 similar experiences)
     │
     ▼
Ollama LLM (gemma4:31b-cloud) → JSON action plan
     │
     ▼
RoboRAGExecutor (ROS2 node) → /cmd_vel → TurtleBot3
     │
     ▼
Outcome Logger → ChromaDB (feedback loop) ← NEXT
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Robot middleware | ROS2 Jazzy (`rclpy`) |
| Simulator | Gazebo + TurtleBot3 |
| Vector DB | ChromaDB (persistent, local) |
| LLM inference | Ollama (`gemma4:31b-cloud`) |
| Embeddings | `all-MiniLM-L6-v2` (ChromaDB default) |
| Language | Python 3 |

---

## Key Files

| File | Purpose |
|---|---|
| `scripts/robot_mover.py` | Basic ROS2 movement node (Week 1 test) |
| `knowledge_base/task_memory.py` | Seeds ChromaDB with initial experiences |
| `planner/rag_planner.py` | Standalone RAG planner (retrieval + LLM) |
| `scripts/roborag_executor.py` | Full end-to-end ROS2 executor node |
| `knowledge_base/chroma_store/` | Persistent ChromaDB vector store |
