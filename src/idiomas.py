import json
import os

# Define o caminho correto para o JSON de idiomas
CAMINHO_IDIOMAS = os.path.join("data", "idiomas.json")

# Garante que o arquivo exista ao iniciar
def carregar_idiomas():
    try:
        # Garante que a pasta data existe
        os.makedirs(os.path.dirname(CAMINHO_IDIOMAS), exist_ok=True)
        
        # Se o arquivo não existe, cria um vazio
        if not os.path.exists(CAMINHO_IDIOMAS):
            with open(CAMINHO_IDIOMAS, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return {}
        
        # Tenta carregar o arquivo
        with open(CAMINHO_IDIOMAS, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:  # Se o arquivo está vazio
                return {}
            return json.loads(content)
            
    except (json.JSONDecodeError, FileNotFoundError):
        # Se há erro no JSON, recria o arquivo
        with open(CAMINHO_IDIOMAS, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    except Exception as e:
        print(f"Erro crítico ao carregar idiomas: {e}")
        return {}

# Carrega os idiomas na inicialização
idiomas = carregar_idiomas()

def salvar_idiomas():
    try:
        # Garante que a pasta data existe
        os.makedirs(os.path.dirname(CAMINHO_IDIOMAS), exist_ok=True)
        with open(CAMINHO_IDIOMAS, "w", encoding="utf-8") as f:
            json.dump(idiomas, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar idiomas: {e}")

def obter_idioma(guild_id):
    guild_id = str(guild_id)
    if guild_id not in idiomas:
        idiomas[guild_id] = "en"  # padrão caso não exista
        salvar_idiomas()
    return idiomas[guild_id]

def definir_idioma(guild_id, idioma_code):
    idiomas[str(guild_id)] = idioma_code
    salvar_idiomas()