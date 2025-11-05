import json
import logging
import os
from datetime import datetime

CONFIG_PATH = "data/config_debug.json"
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

def carregar_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"debug_enabled": False}

def salvar_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def configurar_logger():
    config = carregar_config()
    debug_enabled = config.get("debug_enabled", False)

    logger = logging.getLogger("BotLogger")

    # Remove qualquer handler anterior pra evitar duplicação
    if logger.hasHandlers():
        logger.handlers.clear()

    # Se o modo debug estiver desativado, desliga o logger totalmente
    if not debug_enabled:
        logger.disabled = True
        return logger

    logger.disabled = False
    logger.setLevel(logging.DEBUG)

    # Formato padrão do log
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")

    # 📁 Log apenas em arquivo (sem console)
    log_filename = os.path.join(LOGS_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = configurar_logger()
