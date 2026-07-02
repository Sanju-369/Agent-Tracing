import logging
import time
import random
import functools
from monitor.logger_setup import create_agent_logger


# ─────────────────────────────
# Trace Decorator
# ─────────────────────────────

# create a trace decorator which is take the argument from data logger.
def trace(logger):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time() # Record the stsrt time immediately from debugging to  filtering how much time it will takes.
            logger.debug(f"→ {func.__name__} started")
            
            # Try Block is used For Calculate how long it took in milliseconds. Log at INFO level that it completed successfully.

            try:
                result = func(*args, **kwargs)
                latency = round((time.time() - start) * 1000, 2)
                logger.info(
                    f"✓ {func.__name__} completed",
                    extra={
                        "session_id": kwargs.get("session_id", "unknown"), #Safely Pull the session id from the keyword Argument if it was passed fall back to llm 
                        "latency_ms": latency,
                    }
                )
                return result
            except Exception as e:
                logger.error(f"✗ {func.__name__} failed: {e}")
                raise
        return wrapper
    return decorator


# ─────────────────────────────
# Agent Simulator
# ─────────────────────────────
 #Every session gets its own Agent instance with its own session_id. The logger is created once at initialization
class AgentSimulator:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logger = create_agent_logger("health_agent", session_id)

    def translate(self, text: str) -> str:
        self.logger.debug(
            f"Translating: {text}",
            extra={"session_id": self.session_id, "tool_name": "translate"} #Attaches which tool was called to the log entry
        )
        time.sleep(0.5)
        return f"[translated] {text}"

    def extract_symptoms(self, text: str) -> dict: # Extracting the symtoms from the logger file 
        self.logger.info(
            "Extracting symptoms",
            extra={"session_id": self.session_id, "tool_name": "extract"}
        )
        time.sleep(0.3)
        return {"primary": "fever", "duration": "3 days", "severity": "moderate"}

    def make_triage_decision(self, symptoms: dict) -> str:
        self.logger.info(
            "Making triage decision",
            extra={"session_id": self.session_id, "tool_name": "triage"} #Extracting The triage decision from the loging file 
        )

        if random.random() < 0.3: #30% of the time the agent logs a WARNING about low confidence.
            self.logger.warning(
                "Low confidence — borderline case",
                extra={"session_id": self.session_id}
            )


        #This is the most Important Decission Variable cost for per model call
       
        decision = "URGENT"
        cost = round(random.uniform(0.001, 0.005), 4)

        self.logger.info(
            f"Decision: {decision}",
            extra={
                "session_id": self.session_id,
                "decision": decision,
                "cost_usd": cost,
                "latency_ms": 843
            }
        )
        return decision

    #calls translate, then extract, then triage in sequence. Each step depends on the previous one so they run sequentially, not concurrently.

    def run_session(self, patient_input: str) -> str:
        self.logger.info(
            f"Session started | input: {patient_input}",
            extra={"session_id": self.session_id}
        )

        try:
            translated = self.translate(patient_input)
            symptoms = self.extract_symptoms(translated)
            decision = self.make_triage_decision(symptoms)

            self.logger.info(
                f"Session completed | decision: {decision}",
                extra={"session_id": self.session_id, "decision": decision}
            )
            return decision

        except Exception as e:
            self.logger.critical(               #CRITICAL because if the entire session fails, the health worker gets no answer
                f"Session failed: {e}",
                extra={"session_id": self.session_id}
            )
            return "URGENT"   #. When everything fails, classify UP not down. A missed emergency is worse.