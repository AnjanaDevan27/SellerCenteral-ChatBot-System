import logging
import json
logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format=json.dumps({"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"})
)

def log_event(message):
    logging.info(message)
    print(f"LOGGED: {message}") 

log_event("Data preprocessing completed successfully.")
