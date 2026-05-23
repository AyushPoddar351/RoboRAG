import chromadb
import ollama

# Connect to knowledge base
chroma_client = chromadb.PersistentClient(path="../knowledge_base/chroma_store")
collection = chroma_client.get_collection("robot_tasks")

# Connect to Ollama
llm = ollama.Client(host='http://172.20.192.1:11434')

def plan_task(task: str) -> str:
    # Step 1: Retrieve relevant past experiences
    results = collection.query(query_texts=[task], n_results=2)
    retrieved = results['documents'][0]

    # Step 2: Build prompt with retrieved context
    context = "\n".join([f"- {doc}" for doc in retrieved])
    prompt = f"""You are a robot task planner. Based on past experiences, generate a concise action plan.

Past experiences:
{context}

New task: {task}

Provide a short, specific action plan using ROS2 velocity commands (linear.x, angular.z values and durations). Be concise."""

    # Step 3: Generate plan with LLM
    response = llm.chat(
        model='gemma4:31b-cloud',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.message.content

# Test it
if __name__ == '__main__':
    test_tasks = [
        "move forward slowly",
        "avoid obstacle on the left",
        "do a full rotation"
    ]
    
    for task in test_tasks:
        print(f"\nTask: {task}")
        print(f"Plan: {plan_task(task)}")
        print("-" * 50)