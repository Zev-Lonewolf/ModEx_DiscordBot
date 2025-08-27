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
    pasta = os.path.dirname(CAMINHO_MODOS)
    if pasta and not os.path.exists(pasta):
        os.makedirs(pasta, exist_ok=True)

    with open(CAMINHO_MODOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def salvar_nome_modo(server_id, user_id, nome_modo):
    dados = carregar_modos()
    server_id = str(server_id)
    user_id = str(user_id)

    dados.setdefault(server_id, {})
    dados[server_id].setdefault("modos", {})
    dados[server_id]["modos"].setdefault(user_id, {})

    dados[server_id]["modos"][user_id]["nome"] = nome_modo
    salvar_modos(dados)

def salvar_roles_modo(server_id, user_id, roles):
    dados = carregar_modos()
    server_id = str(server_id)
    user_id = str(user_id)

    dados.setdefault(server_id, {})
    dados[server_id].setdefault("modos", {})
    dados[server_id]["modos"].setdefault(user_id, {})

    role_ids = []
    for r in roles:
        if isinstance(r, int):
            role_ids.append(str(r))
            continue
        if isinstance(r, str):
            s = r.strip()
            if s.isdigit():
                role_ids.append(s)
                continue
        try:
            rid = getattr(r, "id", None)
            if rid is not None:
                role_ids.append(str(rid))
                continue
        except Exception:
            pass
        role_ids.append(str(r))

    dados[server_id]["modos"][user_id]["roles"] = role_ids
    salvar_modos(dados)

def salvar_channels_modo(server_id, user_id, channels):
    dados = carregar_modos()
    server_id = str(server_id)
    user_id = str(user_id)

    dados.setdefault(server_id, {})
    dados[server_id].setdefault("modos", {})
    dados[server_id]["modos"].setdefault(user_id, {})

    dados[server_id]["modos"][user_id]["channels"] = [str(ch.id) for ch in channels]
    salvar_modos(dados)
