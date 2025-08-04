import json
import os
from config import CAMINHO_MODOS

def carregar_modos():
    if not os.path.exists(CAMINHO_MODOS):
        return {}
    with open(CAMINHO_MODOS, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def salvar_modos(dados):
    with open(CAMINHO_MODOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def salvar_nome_modo(server_id, user_id, nome_modo):
    dados = carregar_modos()
    server_id = str(server_id)
    user_id = str(user_id)

    if server_id not in dados:
        dados[server_id] = {}
    if user_id not in dados[server_id]:
        dados[server_id][user_id] = {}

    dados[server_id][user_id]["nome"] = nome_modo
    salvar_modos(dados)

def salvar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)