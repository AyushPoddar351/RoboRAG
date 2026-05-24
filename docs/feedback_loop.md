# Continuous Learning Feedback Loop

The core feature of RoboRAG that distinguishes it from standard zero-shot LLM planners is its **continuous learning feedback loop**.

## How it Works

1. **Task Execution**: The user requests a task, the LLM generates a JSON action plan based on retrieved past experiences, and the ROS2 executor node drives the robot.
2. **User Evaluation**: After the execution steps complete, the robot stops. The user is then explicitly prompted in the terminal:
   ```
   Did the robot complete the task successfully? (y/n):
   ```
3. **Database Upsertion**: 
   - The user's original task description, the exact generated JSON plan, and the user's feedback ("success" or "failure") are combined into a single text document.
   - This document is dynamically embedded and stored as a new entry in the local ChromaDB vector database (`knowledge_base/chroma_store/`).
   
## Why this Matters

When a similar task is requested in the future:
- If the previous execution was a **success**, the LLM sees the exact velocity commands that worked and can confidently reuse or adapt them.
- If the previous execution was a **failure**, the LLM sees what was attempted and explicitly understands that it failed, prompting it to generate a *different* approach for the new attempt.

Over time, this allows the robot to adapt to complex environments (e.g., "avoid the red box") by learning from its mistakes, without requiring any fine-tuning of the underlying `gemma4:31b` model.
