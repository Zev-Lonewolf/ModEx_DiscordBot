import json
import os
from config import CAMINHO_MODOS
import time

def carregar_modos():
    if not os.path.exists(CAMINHO_MODOS):
        return {}
    with open(CAMINHO_MODOS, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
        
def criar_modo(server_id, user_id, nome_modo):
    dados = carregar_modos()
    server_id = str(server_id)

    dados.setdefault(server_id, {})
    dados[server_id].setdefault("modos", {})

    modo_id = str(int(time.time() * 1000))

    dados[server_id]["modos"][modo_id] = {
        "nome": nome_modo,
        "roles": [],
        "channels": [],
        "recepcao": False,
        "criador": str(user_id)
    }

    salvar_modos(dados)
    return modo_id

def modo_existe(server_id, nome_modo):
    dados = carregar_modos()
    server_id = str(server_id)
    if server_id not in dados:
        return None

    for modo_id, modo in dados[server_id].get("modos", {}).items():
        if modo.get("nome", "").lower() == nome_modo.lower():
            return modo_id
    return None

def salvar_modos(dados):
    pasta = os.path.dirname(CAMINHO_MODOS)
    if pasta and not os.path.exists(pasta):
        os.makedirs(pasta, exist_ok=True)

    with open(CAMINHO_MODOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def salvar_nome_modo(server_id, modo_id, nome_modo):
    dados = carregar_modos()
    server_id = str(server_id)
    modo_id = str(modo_id)

    if server_id in dados and modo_id in dados[server_id]["modos"]:
        dados[server_id]["modos"][modo_id]["nome"] = nome_modo
        salvar_modos(dados)

def salvar_roles_modo(server_id, modo_id, roles):
    dados = carregar_modos()
    server_id = str(server_id)
    modo_id = str(modo_id)

    role_ids = []
    for r in roles:
        rid = getattr(r, "id", None) or (r if isinstance(r, int) else None)
        if rid:
            role_ids.append(str(rid))
        else:
            role_ids.append(str(r))

    if server_id in dados and modo_id in dados[server_id]["modos"]:
        dados[server_id]["modos"][modo_id]["roles"] = role_ids
        salvar_modos(dados)

def atribuir_recepcao(server_id, modo_id):
    dados = carregar_modos()
    server_id = str(server_id)
    modo_id = str(modo_id)
    recepcao_anterior = None

    if server_id in dados:
        for mid, modo in dados[server_id].get("modos", {}).items():
            if modo.get("recepcao") and mid != modo_id:
                recepcao_anterior = mid
                modo["recepcao"] = False

        if modo_id in dados[server_id]["modos"]:
            dados[server_id]["modos"][modo_id]["recepcao"] = True

        salvar_modos(dados)

    return recepcao_anterior

def salvar_channels_modo(server_id, modo_id, channels):
    dados = carregar_modos()
    server_id = str(server_id)
    modo_id = str(modo_id)

    if server_id in dados and modo_id in dados[server_id]["modos"]:
        dados[server_id]["modos"][modo_id]["channels"] = [str(ch.id) for ch in channels]
        salvar_modos(dados)


def salvar_recepcao_modo(server_id, modo_id, is_recepcao):
    dados = carregar_modos()
    server_id = str(server_id)
    modo_id = str(modo_id)

    if server_id in dados and modo_id in dados[server_id]["modos"]:
        dados[server_id]["modos"][modo_id]["recepcao"] = is_recepcao
        salvar_modos(dados)
