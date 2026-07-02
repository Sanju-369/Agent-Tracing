import logging
import json
from datetime import datetime


# ─────────────────────────────
# Custom JSON Formatter because it will help indexable and instantly Searchable
# ─────────────────────────────

class JSONFormatter(logging.Formatter): 
    def format(self, record): #record it is a object of logrecord class which record all log if its suscees or fail doesnot matter 
       
       #I Built a dictionary for records attribute 
        log_entry = {
            "timestamp": datetime.now().isoformat(), # when the log will be happened 
            "level": record.levelname, #What type of issue we face it is a INFO, WARNING ,ERROR,CRITICAl
            "logger": record.name, # Which Agent this error came out 
            "message": record.getMessage(), # the Actula Log message 
            "function": record.funcName, # the python function which called the logger
        }

        #If The Log is contained any extra messages beyond the dictionary this is going to this field.
        for field in ["session_id", "tool_name",
                      "latency_ms", "cost_usd", "decision"]:
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)

        return json.dumps(log_entry) # Convert the dictionary to the json 


# ─────────────────────────────
# Custom Filter
# ─────────────────────────────

class SessionFilter(logging.Filter):
    def __init__(self, session_id: str):
        super().__init__()
        self.session_id = session_id

    def filter(self, record): #The Python Calls filter(record) before writing each line this is where decided a log is going to logging file or print to  console
        return getattr(record, "session_id", None) == self.session_id


# ─────────────────────────────
# Logger Factory
# ─────────────────────────────

def create_agent_logger(name: str, session_id: str) -> logging.Logger:
    logger = logging.getLogger(name) # Create the logger and set the level of the logger 
    logger.setLevel(logging.DEBUG)
  
    if logger.handlers:
        logger.handlers.clear()

#-------------------------
# Create multiple handler for different level 
#--------------------------

    # Handler 1 — Console 
    # the output is written in terminal because it is stream handler  
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s"
    ))

    # Handler 2 — Plain text file
    # the output stored in a file because it is a file handler 
    text_handler = logging.FileHandler("traces/agent.log")
    text_handler.setLevel(logging.WARNING)
    text_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    ))

    # Handler 3 — JSON file
    json_handler = logging.FileHandler("traces/agent_traces.jsonl")
    json_handler.setLevel(logging.INFO) #Capture the info and above Debuglines.
    json_handler.setFormatter(JSONFormatter()) # This function used custom json format instead of plaintext
    json_handler.addFilter(SessionFilter(session_id)) #Only the catch the specific json file formats 

    logger.addHandler(console)
    logger.addHandler(text_handler)
    logger.addHandler(json_handler)

    return logger