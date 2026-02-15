# Standard library imports
import json
import os

# Define path for languages storage
CAMINHO_IDIOMAS = os.path.join("data", "idiomas.json")

# Initialize and load language data
def carregar_idiomas():
    try:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(CAMINHO_IDIOMAS), exist_ok=True)
        
        # Create file if it does not exist
        if not os.path.exists(CAMINHO_IDIOMAS):
            with open(CAMINHO_IDIOMAS, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return {}
        
        # Load and parse file content
        with open(CAMINHO_IDIOMAS, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
            
    except (json.JSONDecodeError, FileNotFoundError):
        # Reset file on parse error
        with open(CAMINHO_IDIOMAS, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    except Exception as e:
        print(f"Erro crítico ao carregar idiomas: {e}")
        return {}

# Load language cache on startup
idiomas = carregar_idiomas()

# Persist language data to disk
def salvar_idiomas():
    try:
        os.makedirs(os.path.dirname(CAMINHO_IDIOMAS), exist_ok=True)
        with open(CAMINHO_IDIOMAS, "w", encoding="utf-8") as f:
            json.dump(idiomas, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar idiomas: {e}")

# Get language for a specific guild
def obter_idioma(guild_id):
    guild_id = str(guild_id)
    if guild_id not in idiomas:
        idiomas[guild_id] = "en"
        salvar_idiomas()
    return idiomas[guild_id]

# Set language for a specific guild
def definir_idioma(guild_id, idioma_code):
    idiomas[str(guild_id)] = idioma_code
    salvar_idiomas()
