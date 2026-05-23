# RoboRAG — Setup Guide

## Prerequisites

- Ubuntu 24.04 (or WSL2 on Windows with Ubuntu 24.04)
- ROS2 Jazzy installed and sourced
- Python 3.10+
- Ollama running (locally or on Windows host)
- TurtleBot3 packages installed

---

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/Project-RoboRAG.git
cd Project-RoboRAG
```

---

## 2. Install Python Dependencies

```bash
pip install chromadb ollama
```

> **Note:** `rclpy` and `geometry_msgs` are provided by your ROS2 installation — do not pip-install them.

---

## 3. Configure Ollama Host

By default, the scripts connect to Ollama at `http://172.20.192.1:11434`.  
This is the Windows host IP as seen from WSL2.

If your setup differs, update the host in:
- `planner/rag_planner.py` — line 9
- `scripts/roborag_executor.py` — line 16

```python
llm = ollama.Client(host='http://<YOUR_OLLAMA_HOST>:11434')
```

Ensure the model is pulled:
```bash
ollama pull gemma4:31b-cloud
```

---

## 4. Seed the Knowledge Base

Run this **once** to populate ChromaDB with the initial 5 task experiences:

```bash
cd knowledge_base
python task_memory.py
```

Expected output:
```
Knowledge base seeded with 5 experiences
Test retrieval for 'move robot forward':
  - Task: move forward 1 meter. Context: open corridor...
```

---

## 5. Launch TurtleBot3 in Gazebo

```bash
# In a separate terminal (source ROS2 first)
source /opt/ros/jazzy/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

---

## 6. Run the RoboRAG Executor

```bash
# Source ROS2 environment
source /opt/ros/jazzy/setup.bash

# Run the executor
python scripts/roborag_executor.py
```

You will be prompted:
```
Enter task: move forward slowly
Retrieving experiences and planning...
```

The executor will retrieve relevant past experiences, generate a JSON plan via Ollama, and publish velocity commands to `/cmd_vel`.

---

## Directory Structure

```
Project-RoboRAG/
├── docs/                        # Documentation
│   ├── setup.md                 # This file
│   ├── project_plan.md          # Weekly roadmap
│   └── feedback_loop.md         # Feedback loop design
├── knowledge_base/
│   ├── task_memory.py           # Seed script
│   ├── outcome_logger.py        # (Coming) Feedback logger
│   └── chroma_store/            # Persistent ChromaDB data
├── planner/
│   └── rag_planner.py           # Standalone RAG planner
├── scripts/
│   ├── robot_mover.py           # Basic movement node
│   └── roborag_executor.py      # Full end-to-end executor
├── demos/                       # Demo videos (coming)
└── logs/                        # Execution logs
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `Collection robot_tasks does not exist` | Run `task_memory.py` first to seed ChromaDB |
| `Cannot connect to Ollama` | Check that Ollama is running and the host IP is correct |
| `rclpy not found` | Source your ROS2 environment: `source /opt/ros/jazzy/setup.bash` |
| ChromaDB path errors | Ensure you run scripts from their expected working directories |
