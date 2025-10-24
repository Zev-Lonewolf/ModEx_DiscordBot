import json

CAMINHO_IDIOMAS = "idiomas.json"

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
    with open(CAMINHO_IDIOMAS, "w", encoding="utf-8") as f:
        json.dump(idiomas, f, indent=4)

def obter_idioma(guild_id):
    guild_id = str(guild_id)
    if guild_id not in idiomas:
        idiomas[guild_id] = "en"
        salvar_idiomas()
    return idiomas[guild_id]

def definir_idioma(guild_id, idioma):
    idiomas[str(guild_id)] = idioma
    salvar_idiomas()
