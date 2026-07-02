# Agent Activity Monitor

A production-grade structured logging system for AI agents.
Built from scratch in pure Python — no frameworks, no shortcuts.

## Why This Exists

When an AI agent makes a wrong decision in production, you need 
to know exactly what happened. Which session. Which tool. How long 
it took. What it cost. What the model decided and why.

`print()` cannot answer any of these questions.
Structured logging can.

This project builds a complete logging system for an AI agent — 
three handlers, custom JSON formatter, session filtering, and 
automatic latency + cost tracking on every function call.


## The Architecture — 3 Handlers, 1 Logger

Every log call fans out to three destinations simultaneously:

| Handler | Destination | Level | Format |
|---|---|---|---|
| Console | Terminal | DEBUG+ | Plain text |
| Text file | traces/agent.log | WARNING+ | Plain text |
| JSON file | traces/agent_traces.jsonl | INFO+ | Structured JSON |

Same logger. Three handlers. Each decides independently what to write.

## The 5 Concepts Used

### 1. Log Levels
Five levels in order of severity — each maps to a real situation:

- DEBUG — low-level detail, development only
- INFO — normal operation, permanent record
- WARNING — needs attention, not breaking
- ERROR — something failed, system still running
- CRITICAL — complete failure, immediate action needed

### 2. Named Loggers
Every component gets its own named logger so you always know
which part of the system each log line came from.

### 3. Custom JSON Formatter
Plain text logs are readable.
JSON logs are queryable — filter by session, sort by cost,
find slowest calls by latency. This is the trace file your
monitoring system reads.

### 4. Session Filter
In a system serving 100 users simultaneously, you need to pull
logs for one specific session without reading 10,000 irrelevant
lines. SessionFilter gates the JSON handler — only entries
matching the session ID get written.

### 5. Extra Fields
Structured metadata attached to every log line:

session_id — which session this belongs to
tool_name  — which tool was called
latency_ms — how long it took
cost_usd   — what it cost
decision   — what the agent decided

Three questions every production AI system must answer about
every call: what was decided, how much did it cost, how long
did it take.

## The Problem I Faced And How I solved This Problem.

When running multiple sessions, each session printed log lines
N times — where N was the session number.

Cause: logging.getLogger(name) returns the same logger object
every time. Creating a new AgentSimulator per session kept
adding handlers to the same logger. By session 4 there were
4 sets of handlers firing simultaneously.

Fix — one line:

if logger.handlers:
    logger.handlers.clear()

This bug taught me more about Python's logging system than
reading the documentation did.

## Sample Output

Console:
2026-07-02 07:15:33 | INFO     | Session started | input: ମୋ ପେଟ ଯନ୍ତ୍ରଣା ହେଉଛି
2026-07-02 07:15:33 | DEBUG    | Translating: ମୋ ପେଟ ଯନ୍ତ୍ରଣା ହେଉଛି
2026-07-02 07:15:34 | WARNING  | Low confidence — borderline case
2026-07-02 07:15:34 | INFO     | Decision: URGENT

JSON trace file:
{"timestamp": "2026-07-02T07:15:34", "level": "INFO",
 "message": "Decision: URGENT", "session_id": "sess_001",
 "decision": "URGENT", "cost_usd": 0.003, "latency_ms": 843}

Plain text warning log:
2026-07-02 07:15:34 | WARNING | Low confidence — borderline case

## Run It Yourself

python main.py

Requires Python 3.8+. No external dependencies — pure standard
library only.

After running check:
- traces/agent.log for warnings and above
- traces/agent_traces.jsonl for full structured traces

## What's Next

This trace layer feeds into something larger — an agent that
actually reasons and acts, in a domain where getting it wrong
has real consequences.
