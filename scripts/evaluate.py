import chromadb
import ollama
import json
import re
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(PROJECT_ROOT, "knowledge_base", "chroma_store")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_collection("robot_tasks")
llm = ollama.Client(host='http://172.20.192.1:11434')

MODEL = 'gemma4:31b-cloud'

# 10 test tasks — mix of seen and novel
TEST_TASKS = [
    "move forward slowly",
    "turn right 90 degrees",
    "avoid obstacle on the left",
    "do a full rotation",
    "move backward",
    "spiral outward",
    "move forward then turn left",
    "stop and wait",
    "navigate around a box",
    "do a figure eight",
]

JSON_PROMPT = """Respond ONLY with a JSON list of steps. Each step must have:
- linear_x: float (forward speed, max 0.3)
- angular_z: float (turn speed, max 0.5)
- duration: float (seconds)

Example: [{"linear_x": 0.2, "angular_z": 0.0, "duration": 3.0}]
No explanation, just the JSON."""

def get_rag_plan(task: str) -> str:
    results = collection.query(query_texts=[task], n_results=2)
    retrieved = results['documents'][0]
    context = "\n".join([f"- {doc}" for doc in retrieved])
    prompt = f"""You are a robot task planner. Based on past experiences, generate an action plan.

Past experiences:
{context}

New task: {task}

{JSON_PROMPT}"""
    response = llm.chat(model=MODEL, messages=[{'role': 'user', 'content': prompt}])
    return response.message.content

def get_zeroshot_plan(task: str) -> str:
    prompt = f"""You are a robot task planner. Generate an action plan for a TurtleBot3.

New task: {task}

{JSON_PROMPT}"""
    response = llm.chat(model=MODEL, messages=[{'role': 'user', 'content': prompt}])
    return response.message.content

def score_plan(raw: str) -> dict:
    """Score a plan on 3 criteria. Returns dict with scores and parsed steps."""
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if not match:
        return {"parseable": 0, "valid_values": 0, "multi_step": 0, "total": 0, "steps": []}
    
    try:
        steps = json.loads(match.group())
    except json.JSONDecodeError:
        return {"parseable": 0, "valid_values": 0, "multi_step": 0, "total": 0, "steps": []}

    parseable = 1
    valid_values = 1 if all(
        abs(s.get('linear_x', 99)) <= 0.3 and
        abs(s.get('angular_z', 99)) <= 0.5 and
        s.get('duration', 0) > 0
        for s in steps
    ) else 0
    multi_step = 1 if len(steps) > 1 else 0
    total = parseable + valid_values + multi_step

    return {"parseable": parseable, "valid_values": valid_values,
            "multi_step": multi_step, "total": total, "steps": steps}

def run_evaluation():
    results = []
    print(f"{'Task':<35} {'RAG':>5} {'Zero':>5} {'Winner'}")
    print("-" * 60)

    for task in TEST_TASKS:
        rag_raw = get_rag_plan(task)
        zero_raw = get_zeroshot_plan(task)

        rag_score = score_plan(rag_raw)
        zero_score = score_plan(zero_raw)

        if rag_score['total'] > zero_score['total']:
            winner = "RAG ✓"
        elif zero_score['total'] > rag_score['total']:
            winner = "Zero ✓"
        else:
            winner = "Tie"

        print(f"{task:<35} {rag_score['total']:>5} {zero_score['total']:>5} {winner}")
        results.append({
            "task": task,
            "rag_score": rag_score['total'],
            "zero_score": zero_score['total'],
            "winner": winner
        })

    # Summary
    rag_wins = sum(1 for r in results if r['winner'] == "RAG ✓")
    zero_wins = sum(1 for r in results if r['winner'] == "Zero ✓")
    ties = sum(1 for r in results if r['winner'] == "Tie")
    rag_total = sum(r['rag_score'] for r in results)
    zero_total = sum(r['zero_score'] for r in results)

    print("-" * 60)
    print(f"\nRAG wins: {rag_wins} | Zero-shot wins: {zero_wins} | Ties: {ties}")
    print(f"RAG total score: {rag_total}/{len(TEST_TASKS)*3}")
    print(f"Zero-shot total score: {zero_total}/{len(TEST_TASKS)*3}")

    # Save results
    log_path = os.path.join(PROJECT_ROOT, "logs", "evaluation.json")
    with open(log_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to logs/evaluation.json")

if __name__ == '__main__':
    run_evaluation()
