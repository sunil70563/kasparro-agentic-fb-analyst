import logging
import sys
import os
import json
import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "agent": record.name,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_record)

def get_logger(name):
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # 1. Console Handler (Human Readable for CLI)
        console_formatter = logging.Formatter('%(asctime)s - [%(name)s] - %(levelname)s - %(message)s')
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # 2. File Handler (JSON for Observability)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        log_dir = os.path.join(base_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(os.path.join(log_dir, "execution.jsonl"), mode='a')
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    return logger