import json
import os
from config import CAMINHO_MODOS, MODOS_CACHE
import time

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
        "criador": str(user_id),
        "em_edicao": True,
        "finalizado": False
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

def salvar_roles_modo(server_id, modo_id, roles):
    dados = carregar_modos()
    server_id = str(server_id)
    modo_id = str(modo_id)
    role_ids = []
    for r in roles:
        rid = getattr(r, "id", None) or (r if isinstance(r, int) else None)
        if rid:
            role_ids.append(str(rid))
    if server_id in dados and modo_id in dados[server_id]["modos"]:
        dados[server_id]["modos"][modo_id]["roles"] = role_ids
        salvar_modos(dados)

def salvar_channels_modo(server_id, modo_id, channels):
    dados = carregar_modos()
    server_id = str(server_id)
    modo_id = str(modo_id)
    if server_id in dados and modo_id in dados[server_id]["modos"]:
        dados[server_id]["modos"][modo_id]["channels"] = [str(ch.id) for ch in channels]
        salvar_modos(dados)

async def atribuir_recepcao(guild, modo_id, canais, role=None, overwrite=False):
    dados = carregar_modos()
    server_id = str(guild.id)
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

    if role:
        for ch in canais:
            try:
                await atualizar_permissoes_canal(ch, role, overwrite=overwrite)
            except Exception as e:
                print(f"[WARN] falha ao atualizar permissões no canal {ch.id}: {e}")

    return recepcao_anterior

def salvar_recepcao_modo(server_id, modo_id, is_recepcao):
    dados = carregar_modos()
    server_id = str(server_id)
    modo_id = str(modo_id)
    if server_id in dados and modo_id in dados[server_id]["modos"]:
        dados[server_id]["modos"][modo_id]["recepcao"] = is_recepcao
        salvar_modos(dados)

def esta_em_edicao(server_id, modo_id):
    dados = carregar_modos()
    server_id = str(server_id)
    modo_id = str(modo_id)
    return (
        server_id in dados
        and modo_id in dados[server_id].get("modos", {})
        and dados[server_id]["modos"][modo_id].get("em_edicao", False)
    )

def set_em_edicao(server_id, modo_id, valor=True):
    dados = carregar_modos()
    server_id = str(server_id)
    modo_id = str(modo_id)
    if server_id in dados and modo_id in dados[server_id]["modos"]:
        dados[server_id]["modos"][modo_id]["em_edicao"] = valor
        salvar_modos(dados)

def reset_edicao(guild_id: int, user_id: int = None):
    dados = carregar_modos()
    guild_str = str(guild_id)
    
    if guild_str not in dados:
        return
    
    for mid, m in dados[guild_str].get("modos", {}).items():
        if user_id:
            if m.get("criador") == str(user_id):
                m["em_edicao"] = False
        else:
            m["em_edicao"] = False
    
    salvar_modos(dados)

async def atualizar_permissoes_canal(canal, role, overwrite=False):
    try:
        if overwrite:
            await canal.edit(overwrites={})

        perms = canal.overwrites_for(role)
        perms.view_channel = True
        perms.send_messages = True
        perms.connect = True
        perms.speak = True

        await canal.set_permissions(role, overwrite=perms)

    except Exception as e:
        print(f"[ERROR] Falha ao atualizar permissões em {canal.name}: {e}")

def substituir_cargo(modos, guild_id, modo_id, novo_cargo_id):
    modo = modos[str(guild_id)]["modos"][modo_id]
    cargo_antigo_id = modo.get("roles", [None])[0]

    modo["roles"] = [novo_cargo_id]
    return cargo_antigo_id, novo_cargo_id

def validar_canais(guild, canais_selecionados, canais_existentes_no_modo_atual):

    canais_validos = []
    canais_invalidos = []

    for ch_id in canais_selecionados:
        ch = guild.get_channel(ch_id)
        if not ch:
            canais_invalidos.append(str(ch_id))
            continue

        if ch_id in canais_existentes_no_modo_atual:
            canais_validos.append(ch_id)
            continue

        if ch.permissions_for(guild.me).manage_channels:
            canais_validos.append(ch_id)
        else:
            canais_invalidos.append(ch.name)

    return canais_validos, canais_invalidos

def limpar_modos_incompletos(guild_id):
    guild_id_str = str(guild_id)
    dados = carregar_modos()
    if guild_id_str not in dados:
        return

    modos_guild = dados[guild_id_str].get("modos", {})
    modos_para_remover = []

    for modo_id, modo in modos_guild.items():
        if not modo.get("em_edicao", False) and not modo.get("finalizado", False):
            modos_para_remover.append(modo_id)

    for modo_id in modos_para_remover:
        modos_guild.pop(modo_id, None)

    dados[guild_id_str]["modos"] = modos_guild
    MODOS_CACHE[guild_id_str] = dados[guild_id_str]
    salvar_modos(dados)
