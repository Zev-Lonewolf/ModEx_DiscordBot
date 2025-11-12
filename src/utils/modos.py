import json
import os
import discord
from utils.logger_manager import logger
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

    if server_id not in dados:
        return None

    # Só desativa outros modos se um novo role (modo confirmado) foi definido
    if role:
        for mid, modo in dados[server_id].get("modos", {}).items():
            if modo.get("recepcao", False):
                modo["recepcao"] = False
                recepcao_anterior = mid

        if modo_id in dados[server_id]["modos"]:
            dados[server_id]["modos"][modo_id]["recepcao"] = True
            salvar_modos(dados)
        else:
            print(f"[WARN] modo {modo_id} não encontrado em {server_id}")
            return None
    else:
        # Não altera recepção se nenhum cargo foi confirmado
        print(f"[INFO] Nenhum cargo definido — recepção permanece inalterada")
        return None

    # Atualizar permissões
    for ch in canais:
        if not ch:
            continue
        try:
            overwrites = ch.overwrites.copy()
            overwrites[guild.default_role] = discord.PermissionOverwrite(
                view_channel=False,
                send_messages=False,
                connect=False,
                speak=False
            )
            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                connect=True,
                speak=True
            )
            await ch.edit(overwrites=overwrites)
        except Exception as e:
            print(f"[WARN] falha ao atualizar permissões no canal {getattr(ch, 'name', '?')}: {e}")

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

async def atualizar_permissoes_canal(canal, novo_cargo, bot_instance, criando_modo_dict, overwrite=False, modo_id=None, guild_id=None, user_id=None):
    try:
        logger.debug(f"[PERMISSÕES] Iniciando atualização para canal {canal.name}, cargo {novo_cargo.name}, modo={modo_id}")
        
        # ✅ CORREÇÃO: Usar o backup dos cargos antigos
        if overwrite and user_id and 'backup_data' in criando_modo_dict and user_id in criando_modo_dict['backup_data']:
            backup = criando_modo_dict['backup_data'][user_id]
            cargos_antigos = backup.get('cargos_antigos', [])
            
            logger.debug(f"[BACKUP] Cargos antigos para limpeza: {cargos_antigos}")
            
            # Remove APENAS os cargos antigos DESTE MODO
            cargos_removidos = []
            for role_id in cargos_antigos:
                try:
                    role_id_int = int(role_id)
                    # Não remove o novo cargo (se estiver na lista de antigos)
                    if role_id_int == novo_cargo.id:
                        continue
                        
                    role = canal.guild.get_role(role_id_int)
                    if role:
                        # Verificar se o bot tem permissão para gerenciar este cargo
                        bot_member = canal.guild.get_member(bot_instance.user.id)
                        if bot_member and role.position < bot_member.top_role.position:
                            await canal.set_permissions(role, overwrite=None)
                            cargos_removidos.append(role.name)
                            logger.debug(f"[PERMISSÕES] Removido cargo antigo {role.name} do canal {canal.name}")
                        else:
                            logger.warning(f"[PERMISSÕES] Cargo {role.name} está acima do bot na hierarquia - pulando")
                except (ValueError, TypeError) as e:
                    logger.warning(f"[PERMISSÕES] Erro ao processar cargo antigo {role_id}: {e}")
                    continue
            
            if cargos_removidos:
                logger.info(f"[PERMISSÕES] Cargos antigos removidos de {canal.name}: {', '.join(cargos_removidos)}")
            else:
                logger.debug(f"[PERMISSÕES] Nenhum cargo antigo removido de {canal.name}")
        
        # Agora aplica as permissões para o novo cargo
        try:
            # Verificar se o bot tem permissão para modificar este cargo específico
            bot_member = canal.guild.get_member(bot_instance.user.id)
            if bot_member and novo_cargo.position < bot_member.top_role.position:
                # Define permissões para visualizar o canal
                await canal.set_permissions(
                    novo_cargo,
                    read_messages=True,
                    send_messages=True,
                    view_channel=True,
                    connect=True if isinstance(canal, discord.VoiceChannel) else None
                )
                logger.debug(f"[PERMISSÕES] Permissões concedidas para {novo_cargo.name} em {canal.name}")
                return True
            else:
                logger.warning(f"[PERMISSÕES] Bot não pode modificar cargo {novo_cargo.name} - hierarquia insuficiente")
                return False
            
        except discord.Forbidden:
            logger.error(f"[PERMISSÕES] Sem permissão para definir permissões para {novo_cargo.name} em {canal.name}")
            return False
        except discord.HTTPException as e:
            logger.error(f"[PERMISSÕES] Erro ao definir permissões: {e}")
            return False
            
    except Exception as e:
        logger.error(f"[PERMISSÕES] Erro geral em atualizar_permissoes_canal: {e}")
        return False

