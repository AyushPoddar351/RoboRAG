import chromadb
from chromadb.config import Settings

# Initialize ChromaDB with persistent storage
client = chromadb.PersistentClient(path="./chroma_store")
collection = client.get_or_create_collection(name="robot_tasks")

# Seed with past task experiences
experiences = [
    {
        "task": "move forward 1 meter",
        "context": "open corridor, no obstacles",
        "action_plan": "publish linear.x=0.2 for 5 seconds then stop",
        "outcome": "success",
        "id": "exp_001"
    },
    {
        "task": "turn left 90 degrees",
        "context": "open space",
        "action_plan": "publish angular.z=0.5 for 3 seconds then stop",
        "outcome": "success",
        "id": "exp_002"
    },
    {
        "task": "navigate to goal avoiding obstacle",
        "context": "obstacle detected at 0.5m front",
        "action_plan": "stop, turn right 45 degrees, move forward, resume original heading",
        "outcome": "success",
        "id": "exp_003"
    },
    {
        "task": "patrol area",
        "context": "rectangular room, no obstacles",
        "action_plan": "move forward 2m, turn left 90, repeat 4 times",
        "outcome": "success",
        "id": "exp_004"
    },
    {
        "task": "stop immediately",
        "context": "obstacle detected at 0.2m",
        "action_plan": "publish linear.x=0.0 angular.z=0.0 immediately",
        "outcome": "success",
        "id": "exp_005"
    },
]

# Store experiences
for exp in experiences:
    collection.upsert(
        documents=[f"Task: {exp['task']}. Context: {exp['context']}. Plan: {exp['action_plan']}. Outcome: {exp['outcome']}"],
        ids=[exp['id']],
        metadatas=[{"task": exp['task'], "outcome": exp['outcome']}]
    )

print(f"Knowledge base seeded with {collection.count()} experiences")

# Test retrieval
results = collection.query(
    query_texts=["move robot forward"],
    n_results=2
)
print("\nTest retrieval for 'move robot forward':")
for doc in results['documents'][0]:
    print(f"  - {doc[:80]}...")