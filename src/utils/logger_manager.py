# Standard library imports
import json
import logging
import os
from datetime import datetime

# Configuration and logs paths
CONFIG_PATH = "data/config_debug.json"
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Load configuration from json file
def carregar_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"debug_enabled": False}

# Save configuration to json file
def salvar_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

# Logger setup and initialization
def configurar_logger():
    config = carregar_config()
    debug_enabled = config.get("debug_enabled", False)

    logger = logging.getLogger("BotLogger")

    # Clear existing handlers to prevent duplication
    if logger.hasHandlers():
        logger.handlers.clear()

    # Disable logger if debug mode is off
    if not debug_enabled:
        logger.disabled = True
        return logger

    logger.disabled = False
    logger.setLevel(logging.DEBUG)

    # Standard log format
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")

    # File handler setup
    log_filename = os.path.join(LOGS_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Initialize global logger
logger = configurar_logger()
