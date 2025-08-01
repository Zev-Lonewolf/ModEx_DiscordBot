import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
PREFIX = "!"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
CAMINHO_MODOS = os.path.join(DATA_DIR, "modos.json")
CAMINHO_IDIOMAS = os.path.join(DATA_DIR, "idiomas.json")

os.makedirs(DATA_DIR, exist_ok=True)