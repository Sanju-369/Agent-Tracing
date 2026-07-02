import os
from monitor.agent_simulator import AgentSimulator

# Create traces directory if it doesn't exist
os.makedirs("traces", exist_ok=True)

# Three simulated sessions
sessions = [
    ("sess_001", "ମୋ ପେଟ ଯନ୍ତ୍ରଣା ହେଉଛି"),
    ("sess_002", "बुखार और सिरदर्द तीन दिनों से"),
    ("sess_003", "chest pain since morning"),
    ("sess_004", "heart  pain since morning"),
]

for session_id, patient_input in sessions:
    print(f"\n{'='*50}")
    print(f"Running session: {session_id}")
    print(f"{'='*50}")

    agent = AgentSimulator(session_id)
    decision = agent.run_session(patient_input)
    print(f"Final decision: {decision}")

print("\n✓ All sessions complete")
print("✓ Check traces/agent.log for warnings")
print("✓ Check traces/agent_traces.jsonl for structured logs")