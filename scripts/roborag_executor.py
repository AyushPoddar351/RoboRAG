import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
import chromadb
import ollama
import time
import re
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Connect to knowledge base (using dynamic path)
CHROMA_PATH = os.path.join(PROJECT_ROOT, "knowledge_base", "chroma_store")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_collection("robot_tasks")

# Connect to Ollama
llm = ollama.Client(host='http://172.20.192.1:11434')

def plan_task(task: str) -> str:
    results = collection.query(query_texts=[task], n_results=2)
    retrieved = results['documents'][0]
    context = "\n".join([f"- {doc}" for doc in retrieved])
    prompt = f"""You are a robot task planner. Based on past experiences, generate an action plan.

Past experiences:
{context}

New task: {task}

Respond ONLY with a JSON list of steps. Each step must have:
- linear_x: float (forward speed, max 0.3)
- angular_z: float (turn speed, max 0.5)  
- duration: float (seconds)

Example: [{{"linear_x": 0.2, "angular_z": 0.0, "duration": 3.0}}]
No explanation, just the JSON."""

    response = llm.chat(
        model='gemma4:31b-cloud',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.message.content

def log_outcome(collection, task: str, steps: list, success: bool):
    import uuid
    plan_str = ", ".join([f"linear={s['linear_x']} angular={s['angular_z']} for {s['duration']}s" for s in steps])
    outcome = "success" if success else "failure"
    doc = f"Task: {task}. Plan: {plan_str}. Outcome: {outcome}"
    collection.upsert(
        documents=[doc],
        ids=[f"exp_{uuid.uuid4().hex[:8]}"],
        metadatas=[{"task": task, "outcome": outcome}]
    )
    print(f"Logged to knowledge base: {outcome}")

class RoboRAGExecutor(Node):
    def __init__(self):
        super().__init__('roborag_executor')
        self.publisher = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.get_logger().info('RoboRAG Executor ready')

    def execute_plan(self, steps: list):
        for i, step in enumerate(steps):
            self.get_logger().info(
                f"Step {i+1}: linear={step['linear_x']}, angular={step['angular_z']}, duration={step['duration']}s"
            )
            end_time = time.time() + step['duration']
            while time.time() < end_time:
                msg = TwistStamped()
                msg.twist.linear.x = float(step['linear_x'])
                msg.twist.angular.z = float(step['angular_z'])
                self.publisher.publish(msg)
                time.sleep(0.1)

        # Stop robot
        self.stop()

    def stop(self):
        msg = TwistStamped()
        self.publisher.publish(msg)
        self.get_logger().info('Task complete. Robot stopped.')

def main():
    rclpy.init()
    node = RoboRAGExecutor()

    task = input("\nEnter task: ")
    print("Retrieving experiences and planning...")
    
    raw_plan = plan_task(task)
    print(f"Raw plan:\n{raw_plan}\n")

    # Parse JSON from response
    import json
    match = re.search(r'\[.*\]', raw_plan, re.DOTALL)
    if match:
        steps = json.loads(match.group())
        print(f"Executing {len(steps)} steps...")
        node.execute_plan(steps)
        
        feedback = input("Did the robot complete the task successfully? (y/n): ")
        log_outcome(collection, task, steps, feedback.lower() == 'y')
        print(f"Knowledge base now has {collection.count()} experiences")
    else:
        print("Could not parse plan. Try again.")

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()