import json
import os

# Define o caminho correto para o JSON de idiomas
CAMINHO_IDIOMAS = os.path.join("data", "idiomas.json")

# Garante que o arquivo exista ao iniciar
try:
    with open(CAMINHO_IDIOMAS, "r", encoding="utf-8") as f:
        idiomas = json.load(f)
except FileNotFoundError:
    idiomas = {}

def carregar_idiomas():
    try:
        with open(CAMINHO_IDIOMAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def salvar_idiomas():
    # Garante que a pasta 'data' exista
    os.makedirs(os.path.dirname(CAMINHO_IDIOMAS), exist_ok=True)
    with open(CAMINHO_IDIOMAS, "w", encoding="utf-8") as f:
        json.dump(idiomas, f, indent=4)

def obter_idioma(guild_id):
    guild_id = str(guild_id)
    if guild_id not in idiomas:
        idiomas[guild_id] = "en"  # padrão caso não exista
        salvar_idiomas()
    return idiomas[guild_id]

def definir_idioma(guild_id, idioma):
    idiomas[str(guild_id)] = idioma
    salvar_idiomas()