def substituir_cargo(modos, guild_id, modo_id, novo_cargo_id):
    guild_id_str = str(guild_id)
    
    if guild_id_str not in modos:
        return None, novo_cargo_id
    
    # Encontra o modo de recepção atual
    modo_recepcao_anterior = None
    cargo_antigo_id = None
    
    for mid, modo_data in modos[guild_id_str]["modos"].items():
        if modo_data.get("recepcao"):
            modo_recepcao_anterior = mid
            if modo_data.get("roles"):
                cargo_antigo_id = int(modo_data["roles"][0])
            break
    
    # Se é o mesmo cargo, não faz nada
    if cargo_antigo_id == novo_cargo_id:
        return cargo_antigo_id, novo_cargo_id
    
    # Remove recepção de todos os modos
    for mid in modos[guild_id_str]["modos"]:
        modos[guild_id_str]["modos"][mid]["recepcao"] = False
    
    # Define o novo modo como recepção
    if modo_id in modos[guild_id_str]["modos"]:
        modos[guild_id_str]["modos"][modo_id]["recepcao"] = True
    
    salvar_modos(modos)
    
    logger.info(f"[RECEPÇÃO] Cargo de recepção substituído: {cargo_antigo_id} → {novo_cargo_id}")
    return cargo_antigo_id, novo_cargo_id

def validar_canais(guild, canais_selecionados, canais_existentes_no_modo_atual):
    canais_validos = []
    canais_invalidos = []

    for ch_id in canais_selecionados:
        ch_id_str = str(ch_id)
        ch = guild.get_channel(int(ch_id))
        if not ch:
            canais_invalidos.append(ch_id_str)
            continue

        if ch_id_str in canais_existentes_no_modo_atual:
            canais_validos.append(ch_id_str)
            continue

        if ch.permissions_for(guild.me).manage_channels:
            canais_validos.append(ch_id_str)
        else:
            canais_invalidos.append(ch.name)

    return canais_validos, canais_invalidos

def finalizar_modos_em_edicao(guild_id, user_id=None):
    dados = carregar_modos()
    guild_id_str = str(guild_id)
    if guild_id_str not in dados:
        return

    modos_guild = dados[guild_id_str].get("modos", {})

    for modo_id, modo in modos_guild.items():
        # Se user_id for passado, só finaliza modos desse usuário
        if user_id:
            if modo.get("criador") == str(user_id) and modo.get("em_edicao", False):
                modo["em_edicao"] = False
        else:
            # Se não passar user_id, finaliza todos que estão em edição
            if modo.get("em_edicao", False):
                modo["em_edicao"] = False

    dados[guild_id_str]["modos"] = modos_guild
    salvar_modos(dados)

def limpar_modos_incompletos(guild_id):
    guild_id_str = str(guild_id)
    dados = carregar_modos()
    if guild_id_str not in dados:
        return

    modos_guild = dados[guild_id_str].get("modos", {})
    modos_para_remover = []

    for modo_id, modo in modos_guild.items():
        if modo.get("em_edicao") is False and modo.get("finalizado") is False:
            modos_para_remover.append(modo_id)

    for modo_id in modos_para_remover:
        modos_guild.pop(modo_id, None)

    dados[guild_id_str]["modos"] = modos_guild
    # Remove do cache também para evitar "ressurreição"
    if guild_id_str in MODOS_CACHE:
        MODOS_CACHE[guild_id_str]["modos"] = modos_guild

    salvar_modos(dados)

def limpar_modos_usuario(guild_id, user_id):
    dados = carregar_modos()
    guild_id_str = str(guild_id)
    user_id_str = str(user_id)

    if guild_id_str not in dados:
        return

    modos_guild = dados[guild_id_str].get("modos", {})
    modos_para_remover = []

    for modo_id, modo in modos_guild.items():
        if modo.get("criador") == user_id_str and modo.get("em_edicao", True):
            modos_para_remover.append(modo_id)

    for modo_id in modos_para_remover:
        modos_guild.pop(modo_id, None)

    dados[guild_id_str]["modos"] = modos_guild
    MODOS_CACHE[guild_id_str] = dados[guild_id_str]
    salvar_modos(dados)
