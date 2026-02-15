import re
import os
import sys
from pathlib import Path
import json
import discord
import asyncio
from utils.dropbox_sync import sync_file_to_drive, run_setup_periodic, get_dropbox_client, StateManager, create_periodic_state_save, bootstrap_data_files
from discord.ext import commands, tasks
from config import TOKEN, PREFIX, CAMINHO_IDIOMAS, CAMINHO_MODOS, DATA_DIR
from utils.logger_manager import logger, carregar_config, salvar_config, configurar_logger, CONFIG_PATH
from idiomas import obter_idioma, definir_idioma, carregar_idiomas
from utils.modos import (
    criar_modo,
    modo_existe,
    salvar_modos,
    salvar_roles_modo,
    carregar_modos,
    salvar_channels_modo,
    atribuir_recepcao,
    reset_edicao,
    atualizar_permissoes_canal,
    substituir_cargo,
    validar_canais,
    limpar_modos_incompletos,
    limpar_modos_usuario,
    finalizar_modos_em_edicao,
    apagar_modo,
    aplicar_modo_servidor
)
from embed import (
    get_language_embed,
    get_greeting_embed,
    get_setup_embed,
    get_about_embed,
    get_functions_embed,
    get_roles_embed,
    get_edit_embed,
    get_invalid_mode_embed,
    get_mode_selected_embed,
    get_create_embed,
    get_initial_create_embed,
    get_name_saved_embed,
    get_invalid_name_embed,
    get_name_conflict_embed,
    get_role_select_embed,
    get_role_saved_embed,
    get_invalid_role_embed,
    get_channel_select_embed,
    get_channel_saved_embed,
    get_invalid_channel_embed,
    get_reception_mode_question_embed,
    get_reception_assigned_embed,
    get_reception_replaced_embed,
    get_reception_skipped_embed,
    get_finish_mode_embed,
    get_channel_conflict_warning_embed,
    get_channel_removed_warning_embed,
    get_log_info_embed,
    get_log_confirm_embed,
    get_log_activated_embed,
    get_log_deactivated_embed,
    get_delete_mode_embed,
    get_delete_confirm_embed,
    get_delete_success_embed,
    get_delete_error_embed,
    get_switch_mode_list_embed,
    get_switch_success_embed,
    get_switch_error_embed,
    get_switch_not_found_embed,
    get_clean_embed
)

# Reset user session state
def resetar_estado_usuario(guild_id, user_id):
    criando_modo.pop(user_id, None)
    modo_ids.pop(user_id, None)
    user_progress.setdefault(guild_id, {}).pop(user_id, None)
    historico_embeds.pop(user_id, None)
    em_edicao.pop(user_id, None)
    modo_atual.pop(user_id, None)
    limpar_modos_usuario(guild_id, user_id)

# Bot & Intents configuration
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
MODOS_CACHE = carregar_modos()

# Periodic backup task
@tasks.loop(hours=1)
async def backup_task():
    logger.info("Iniciando backup...")
    try:
        await asyncio.to_thread(sync_file_to_drive, CAMINHO_MODOS, "modos.json")
        await asyncio.to_thread(sync_file_to_drive, CAMINHO_IDIOMAS, "idiomas.json")
        await asyncio.to_thread(sync_file_to_drive, CONFIG_PATH, "config_debug.json")
        logger.info("Backup completo")
    except Exception as e:
        logger.error(f"Erro no backup: {e}")

@backup_task.before_loop
async def before_backup():
    logger.debug("Aguardando o bot ligar para iniciar o loop de backup.")
    await bot.wait_until_ready()

# Global state variables
mensagem_idioma_id = {}
mensagem_voltar_ids = {}
mensagem_avancar_ids = {}
criando_modo = {}
user_progress = {}
historico_embeds = {}
user_id = {}
modo_ids = {}
em_edicao = {}
modo_atual = {}
resposta_enviada = set()
MODOS_CACHE = carregar_modos()

# Flow navigation mapping
flow = {
    "get_language_embed": {
        "next": "get_greeting_embed",
        "back": None
    },
    "get_greeting_embed": {
        "next": "get_setup_embed",
        "back": None
    },
    "get_setup_embed": {
        "next": None,
        "back": None
    },
    "get_about_embed": {
        "next": None,
        "back": "get_setup_embed"
    },
    "get_functions_embed": {
        "next": None,
        "back": "get_setup_embed"
    },
    "get_roles_embed": {
        "next": None,
        "back": "get_setup_embed"
    },
    "get_edit_embed": {
        "back": "get_setup_embed",
        "next": None,
    },
    "get_mode_selected_embed": {
        "next": "get_initial_create_embed",
        "back": "get_edit_embed"
    },
    "get_invalid_mode_embed": {
        "next": None,
        "back": "get_edit_embed"
    },
    "get_create_embed": {
        "back": "get_setup_embed",
        "next": [
            "get_initial_create_embed", 
            "get_name_saved_embed", 
            "get_name_conflict_embed", 
            "get_invalid_name_embed"
        ]
    },
    "get_initial_create_embed": {
        "back": "get_create_embed",
        "next": None
    },
    "get_name_saved_embed": {
        "back": "get_create_embed",
        "next": "get_role_select_embed"
    },
    "get_name_conflict_embed": {
        "back": "get_create_embed",
        "next": "get_role_select_embed"
    },
    "get_invalid_name_embed": {
        "back": "get_create_embed",
        "next": "get_role_select_embed"
    },
    "get_role_select_embed": {
        "back": "get_initial_create_embed",
        "next": None
    },
    "get_role_saved_embed": {
        "back": "get_role_select_embed",
        "next": "get_channel_select_embed"
    },
    "get_invalid_role_embed": {
        "back": "get_role_select_embed",
        "next": "get_channel_select_embed"
    },
    "get_channel_select_embed": {
        "back": "get_role_saved_embed",
        "next": None
    },
    "get_channel_saved_embed": {
        "back": "get_channel_select_embed",
        "next": "get_reception_mode_question_embed"      
    },
    "get_invalid_channel_embed": {
        "back": "get_channel_select_embed",
        "next": "get_reception_mode_question_embed"      
    },
    "get_reception_mode_question_embed": {
        "back": "get_channel_select_embed",
        "next": [
            "get_reception_assigned_embed", 
            "get_reception_replaced_embed", 
            "get_reception_skipped_embed", 
            "get_reception_error_embed",
            "get_channel_conflict_warning_embed",
            "get_channel_removed_warning_embed"
        ]
    },
    "get_reception_assigned_embed": {
        "back": "get_reception_mode_question_embed",
        "next": "get_finish_mode_embed"
    },
    "get_reception_replaced_embed": {
        "back": "get_reception_mode_question_embed",
        "next": "get_finish_mode_embed"
    },
    "get_reception_error_embed": {
        "back": "get_reception_mode_question_embed",
        "next": "get_finish_mode_embed"
    },
    "get_channel_conflict_warning_embed": {
        "back": "get_channel_select_embed",
        "next": "get_finish_mode_embed"
    },
    "get_channel_removed_warning_embed": {
        "back": "get_channel_select_embed",
        "next": "get_finish_mode_embed"
    },
    "get_reception_skipped_embed": {
        "back": "get_reception_mode_question_embed",
        "next": "get_finish_mode_embed"
    },
    "get_finish_mode_embed": {
        "back": "get_setup_embed",
        "next": None
    },
    "get_log_info_embed": {
        "back": "get_setup_embed",
        "next": "get_log_confirm_embed"
    },
    "get_log_confirm_embed": {
        "back": "get_log_info_embed",
        "next": [
            "get_log_activated_embed",
            "get_log_deactivated_embed"
        ]
    },
    "get_log_activated_embed": {
        "back": "get_setup_embed",
        "next": None
    },
    "get_log_deactivated_embed": {
        "back": "get_setup_embed",
        "next": None
    },
    "get_delete_mode_embed": {
        "back": "get_setup_embed",
        "next": [
            "get_delete_confirm_embed",
            "get_delete_error_embed"
        ]
    },
    "get_delete_confirm_embed": {
        "back": "get_delete_mode_embed",
        "next": [
            "get_delete_success_embed",
            "get_delete_error_embed"
        ]
    },
    "get_delete_success_embed": {
        "back": "get_setup_embed",
        "next": None
    },
    "get_delete_error_embed": {
        "back": "get_delete_mode_embed", 
        "next": None
    },
    "get_switch_mode_list_embed": {
        "back": "get_setup_embed",
        "next": [
            "get_switch_success_embed",
            "get_switch_error_embed"
        ]
    },
    "get_switch_success_embed": {
        "next": None,
        "back": "get_setup_embed"
    },
    "get_switch_error_embed": {
        "next": None,
        "back": "get_setup_embed"
    },
    "get_switch_not_found_embed": {
        "next": None,
        "back": "get_switch_mode_list_embed"
    }
}

# State to embed mapping
estado_to_embed = {
    "idioma": "get_language_embed",
    "apresentacao": "get_greeting_embed",
    "setup": "get_setup_embed",
    "about": "get_about_embed",
    "functions": "get_functions_embed",
    "roles": "get_roles_embed",
    "edit": "get_edit_embed",
    "iniciando_edicao": "get_mode_selected_embed",
    "erro_iniciacao_edicao": "get_invalid_mode_embed",
    "criando_modo": "get_create_embed",
    "inicial_criacao": "get_initial_create_embed",
    "nome_salvo": "get_name_saved_embed",
    "nome_conflito": "get_name_conflict_embed",
    "nome_invalido": "get_invalid_name_embed",
    "selecionando_cargo": "get_role_select_embed",
    "cargo_salvo": "get_role_saved_embed",
    "cargo_invalido": "get_invalid_role_embed",
    "selecionando_canal": "get_channel_select_embed",
    "canal_salvo": "get_channel_saved_embed",
    "canal_invalido": "get_invalid_channel_embed",
    "canal_conflito": "get_channel_conflict_warning_embed",
    "canal_removido": "get_channel_removed_warning_embed",
    "modo_recepcao_pergunta": "get_reception_mode_question_embed",
    "modo_recepcao_atribuido": "get_reception_assigned_embed",
    "modo_recepcao_trocado": "get_reception_replaced_embed",
    "modo_recepcao_pulado": "get_reception_skipped_embed",
    "finalizado": "get_finish_mode_embed",
    "log_info": "get_log_info_embed",
    "log_confirm": "get_log_confirm_embed",
    "log_ativado": "get_log_activated_embed",
    "log_desativado": "get_log_deactivated_embed",
    "apagando_modo": "get_delete_mode_embed",
    "confirmando_exclusao": "get_delete_confirm_embed", 
    "exclusao_sucesso": "get_delete_success_embed",
    "exclusao_erro": "get_delete_error_embed",
    "selecionando_modo_trocar": "get_switch_mode_list_embed",
    "troca_sucesso": "get_switch_success_embed", 
    "troca_erro": "get_switch_error_embed",
    "troca_nao_encontrado": "get_switch_not_found_embed",
}

embed_to_estado = {v: k for k, v in estado_to_embed.items()}

# Embed functions dictionary
EMBEDS = {
    "get_language_embed": get_language_embed,
    "get_greeting_embed": get_greeting_embed,
    "get_setup_embed": get_setup_embed,
    "get_about_embed": get_about_embed,
    "get_functions_embed": get_functions_embed,
    "get_roles_embed": get_roles_embed,
    "get_edit_embed": get_edit_embed,
    "get_invalid_mode_embed": get_invalid_mode_embed,
    "get_mode_selected_embed": get_mode_selected_embed,
    "get_create_embed": get_create_embed,
    "get_initial_create_embed": get_initial_create_embed,
    "get_name_saved_embed": get_name_saved_embed,
    "get_invalid_name_embed": get_invalid_name_embed,
    "get_name_conflict_embed": get_name_conflict_embed,
    "get_role_select_embed": get_role_select_embed,
    "get_role_saved_embed": get_role_saved_embed,
    "get_invalid_role_embed": get_invalid_role_embed,
    "get_channel_select_embed": get_channel_select_embed,
    "get_channel_saved_embed": get_channel_saved_embed,
    "get_invalid_channel_embed": get_invalid_channel_embed,
    "get_channel_conflict_warning_embed": get_channel_conflict_warning_embed,
    "get_channel_removed_warning_embed": get_channel_removed_warning_embed,
    "get_reception_mode_question_embed": get_reception_mode_question_embed,
    "get_reception_assigned_embed": get_reception_assigned_embed,
    "get_reception_replaced_embed": get_reception_replaced_embed,
    "get_reception_skipped_embed": get_reception_skipped_embed,
    "get_finish_mode_embed": get_finish_mode_embed,
    "get_log_info_embed": get_log_info_embed,
    "get_log_confirm_embed": get_log_confirm_embed,
    "get_log_activated_embed": get_log_activated_embed,
    "get_log_deactivated_embed": get_log_deactivated_embed,
    "get_delete_mode_embed": get_delete_mode_embed,
    "get_delete_confirm_embed": get_delete_confirm_embed,
    "get_delete_success_embed": get_delete_success_embed,
    "get_delete_error_embed": get_delete_error_embed,
    "get_switch_mode_list_embed": get_switch_mode_list_embed,
    "get_switch_success_embed": get_switch_success_embed,
    "get_switch_error_embed": get_switch_error_embed,
    "get_switch_not_found_embed": get_switch_not_found_embed,
}

# Helper functions
logger.debug("[INIT] Módulo de idiomas inicializado")

def push_embed(user_id, estado, *args):
    historico_embeds.setdefault(user_id, []).append((estado, args))
    logger.debug(f"[EMBED] push_embed chamado | user_id={user_id}, estado={estado}, args={args}")

def inicializar_estado_usuario(guild_id, user_id):
    if guild_id not in user_progress:
        user_progress[guild_id] = {}
    
    user_progress[guild_id][user_id] = "get_greeting_embed"
    
    criando_modo.pop(user_id, None)
    modo_ids.pop(user_id, None)
    historico_embeds.pop(user_id, None)
    em_edicao.pop(user_id, None)
    modo_atual.pop(user_id, None)

def verificar_arquivo_idiomas():
    try:
        if os.path.exists(CAMINHO_IDIOMAS):
            with open(CAMINHO_IDIOMAS, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"[VERIFICAÇÃO] Arquivo idiomas.json carregado com {len(data)} servidores")
            return True
        else:
            logger.debug("[VERIFICAÇÃO] Arquivo idiomas.json não existe, será criado automaticamente")
            return False
    except Exception as e:
        logger.error(f"[VERIFICAÇÃO] Erro ao verificar arquivo idiomas.json: {e}")
        return False

def pop_embed(user_id):
    if historico_embeds.get(user_id):
        estado, args = historico_embeds[user_id].pop()
        logger.debug(f"[EMBED] pop_embed retornou | user_id={user_id}, estado={estado}, args={args}")
        return estado, args
    logger.debug(f"[EMBED] pop_embed vazio | user_id={user_id}")
    return None, ()

async def limpar_mensagens(canal, autor1, autor2, quantidade=50):
    def check(msg):
        return msg.author in [autor1, autor2]
    
    mensagens_deletadas = 0
    try:
        deleted = await canal.purge(limit=quantidade, check=check)
        mensagens_deletadas = len(deleted)
        logger.debug(f"[MSG] {mensagens_deletadas} mensagens do bot/user limpas | canal={canal}")
        return mensagens_deletadas
    except Exception as e:
        logger.debug(f"[MSG] Falha no purge ({e}) — usando fallback para deletar manualmente.")
        mensagens_deletadas = 0
        async for m in canal.history(limit=50):
            if m.author in [autor1, autor2]:
                try:
                    await m.delete()
                    mensagens_deletadas += 1
                    logger.debug(f"[MSG] Mensagem manualmente deletada | autor={m.author}")
                except Exception as e:
                    logger.debug(f"[MSG] Falha ao deletar mensagem manualmente: {e}")
        return mensagens_deletadas

async def limpar_mensagem_user(canal, quantidade=50):
    def check(msg):
        return not msg.pinned
    
    mensagens_deletadas = 0
    try:
        deleted = await canal.purge(limit=quantidade, check=check)
        mensagens_deletadas = len(deleted)
        logger.debug(f"[MSG] {mensagens_deletadas} mensagens gerais limpas | canal={canal}")
        return mensagens_deletadas
    except Exception as e:
        logger.debug(f"[MSG] Falha no purge ({e}) — usando fallback para deletar manualmente.")
        mensagens_deletadas = 0
        async for m in canal.history(limit=quantidade):
            if not m.pinned:
                try:
                    await m.delete()
                    mensagens_deletadas += 1
                    logger.debug(f"[MSG] Mensagem geral manualmente deletada")
                except Exception as e:
                    logger.debug(f"[MSG] Falha ao deletar mensagem manualmente: {e}")
        return mensagens_deletadas

async def enviar_embed(canal, user_id, embed):
    try:
        await canal.send(embed=embed)
        logger.debug(f"[EMBED] Enviado com sucesso | user={user_id}, canal={canal}")
    except Exception as e:
        logger.debug(f"[EMBED] Erro ao enviar embed para user={user_id}, canal={canal}: {e}")

# Flow navigation logic
async def go_next(canal, user_id, guild_id, resultado=None):
    logger.debug(f"[FLOW] go_next iniciado | user={user_id}, guild={guild_id}, resultado={resultado}")
    logger.debug(f"[FLOW] Estado atual: {user_progress.get(guild_id, {}).get(user_id)}")

    if guild_id not in user_progress:
        user_progress[guild_id] = {}
    
    if user_id not in user_progress[guild_id]:
        user_progress[guild_id][user_id] = "get_greeting_embed"
        logger.debug(f"[FLOW] Estado inicializado para user={user_id}")

    idioma = obter_idioma(guild_id)
    extra_args = ()

    # Handle tuple results
    if isinstance(resultado, tuple):
        logger.debug(f"[FLOW] Processando resultado como tupla: {resultado}")
        func_name, *extra_args = resultado
        embed_func = EMBEDS.get(func_name) or globals().get(func_name)
        
        if not embed_func:
            logger.error(f"[FLOW] Embed {func_name} não encontrado")
            return
        
        try:
            embed = embed_func(idioma, *extra_args)
            logger.debug(f"[FLOW] Embed gerado: {func_name}")
        except Exception as e:
            logger.error(f"[FLOW] Erro ao gerar embed {func_name}: {e}")
            return

        membro = canal.guild.get_member(user_id)
        await limpar_mensagens(canal, membro, bot.user)
        msg = await canal.send(embed=embed)

        flow_config = flow.get(func_name, {})
        if flow_config.get("back"):
            await msg.add_reaction("🔙")
            logger.debug(f"[FLOW] Reação 🔙 adicionada para {func_name}")
        if flow_config.get("next"):
            await msg.add_reaction("✅")
            logger.debug(f"[FLOW] Reação ✅ adicionada para {func_name}")

        mensagem_voltar_ids[str(guild_id)] = msg.id
        mensagem_avancar_ids[str(guild_id)] = msg.id
        user_progress.setdefault(guild_id, {})[user_id] = func_name
        
        logger.debug(f"[FLOW] Tupla {func_name} processada com sucesso")
        return

    # Normal navigation logic
    current = user_progress.get(guild_id, {}).get(user_id)
    if not current:
        logger.debug("[FLOW] Nenhum estado atual encontrado")
        return

    logger.debug(f"[FLOW] Estado atual: {current}")
    next_step = flow[current].get("next")
    logger.debug(f"[FLOW] Próximo passo do flow: {next_step}")

    if isinstance(next_step, list):
        next_embed_name = resultado if (resultado and resultado in next_step) else next_step[0]
    else:
        next_embed_name = next_step

    logger.debug(f"[FLOW] Próximo embed definido: {next_embed_name}")

    if not next_embed_name:
        logger.debug("[FLOW] Nenhum próximo embed definido")
        return

    embed_func = EMBEDS.get(next_embed_name)
    if not embed_func:
        logger.error(f"[FLOW] Embed {next_embed_name} não encontrado")
        return

    logger.debug(f"[FLOW] Gerando embed: {next_embed_name}")
    embed = None
    try:
        if next_embed_name == "get_role_select_embed":
            roles = [role for role in canal.guild.roles if role.name != "@everyone"]
            embed = embed_func(idioma, roles)
        elif next_embed_name == "get_channel_select_embed":
            channels = canal.guild.channels
            embed = embed_func(idioma)
        elif next_embed_name == "get_delete_mode_embed":
            modos = carregar_modos().get(str(guild_id), {}).get("modos", {})
            embed = embed_func(idioma, modos)
        elif next_embed_name == "get_delete_success_embed":
            modo_id = modo_ids.get(user_id)
            modos = carregar_modos()
            modo_nome = modos.get(str(guild_id), {}).get("modos", {}).get(modo_id, {}).get("nome", "Desconhecido")
            embed = embed_func(idioma, modo_nome)
        elif next_embed_name == "get_delete_error_embed":
            modo_id = modo_ids.get(user_id)
            modos = carregar_modos()
            modo_nome = modos.get(str(guild_id), {}).get("modos", {}).get(modo_id, {}).get("nome", "Desconhecido")
            embed = embed_func(idioma, modo_nome)
        else:
            embed = embed_func(idioma)
        logger.debug(f"[FLOW] Embed {next_embed_name} gerado com sucesso")
    except Exception as e:
        logger.error(f"[FLOW] Erro ao gerar embed {next_embed_name}: {e}")
        return

    user_progress[guild_id][user_id] = next_embed_name
    push_embed(user_id, next_embed_name, *extra_args)

    membro = canal.guild.get_member(user_id)
    await limpar_mensagens(canal, membro, bot.user)
    msg = await canal.send(embed=embed)
    logger.debug(f"[FLOW] Embed {next_embed_name} enviado")

    flow_config = flow.get(next_embed_name, {})
    
    if next_embed_name in ["get_channel_conflict_warning_embed", "get_channel_removed_warning_embed"]:
        await msg.add_reaction("🔙")
        logger.debug(f"[FLOW] Reação 🔙 adicionada para {next_embed_name} (warning - SEM ✅)")
    
    elif next_embed_name in ["get_name_conflict_embed", "get_invalid_name_embed"]:
        await msg.add_reaction("🔙")
        logger.debug(f"[FLOW] Reação 🔙 adicionada para {next_embed_name} (conflito/inválido - SEM ✅)")

    elif next_embed_name in ["get_delete_success_embed", "get_delete_error_embed"]:
        await msg.add_reaction("🔙")
        logger.debug(f"[FLOW] Reação 🔙 adicionada para {next_embed_name}")
    
    elif next_embed_name == "get_reception_mode_question_embed":
        try:
            await msg.add_reaction("🔙")
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            logger.debug(f"[FLOW] Reações 🔙✅❌ adicionadas para recepção")
        except Exception as e:
            logger.warning(f"[FLOW] Não foi possível adicionar reações de recepção: {e}")
    
    else:
        if flow_config.get("back"):
            await msg.add_reaction("🔙")
            logger.debug(f"[FLOW] Reação 🔙 adicionada para {next_embed_name}")
        if flow_config.get("next"):
            await msg.add_reaction("✅")
            logger.debug(f"[FLOW] Reação ✅ adicionada para {next_embed_name}")

    # State specific updates
    if current == "get_name_saved_embed":
        criando_modo[user_id] = "selecionando_cargo"
        logger.debug(f"[FLOW] Estado atualizado: selecionando_cargo")
    elif current == "get_role_saved_embed":
        criando_modo[user_id] = "selecionando_canal"
        logger.debug(f"[FLOW] Estado atualizado: selecionando_canal")
    elif next_embed_name == "get_name_saved_embed":
        criando_modo[user_id] = "nome_salvo"
        logger.debug(f"[FLOW] Estado atualizado: nome_salvo")
    elif next_embed_name == "get_name_conflict_embed":
        criando_modo[user_id] = "nome_conflito"
        logger.debug(f"[FLOW] Estado atualizado: nome_conflito")
    elif next_embed_name == "get_invalid_name_embed":
        criando_modo[user_id] = "nome_invalido"
        logger.debug(f"[FLOW] Estado atualizado: nome_invalido")
    elif next_embed_name == "get_finish_mode_embed":
        await finalizar_modo_fluxo(canal, user_id, guild_id, idioma)
    elif next_embed_name == "get_role_select_embed":
        criando_modo[user_id] = "selecionando_cargo"
        logger.debug(f"[FLOW] Estado atualizado: selecionando_cargo")
    elif next_embed_name == "get_channel_select_embed":
        criando_modo[user_id] = "selecionando_canal"
        logger.debug(f"[FLOW] Estado atualizado: selecionando_canal")

    logger.debug(f"[FLOW] go_next concluído | user={user_id}, next={next_embed_name}")

# Finalize flow process
async def finalizar_modo_fluxo(canal, user_id, guild_id, idioma):
    logger.debug(f"[FLOW] Finalizando modo | user={user_id}, guild={guild_id}")
    
    modos = carregar_modos()
    guild_id_str = str(guild_id)
    modo_id = modo_ids.get(user_id)
    
    if modo_id:
        modo_atual_guild = modos.get(guild_id_str, {}).get("modos", {}).get(modo_id)
        if modo_atual_guild:
            if not modo_atual_guild.get("finalizado"):
                modo_atual_guild["finalizado"] = True
                modo_atual_guild["em_edicao"] = False
                salvar_modos(modos)
                MODOS_CACHE[guild_id_str]["modos"][modo_id] = modo_atual_guild
                logger.info(f"[FLOW] Modo {modo_id} finalizado e salvo")
            else:
                logger.debug(f"[FLOW] Modo {modo_id} já estava finalizado")
        else:
            logger.warning(f"[FLOW] Modo {modo_id} não encontrado no servidor")

    resetar_estado_usuario(guild_id, user_id)
    criando_modo[user_id] = "finalizado"

    try:
        embed = get_finish_mode_embed(idioma)
        membro = canal.guild.get_member(user_id)
        await limpar_mensagens(canal, membro, bot.user)
        msg = await canal.send(embed=embed)
        
        await msg.add_reaction("🔙")
        
        user_progress.setdefault(guild_id, {})[user_id] = "get_finish_mode_embed"
        criando_modo[user_id] = None
        logger.debug(f"[FLOW] Estado final resetado para user={user_id}")
    except Exception as e:
        logger.error(f"[FLOW] Falha ao enviar embed final: {e}")

# Back navigation logic
async def go_back(canal, user_id, guild_id):
    logger.debug(f"[FLOW] go_back iniciado | user={user_id}, guild={guild_id}")

    current = user_progress.get(guild_id, {}).get(user_id)
    if not current:
        logger.debug("[FLOW] Nenhum estado atual encontrado para voltar")
        return

    logger.debug(f"[FLOW] Estado atual: {current}")
    idioma = obter_idioma(guild_id)

    back_embed = flow[current].get("back")
    logger.debug(f"[FLOW] Embed anterior do flow: {back_embed}")

    if not back_embed:
        logger.debug("[FLOW] Nenhum embed anterior definido")
        return

    if back_embed == "get_delete_mode_embed":
        criando_modo[user_id] = "apagando_modo"
        logger.debug("[DELETE] Retornando para lista de modos para apagar")

    embed_func = EMBEDS.get(back_embed)
    if not embed_func:
        logger.error(f"[FLOW] Embed {back_embed} não encontrado")
        return

    logger.debug(f"[FLOW] Gerando embed anterior: {back_embed}")
    embed = None
    try:
        if back_embed == "get_role_select_embed":
            roles = [r for r in canal.guild.roles if not r.is_default()]
            embed = embed_func(idioma, roles)
        elif back_embed == "get_channel_select_embed":
            channels = canal.guild.channels
            embed = embed_func(idioma)
        elif back_embed == "get_create_embed":
            embed = embed_func(canal.guild)
        elif back_embed == "get_roles_embed":
            roles = [role for role in canal.guild.roles if not role.is_default()]
            embed = embed_func(roles, idioma, canal.guild) if hasattr(embed_func, '__code__') and embed_func.__code__.co_argcount > 2 else embed_func(idioma)
        elif back_embed == "get_edit_embed":
            embed = embed_func(guild_id, idioma)
        elif back_embed == "get_delete_mode_embed":
            modos = carregar_modos().get(str(guild_id), {}).get("modos", {})
            embed = embed_func(idioma, modos)
        else:
            embed = embed_func(idioma)
        
        logger.debug(f"[FLOW] Embed {back_embed} gerado com sucesso")
    except Exception as e:
        logger.error(f"[FLOW] Erro ao gerar embed {back_embed}: {e}")
        return

    membro = canal.guild.get_member(user_id)
    await limpar_mensagens(canal, membro, bot.user)
    msg = await canal.send(embed=embed)
    logger.debug(f"[FLOW] Embed {back_embed} enviado")

    flow_config = flow.get(back_embed, {})

    if back_embed == "get_delete_mode_embed":
        await msg.add_reaction("🔙")
        logger.debug(f"[FLOW] Reação 🔙 adicionada para {back_embed} (exclusão)")
    else:
        if flow_config.get("back"):
            await msg.add_reaction("🔙")
            logger.debug(f"[FLOW] Reação 🔙 adicionada para {back_embed}")
        if flow_config.get("next"):
            await msg.add_reaction("✅")
            logger.debug(f"[FLOW] Reação ✅ adicionada para {back_embed}")

# Update user state
    user_progress.setdefault(guild_id, {})[user_id] = back_embed
    
    # Update mode creation state based on embed
    estado_correspondente = embed_to_estado.get(back_embed)
    if estado_correspondente:
        criando_modo[user_id] = estado_correspondente
        logger.debug(f"[FLOW] criando_modo atualizado para: {estado_correspondente}")

    # Clean duplicate history
    if user_id in historico_embeds:
        historico_embeds[user_id] = [
            (e, a) for e, a in historico_embeds[user_id] 
            if e != back_embed and e != current
        ]

    # Add to history
    push_embed(user_id, back_embed)

    # Special state handling
    if back_embed == "get_setup_embed":
        logger.debug(f"[FLOW] Retornando para setup - resetando estado")
        reset_edicao(guild_id, user_id)
        em_edicao[user_id] = False
        modo_atual[user_id] = None
        modo_ids.pop(user_id, None)
        criando_modo[user_id] = None
        limpar_modos_incompletos(guild_id)
        logger.debug("[FLOW] Estado de edição resetado")

    logger.debug(f"[FLOW] go_back concluído | user={user_id}, back={back_embed}")

async def apagar_modo_completo(guild_id, modo_id):
    # Full mode deletion including channel resets
    try:
        logger.debug(f"[DELETE] Iniciando apagamento completo do modo {modo_id} no servidor {guild_id}")
        
        modos = carregar_modos()
        guild_id_str = str(guild_id)
        
        if guild_id_str not in modos or modo_id not in modos[guild_id_str]["modos"]:
            logger.warning(f"[DELETE] Modo {modo_id} não encontrado no servidor {guild_id}")
            return False

        modo = modos[guild_id_str]["modos"][modo_id]
        modo_nome = modo.get("nome", "Desconhecido")
        
        # Get guild instance
        guild = bot.get_guild(guild_id)
        if not guild:
            logger.error(f"[DELETE] Guild {guild_id} não encontrada")
            return False

        # Prepare channel reset data
        canais_para_resetar = modo.get("channels", [])
        cargo_id = modo.get("roles", [None])[0] if modo.get("roles") else None
        cargo = guild.get_role(int(cargo_id)) if cargo_id else None
        
        logger.debug(f"[DELETE] Resetando {len(canais_para_resetar)} canais do modo '{modo_nome}'")
        
        canais_resetados = 0
        erros_reset = []
        
        # Reset each channel
        for canal_data in canais_para_resetar:
            try:
                canal_id = int(canal_data.id) if hasattr(canal_data, "id") else int(canal_data)
                canal = guild.get_channel(canal_id)
                
                if canal:
                    sucesso = await resetar_permissoes_canal(canal, cargo)
                    if sucesso:
                        canais_resetados += 1
                        logger.debug(f"[DELETE] Canal {canal.name} resetado com sucesso")
                    else:
                        erros_reset.append(f"Canal {canal.name} ({canal.id})")
                else:
                    logger.warning(f"[DELETE] Canal {canal_id} não encontrado no servidor")
                    
            except Exception as e:
                erro_msg = f"Canal {canal_id}: {str(e)}"
                erros_reset.append(erro_msg)
                logger.error(f"[DELETE] Erro ao resetar canal {canal_id}: {e}")

        # Delete mode entry from data
        sucesso_apagar = apagar_modo(guild_id, modo_id)
        
        if sucesso_apagar:
            logger.info(f"[DELETE] Modo '{modo_nome}' ({modo_id}) apagado com sucesso")
            logger.info(f"[DELETE] {canais_resetados}/{len(canais_para_resetar)} canais resetados")
        else:
            logger.error(f"[DELETE] Falha ao apagar modo {modo_id} após resetar canais")
        if erros_reset:
            logger.warning(f"[DELETE] Erros ao resetar canais: {erros_reset}")
        return sucesso_apagar
        
    except Exception as e:
        logger.error(f"[DELETE] Erro crítico ao apagar modo {modo_id}: {e}", exc_info=True)
        return False

async def resetar_permissoes_canal(canal, cargo=None):
    # Restore default channel permissions
    try:
        # Clear specific role overwrites
        if cargo:
            try:
                await canal.set_permissions(cargo, overwrite=None)
                logger.debug(f"[DELETE] Permissões do cargo {cargo.name} removidas do canal {canal.name}")
            except Exception as e:
                logger.warning(f"[DELETE] Não foi possível remover permissões do cargo {cargo.name}: {e}")

        # Apply basic default overwrites for @everyone
        overwrites = {
            canal.guild.default_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                connect=True,
                speak=True
            )
        }
        
        await canal.edit(overwrites=overwrites)
        logger.debug(f"[DELETE] Canal {canal.name} resetado para permissões padrão")
        return True
        
    except discord.Forbidden:
        logger.error(f"[DELETE] Sem permissão para resetar canal {canal.name}")
        return False
    except discord.HTTPException as e:
        logger.error(f"[DELETE] Erro HTTP ao resetar canal {canal.name}: {e}")
        return False
    except Exception as e:
        logger.error(f"[DELETE] Erro inesperado ao resetar canal {canal.name}: {e}")
        return False

# Events
CAMINHO_MAIN = None
CAMINHO_PROJETO = None

def obter_caminho_main():
    # Store project root and main script paths
    global CAMINHO_MAIN, CAMINHO_PROJETO
    caminho_atual = os.path.abspath(__file__)
    CAMINHO_MAIN = caminho_atual
    CAMINHO_PROJETO = Path(caminho_atual).parent.parent
    
    logger.debug(f"[INIT] Caminho do main.py armazenado: {CAMINHO_MAIN}")
    logger.debug(f"[INIT] Caminho da raiz do projeto: {CAMINHO_PROJETO}")
    
    return CAMINHO_MAIN, CAMINHO_PROJETO

def obter_caminho_arquivo(caminho_relativo):
    # Resolve relative paths to absolute project paths
    if CAMINHO_PROJETO is None:
        raise RuntimeError("Caminho do projeto não foi inicializado. Execute obter_caminho_main() primeiro.")
    
    caminho_completo = CAMINHO_PROJETO / caminho_relativo
    logger.debug(f"[PATH] Caminho solicitado: {caminho_relativo} -> {caminho_completo}")

    return caminho_completo

@bot.event
async def on_ready():
    # Bot initialization on ready
    try:
        configurar_logger()
        carregar_config()
        caminho_main, caminho_projeto = obter_caminho_main()
        print(f"Caminho do main.py: {caminho_main}")
        print(f"Caminho da raiz do projeto: {caminho_projeto}")

    except Exception as e:
        print(f"ERRO CRÍTICO na inicialização do Logger/Config: {e}") 
    
    print(f"Usuário conectado: {bot.user}!")
    verificar_arquivo_idiomas()
    logger.info(f'Usuário conectado: {bot.user}! | Prefix usado: {PREFIX}')
    
    # Start background backup task
    if not backup_task.is_running():
        try:
            backup_task.start()
            logger.info("Tarefa de backup iniciada com sucesso!")
        except Exception as e:
            logger.error(f"Falha ao iniciar a backup_task: {e}", exc_info=True)

@bot.event
async def on_guild_join(guild):
    # Language selection on guild join
    logger.info(f"Bot entrou no servidor: {guild.name} (ID: {guild.id})")
    obter_idioma(guild.id)
    
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            try:
                logger.debug(f"Enviando embed de idioma no canal: {channel.name} ({channel.id})")
                
                embed = get_language_embed("en", guild)
                msg = await channel.send(embed=embed)
                await msg.add_reaction("🇺🇸")
                await msg.add_reaction("🇧🇷")
                mensagem_idioma_id[str(guild.id)] = msg.id
                
                logger.info(f"Mensagem de idioma enviada com sucesso em {channel.name}")
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem de idioma em {channel.name}: {e}", exc_info=True)
            break
    else:
        logger.warning(f"Nenhum canal com permissão de envio encontrado em {guild.name}")

@bot.event
async def on_member_join(member):
    # Auto-role assignment on member join
    guild = member.guild
    guild_id = str(guild.id)
    server_modos = carregar_modos().get(guild_id, {}).get("modos", {})
    modo_recepcao = next((m for m in server_modos.values() if m.get("recepcao")), None)
    if not modo_recepcao:
        return
    roles = modo_recepcao.get("roles", [])
    if not roles:
        return
    role = guild.get_role(int(roles[0]))
    if not role:
        return
    try:
        await member.add_roles(role)
        logger.info(f"Cargo de recepção '{role.name}' atribuído a {member.name}")
    except Exception as e:
        logger.error(f"Falha ao atribuir cargo de recepção: {e}", exc_info=True)

@bot.event
async def on_raw_reaction_add(payload):
    # Global reaction handler
    logger.debug(f"[EVENT] on_raw_reaction_add: user={payload.user_id}, emoji={payload.emoji.name}, guild={payload.guild_id}, channel={payload.channel_id}")

    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    canal = bot.get_channel(payload.channel_id)
    if not guild or not canal:
        logger.debug(f"[WARN] Guild ou canal não encontrados para o payload {payload.message_id}")
        return

    user_id = payload.user_id
    guild_id = payload.guild_id
    idioma = obter_idioma(guild_id)
    current = user_progress.get(guild_id, {}).get(user_id)

    logger.debug(f"[TRACE] Reação adicionada por {user_id} em guild {guild_id} | Emoji: {payload.emoji.name} | Current: {current}")

    # Log info confirmation
    if current == "get_log_info_embed" and payload.emoji.name == "✅":
        logger.debug(f"[LOG] Avançando de info para confirm | user={user_id}")

        # Basic cleanup
        finalizar_modos_em_edicao(guild_id, user_id)
        limpar_modos_usuario(guild_id, user_id)
        limpar_modos_incompletos(guild_id)

        # Delete previous message
        try:
            msg_antiga = await canal.fetch_message(payload.message_id)
            await msg_antiga.delete()
            logger.debug(f"[LOG] Mensagem anterior apagada antes de enviar o embed de confirmação")
        except Exception as e:
            logger.warning(f"[LOG] Não foi possível apagar a mensagem anterior: {e}")

        # Send confirmation embed
        config = carregar_config()
        debug_logs = config.get("debug_logs", False)

        msg = await canal.send(embed=get_log_confirm_embed(idioma, debug_logs))

        try:
            await msg.add_reaction("🔙")
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
        except Exception as e:
            logger.warning(f"[LOG] Falha ao adicionar reações: {e}")

        user_progress[guild_id][user_id] = "get_log_confirm_embed"
        return

    # Log state confirmation
    if current == "get_log_confirm_embed":
        member = guild.get_member(user_id)
        if not member or not member.guild_permissions.manage_guild:
            logger.warning(f"[LOG] Usuário {user_id} sem permissão para alterar logs em guild {guild_id}")
            return

        # Enable logs
        if payload.emoji.name == "✅":
            try:
                config = carregar_config()
                config["debug_enabled"] = True
                config["debug_logs"] = True  
                salvar_config(config)
                configurar_logger()
                logger.info(f"[LOG] Debug mode ATIVADO via fluxo pelo usuário {user_id} no servidor {guild_id}")
            except Exception as e:
                logger.exception(f"[LOG] Falha ao ativar debug via fluxo: {e}")

            await go_next(canal, user_id, guild_id, resultado="get_log_activated_embed")
            return

        # Disable logs
        if payload.emoji.name == "❌":
            try:
                config = carregar_config()
                config["debug_enabled"] = False
                config["debug_logs"] = False  
                salvar_config(config)
                configurar_logger()
                logger.info(f"[LOG] Debug mode DESATIVADO via fluxo pelo usuário {user_id} no servidor {guild_id}")
            except Exception as e:
                logger.exception(f"[LOG] Falha ao desativar debug via fluxo: {e}")

            await go_next(canal, user_id, guild_id, resultado="get_log_deactivated_embed")
            return

    # Language selection
    if str(guild_id) in mensagem_idioma_id and mensagem_idioma_id[str(guild_id)] == payload.message_id:
        logger.debug(f"[IDIOMA] Reação de idioma detectada: {payload.emoji.name} por {user_id}")
        
        if payload.emoji.name == "🇧🇷":
            definir_idioma(guild_id, "pt")
            idioma = "pt"
            logger.debug(f"[IDIOMA] Idioma definido como português para guild {guild_id}")
        elif payload.emoji.name == "🇺🇸":
            definir_idioma(guild_id, "en")
            idioma = "en"
            logger.debug(f"[IDIOMA] Idioma definido como inglês para guild {guild_id}")
        else:
            logger.debug(f"[IDIOMA] Emoji não reconhecido: {payload.emoji.name}")
            return

        try:
            # Remove reaction
            msg = await canal.fetch_message(payload.message_id)
            await msg.remove_reaction(payload.emoji, payload.member)
            logger.debug(f"[IDIOMA] Reação removida da mensagem")
        except Exception as e:
            logger.debug(f"[IDIOMA] Não foi possível remover reação: {e}")

        try:
            # Delete message
            await msg.delete()
            logger.debug(f"[IDIOMA] Mensagem de idioma deletada")
            
            # Initialize state
            if guild_id not in user_progress:
                user_progress[guild_id] = {}
            user_progress[guild_id][user_id] = "get_greeting_embed"
            
            # Send greeting
            embed_greeting = get_greeting_embed(idioma)
            msg_greeting = await canal.send(embed=embed_greeting)
            
            # Add reaction
            await msg_greeting.add_reaction("✅")
            
            # Update IDs
            mensagem_avancar_ids[str(guild_id)] = msg_greeting.id
            
            logger.debug(f"[IDIOMA] Embed de greeting enviado com sucesso")
            
        except Exception as e:
            logger.error(f"[IDIOMA] Erro no processamento pós-seleção: {e}", exc_info=True)
        return
    
    # Back navigation
    if payload.emoji.name == "🔙":
        logger.debug(f"[NAVEGAÇÃO] Usuário {user_id} reagiu com 🔙 em guild {guild_id}")
        
        # Delete confirmation back
        if current == "get_delete_confirm_embed":
            logger.debug(f"[DELETE] Usuário {user_id} voltou da confirmação para lista de modos")
            modo_ids.pop(user_id, None)
            criando_modo[user_id] = "apagando_modo"
            await go_back(canal, user_id, guild_id)
            return
        
        await go_back(canal, user_id, guild_id)
        return

    # Switch mode navigation
    if payload.emoji.name == "🔙" and current in ["get_switch_success_embed", "get_switch_error_embed", "get_switch_not_found_embed"]:
        logger.debug(f"[FLOW] Reação 🔙 detectada para {current} - seguindo flow")
        await go_back(canal, user_id, guild_id)
        return

    # Next navigation
    elif payload.emoji.name == "✅":
        logger.debug(f"[NAVEGAÇÃO] Reação de AVANÇAR detectada | user={user_id} | current={current}")

        if current == "get_mode_selected_embed":
            logger.debug(f"[CRIAÇÃO] Usuário {user_id} entrou no modo de criação de modo (esperando nome)")
            criando_modo[user_id] = "esperando_nome"
            await go_next(canal, user_id, guild_id)
            return
        
    # Delete mode confirmation
    if current == "get_delete_confirm_embed":
        modo_id = modo_ids.get(user_id)
        
        if payload.emoji.name == "✅":
            # Confirm delete
            if modo_id:
                modos = carregar_modos()
                modo_nome = modos.get(str(guild_id), {}).get("modos", {}).get(modo_id, {}).get("nome", "Desconhecido")

                sucesso = await apagar_modo_completo(guild_id, modo_id)
                
                if sucesso:
                    logger.info(f"[DELETE] Modo {modo_id} apagado por {user_id}")
                    await go_next(canal, user_id, guild_id, resultado="get_delete_success_embed")
                else:
                    logger.error(f"[DELETE] Falha ao apagar modo {modo_id}")
                    await go_next(canal, user_id, guild_id, resultado="get_delete_error_embed")
            else:
                logger.warning(f"[DELETE] Nenhum modo_id encontrado para confirmação")
                await go_next(canal, user_id, guild_id, resultado="get_delete_error_embed")
            
            # Clean state
            modo_ids.pop(user_id, None)
            criando_modo.pop(user_id, None)
            return

        elif current == "get_reception_mode_question_embed":
            logger.debug(f"[RECEPÇÃO] Usuário {user_id} confirmou recepção | guild={guild_id}")
            modo_id = modo_ids.get(user_id)
            if not modo_id:
                logger.warning(f"[RECEPÇÃO] Nenhum modo_id encontrado para o usuário {user_id}")
                return

            modos = carregar_modos()
            modo = modos.get(str(guild_id), {}).get("modos", {}).get(modo_id)
            if not modo:
                logger.warning(f"[RECEPÇÃO] Modo {modo_id} não encontrado para guild {guild_id}")
                return

            novo_cargo_id = int(modo["roles"][0]) if modo.get("roles") else None
            cargo_antigo_id, novo_cargo_id = substituir_cargo(modos, guild_id, modo_id, novo_cargo_id)
            logger.debug(f"[RECEPÇÃO] Cargo antigo: {cargo_antigo_id} | Novo cargo: {novo_cargo_id}")

            # Normalize channels
            raw_canais = modo.get("channels", []) or []
            canais_existentes = []
            for c in raw_canais:
                try:
                    cid = int(c.id) if hasattr(c, "id") else int(c)
                except Exception:
                    try:
                        cid = int(str(c))
                    except Exception:
                        continue
                canais_existentes.append(str(cid))

            logger.debug(f"[RECEPÇÃO] Canais normalizados: {canais_existentes}")

            # Validate channels
            try:
                canais_existentes_no_modo_atual = modo.get("channels", []) or []
                canais_validos, canais_invalidos = validar_canais(guild, canais_existentes, canais_existentes_no_modo_atual)
                logger.debug(f"[RECEPÇÃO] Validação de canais: válidos={canais_validos}, inválidos={canais_invalidos}")
            except Exception as e:
                logger.exception(f"[ERROR] validar_canais falhou: {e}")
                embed = get_channel_removed_warning_embed(idioma, ["(erro ao validar canais)"])
                msg = await canal.send(embed=embed)
                user_progress[guild_id][user_id] = "get_channel_removed_warning_embed"
                await msg.add_reaction("🔙")
                return

            canais_removidos, canais_conflitantes = [], []
            for cid in canais_invalidos:
                ch = guild.get_channel(int(cid))
                if ch:
                    canais_conflitantes.append(cid)
                else:
                    canais_removidos.append(cid)

            if canais_removidos:
                logger.debug(f"[WARN] Canais removidos: {canais_removidos}")
                embed = get_channel_removed_warning_embed(idioma, canais_removidos)
                msg = await canal.send(embed=embed)
                user_progress[guild_id][user_id] = "get_channel_removed_warning_embed"
                await msg.add_reaction("🔙")
                return
            if canais_conflitantes:
                logger.debug(f"[WARN] Canais conflitantes: {canais_conflitantes}")
                embed = get_channel_conflict_warning_embed(idioma, canais_conflitantes)
                msg = await canal.send(embed=embed)
                user_progress[guild_id][user_id] = "get_channel_conflict_warning_embed"
                await msg.add_reaction("🔙")
                return

            novo_role = guild.get_role(novo_cargo_id) if novo_cargo_id else None

            # Get valid channels objects
            canais_validos = []
            for cid in raw_canais:
                ch = guild.get_channel(int(cid))
                if ch:
                    canais_validos.append(ch)

            logger.debug(f"[RECEPÇÃO] Canais válidos obtidos: {[ch.name for ch in canais_validos]}")

            recepcao_anterior = None
            
            # Update reception if role and channels exist
            if novo_role and canais_validos:
                try:
                    for ch in canais_validos:
                        success = await atualizar_permissoes_canal(
                            ch, 
                            novo_role,
                            bot, 
                            overwrite=True,
                            modo_id=modo_id,
                            guild_id=guild_id,
                            user_id=user_id,
                            criando_modo_dict=criando_modo
                        )

                    # Mark mode as reception
                    for mid, mdata in modos[str(guild_id)]["modos"].items():
                        mdata["recepcao"] = False
                    modos[str(guild_id)]["modos"][modo_id]["recepcao"] = True

                    # Save updated modes
                    salvar_modos(modos)
                    MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = modos[str(guild_id)]["modos"][modo_id]

# Apply reception settings
                    recepcao_anterior = await atribuir_recepcao(
                        guild,
                        modo_id,
                        canais_validos,
                        novo_role,
                        overwrite=True
                    )
                    logger.debug(f"[RECEPÇÃO] Recepção atualizada: cargo={novo_role.name}, canais={len(canais_validos)}")

                except Exception as e:
                    logger.exception(f"[ERROR] Falha ao aplicar recepção para {novo_role.name if novo_role else 'N/A'}: {e}")
            else:
                recepcao_anterior = None
                logger.info(f"[RECEPÇÃO] Nenhum cargo ou canal válido — recepção permanece inalterada")

            # Navigation with embed results
            if recepcao_anterior:
                old_role_id = modos.get(str(guild_id), {}).get("modos", {}).get(recepcao_anterior, {}).get("roles", [None])[0]
                old_role = guild.get_role(int(old_role_id)) if old_role_id else None
                old_name = old_role.name if old_role else "N/A"
                logger.debug(f"[RECEPÇÃO] Recepção substituída: {old_name} → {novo_role.name if novo_role else 'N/A'}")
                await go_next(canal, user_id, guild_id, resultado=("get_reception_replaced_embed", old_name, novo_role.name if novo_role else "N/A"))
            else:
                logger.debug(f"[RECEPÇÃO] Nova recepção atribuída: {novo_role.name if novo_role else 'N/A'}")
                await go_next(canal, user_id, guild_id, resultado=("get_reception_assigned_embed", novo_role.name if novo_role else "N/A"))
            
            # Finalize mode status and save
            try:
                modo = modos[str(guild_id)]["modos"][modo_id]
                if modo.get("finalizado"):
                    logger.debug(f"[CRIAÇÃO] Modo {modo_id} já estava finalizado — pulando duplicação")
                else:
                    modo["finalizado"] = True
                    modo["em_edicao"] = False
                    salvar_modos(modos)
                    MODOS_CACHE[str(guild_id)]["modos"][modo_id] = modo
                    logger.info(f"[CRIAÇÃO] Modo {modo_id} marcado como finalizado com sucesso")

                    # Clear user backup
                    if 'backup_data' in criando_modo and user_id in criando_modo['backup_data']:
                        del criando_modo['backup_data'][user_id]
                        logger.debug(f"[BACKUP] Backup limpo para usuário {user_id}")
                        
            except Exception as e:
                logger.exception(f"[WARN] Falha ao marcar modo {modo_id} como finalizado: {e}")

            # Reset edition flag
            try:
                modos[str(guild_id)]["modos"][modo_id]["em_edicao"] = False
                salvar_modos(modos)
                MODOS_CACHE[str(guild_id)]["modos"][modo_id] = modos[str(guild_id)]["modos"][modo_id]
                logger.debug(f"[CRIAÇÃO] Flag 'em_edicao' resetada para o modo {modo_id}")
            except Exception as e:
                logger.warning(f"[WARN] Não foi possível resetar 'em_edicao' para o modo {modo_id}: {e}")

        else:
            await go_next(canal, user_id, guild_id)
            logger.debug(f"[NAVEGAÇÃO] Avançando para o próximo passo após reação ✅ para user_id={user_id}")
    
    # Navigation confirmation logic
    elif payload.emoji.name == "✅":
        if current == "get_mode_selected_embed":
            logger.debug(f"[CRIAÇÃO] Usuário {user_id} confirmou seleção de modo — aguardando nome")
            criando_modo[user_id] = "esperando_nome"
            await go_next(canal, user_id, guild_id)
            return

        elif current == "get_reception_mode_question_embed":
            modo_id = modo_ids.get(user_id)
            if not modo_id:
                logger.warning(f"[RECEPÇÃO] Nenhum modo_id encontrado para usuário {user_id}")
                return

            modos = carregar_modos()
            modo = modos.get(str(guild_id), {}).get("modos", {}).get(modo_id)
            if not modo:
                logger.warning(f"[RECEPÇÃO] Modo {modo_id} não encontrado para o usuário {user_id}")
                return

            novo_cargo_id = int(modo["roles"][0]) if modo.get("roles") else None
            cargo_antigo_id, novo_cargo_id = substituir_cargo(modos, guild_id, modo_id, novo_cargo_id)
            logger.debug(f"[RECEPÇÃO] Substituição de cargo concluída: antigo={cargo_antigo_id}, novo={novo_cargo_id}")

            # Normalize channel list
            raw_canais = modo.get("channels", []) or []
            canais_existentes = []
            for c in raw_canais:
                try:
                    cid = int(c.id) if hasattr(c, "id") else int(c)
                except Exception:
                    try:
                        cid = int(str(c))
                    except Exception:
                        continue
                canais_existentes.append(str(cid))
            logger.debug(f"[RECEPÇÃO] Canais normalizados para o modo {modo_id}: {canais_existentes}")

            # Validate channels and handle errors
            try:
                canais_existentes_no_modo_atual = modo.get("channels", []) or []
                canais_validos, canais_invalidos = validar_canais(guild, canais_existentes, canais_existentes_no_modo_atual)
                logger.debug(f"[RECEPÇÃO] Canais válidos: {canais_validos} | inválidos: {canais_invalidos}")
            except Exception as e:
                logger.error(f"[ERROR] Erro ao validar canais no modo {modo_id}: {e}", exc_info=True)
                embed = get_channel_removed_warning_embed(idioma, ["(erro ao validar canais)"])
                msg = await canal.send(embed=embed)
                user_progress[guild_id][user_id] = "get_channel_removed_warning_embed"
                await msg.add_reaction("🔙")
                return

            canais_removidos, canais_conflitantes = [], []
            for cid in canais_invalidos:
                ch = guild.get_channel(int(cid))
                if ch:
                    canais_conflitantes.append(cid)
                else:
                    canais_removidos.append(cid)

            # Handle removed or conflicting channels
            if canais_removidos:
                logger.info(f"[WARN] Canais removidos detectados: {canais_removidos}")
                embed = get_channel_removed_warning_embed(idioma, canais_removidos)
                msg = await canal.send(embed=embed)
                user_progress[guild_id][user_id] = "get_channel_removed_warning_embed"
                await msg.add_reaction("🔙")
                return
            if canais_conflitantes:
                logger.info(f"[WARN] Canais conflitantes detectados: {canais_conflitantes}")
                embed = get_channel_conflict_warning_embed(idioma, canais_conflitantes)
                msg = await canal.send(embed=embed)
                user_progress[guild_id][user_id] = "get_channel_conflict_warning_embed"
                await msg.add_reaction("🔙")
                return

            novo_role = guild.get_role(novo_cargo_id) if novo_cargo_id else None

            # Resolve valid channel objects
            canais_validos = []
            for cid in raw_canais:
                ch = guild.get_channel(int(cid))
                if ch:
                    canais_validos.append(ch)
            logger.debug(f"[RECEPÇÃO] Canais válidos resolvidos: {[c.name for c in canais_validos]}")

            recepcao_anterior = None
            
            # Update permissions and set main reception
            if novo_role and canais_validos:
                try:
                    for ch in canais_validos:
                        success = await atualizar_permissoes_canal(
                            ch, 
                            novo_role,
                            bot, 
                            overwrite=True,
                            modo_id=modo_id,
                            guild_id=guild_id,
                            user_id=user_id,
                            criando_modo_dict=criando_modo
                        )
                    logger.info(f"[RECEPÇÃO] Permissões atualizadas para cargo '{novo_role.name}' em {len(canais_validos)} canais")

                    for mid, mdata in modos[str(guild_id)]["modos"].items():
                        mdata["recepcao"] = False
                    modos[str(guild_id)]["modos"][modo_id]["recepcao"] = True

                    salvar_modos(modos)
                    MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = modos[str(guild_id)]["modos"][modo_id]
                    logger.info(f"[RECEPÇÃO] Modo {modo_id} definido como recepção principal no servidor {guild.name}")

                    # Final assignment
                    recepcao_anterior = await atribuir_recepcao(
                        guild,
                        modo_id,
                        canais_validos,
                        novo_role,
                        overwrite=True
                    )
                except Exception as e:
                    logger.error(f"[ERROR] Falha ao aplicar recepção para '{novo_role.name if novo_role else 'N/A'}': {e}", exc_info=True)
            else:
                recepcao_anterior = None
                logger.info(f"[RECEPÇÃO] Nenhum cargo definido — recepção permanece inalterada")

            # Navigation based on assignment result
            if recepcao_anterior:
                old_role_id = modos.get(str(guild_id), {}).get("modos", {}).get(recepcao_anterior, {}).get("roles", [None])[0]
                old_role = guild.get_role(int(old_role_id)) if old_role_id else None
                old_name = old_role.name if old_role else "N/A"
                logger.debug(f"[RECEPÇÃO] Recepção substituída: {old_name} → {novo_role.name if novo_role else 'N/A'}")
                await go_next(canal, user_id, guild_id, resultado=("get_reception_replaced_embed", old_name, novo_role.name if novo_role else "N/A"))
            else:
                logger.debug(f"[RECEPÇÃO] Nova recepção atribuída: {novo_role.name if novo_role else 'N/A'}")
                await go_next(canal, user_id, guild_id, resultado=("get_reception_assigned_embed", novo_role.name if novo_role else "N/A"))
            
            # Persist finalized mode state
            try:
                modo = modos[str(guild_id)]["modos"][modo_id]
                if modo.get("finalizado"):
                    logger.info(f"[CRIAÇÃO] Modo {modo_id} já estava finalizado — pulando duplicação")
                else:
                    modo["finalizado"] = True
                    modo["em_edicao"] = False
                    salvar_modos(modos)
                    MODOS_CACHE[str(guild_id)]["modos"][modo_id] = modo
                    logger.info(f"[CRIAÇÃO] Modo {modo_id} marcado como finalizado com sucesso")
            except Exception as e:
                logger.warning(f"[WARN] Falha ao marcar modo {modo_id} como finalizado: {e}", exc_info=True)

            # Cleanup user session
            resetar_estado_usuario(guild_id, user_id)
            logger.debug(f"[ESTADO] Estado do usuário {user_id} resetado em {guild_id}")

            # Reset edition flag safety
            try:
                modos[str(guild_id)]["modos"][modo_id]["em_edicao"] = False
                salvar_modos(modos)
                MODOS_CACHE[str(guild_id)]["modos"][modo_id] = modos[str(guild_id)]["modos"][modo_id]
                logger.debug(f"[CRIAÇÃO] Flag 'em_edicao' resetada para modo {modo_id}")
            except Exception as e:
                logger.warning(f"[WARN] Não foi possível resetar 'em_edicao' para modo {modo_id}: {e}", exc_info=True)

        elif current == "get_finish_mode_embed": 
            # Final state cleanup
            resetar_estado_usuario(guild_id, user_id)
            logger.debug(f"[ESTADO] Estado do usuário {user_id} resetado (etapa final)")
            return
        else:
            await go_next(canal, user_id, guild_id)
            logger.debug(f"[NAVEGAÇÃO] Avançando para o próximo passo de {user_id} em {guild_id}")

    # Reception response handling
    elif current in ("get_reception_replaced_embed", "get_reception_skipped_embed", "get_reception_assigned_embed"):
        logger.debug(f"[RECEPÇÃO] Recepção ({current}) detectada para usuário {user_id} em {guild_id}. Avançando para o próximo passo")
        await go_next(canal, user_id, guild_id)
        logger.info(f"[RECEPÇÃO] Usuário {user_id} avançou após recepção ({current}) em {guild_id}")
        return
    
    # Skip reception logic (X reaction)
    elif payload.emoji.name == "❌" and current == "get_reception_mode_question_embed":
        logger.debug(f"[RECEPÇÃO] Reação ❌ detectada — usuário {user_id}, guilda {guild_id}. Iniciando rotina de pular recepção")
        modo_id = modo_ids.get(user_id)
        if not modo_id:
            logger.warning(f"[RECEPÇÃO] Nenhum modo_id encontrado para usuário {user_id} em guilda {guild_id}")
            return

        modos = carregar_modos()
        modo = modos.get(str(guild_id), {}).get("modos", {}).get(modo_id)
        if not modo:
            logger.warning(f"[RECEPÇÃO] Modo inexistente ({modo_id}) para usuário {user_id} em guilda {guild_id}")
            return

        cargo_id = int(modo["roles"][0]) if modo.get("roles") else None
        role = guild.get_role(cargo_id) if cargo_id else None

        # Normalize channel IDs
        raw_canais = modo.get("channels", [])
        canais_existentes = []
        for c in raw_canais:
            try:
                cid = int(c.id) if hasattr(c, "id") else int(c)
            except Exception:
                try:
                    cid = int(str(c))
                except Exception:
                    continue
            canais_existentes.append(str(cid))

        canais_existentes_no_modo_atual = modo.get("channels", []) or []

        # Validate channel availability
        try:
            canais_validos, canais_invalidos = validar_canais(
                guild,
                canais_existentes,
                canais_existentes_no_modo_atual
            )
        except Exception as e:
            logger.exception(f"[ERROR] Erro ao validar canais no ❌ (usuário {user_id}, guilda {guild_id}): {e}")
            embed = get_channel_removed_warning_embed(idioma, ["(erro ao validar canais)"])
            msg = await canal.send(embed=embed)
            user_progress[guild_id][user_id] = "get_channel_removed_warning_embed"
            await msg.add_reaction("🔙")
            return

        canais_removidos, canais_conflitantes = [], []
        for cid in canais_invalidos:
            ch = guild.get_channel(int(cid))
            if ch:
                canais_conflitantes.append(cid)
            else:
                canais_removidos.append(cid)

        # Handle validation warnings
        if canais_removidos:
            logger.warning(f"[WARN] Canais removidos detectados no ❌: {canais_removidos}")
            embed = get_channel_removed_warning_embed(idioma, canais_removidos)
            msg = await canal.send(embed=embed)
            user_progress[guild_id][user_id] = "get_channel_removed_warning_embed"
            await msg.add_reaction("🔙")
            return
        if canais_conflitantes:
            logger.warning(f"[WARN] Canais conflitantes detectados no ❌: {canais_conflitantes}")
            embed = get_channel_conflict_warning_embed(idioma, canais_conflitantes)
            msg = await canal.send(embed=embed)
            user_progress[guild_id][user_id] = "get_channel_conflict_warning_embed"
            await msg.add_reaction("🔙")
            return

        # Map channel objects
        canais_validos = []
        for cid in raw_canais:
            ch = guild.get_channel(int(cid))
            if ch:
                canais_validos.append(ch)

        # Update role permissions
        if role and canais_validos:
            try:
                for ch in canais_validos:
                    success = await atualizar_permissoes_canal(
                        ch, 
                        role,
                        bot, 
                        overwrite=True,
                        modo_id=modo_id,
                        guild_id=guild_id,
                        user_id=user_id,
                        criando_modo_dict=criando_modo
                    )
                logger.info(f"[RECEPÇÃO] Permissões atualizadas para cargo '{role.name}' ({role.id}) nos canais válidos: {len(canais_validos)}")
            except Exception as e:
                logger.exception(f"[ERROR] Falha ao atualizar permissões no ❌ (cargo {role.name if role else 'N/A'}) — {e}")

        # Finish mode before skipping
        role_name = role.name if role else "N/A"
        try:
            modo = modos[str(guild_id)]["modos"][modo_id]
            if modo.get("finalizado"):
                logger.debug(f"[CRIAÇÃO] Modo {modo_id} já estava finalizado — pulando duplicação no ❌")
            else:
                modo["finalizado"] = True
                modo["em_edicao"] = False
                salvar_modos(modos)
                MODOS_CACHE[str(guild_id)]["modos"][modo_id] = modo
                logger.info(f"[CRIAÇÃO] Modo {modo_id} finalizado corretamente antes do skip (❌)")
        except Exception as e:
            logger.warning(f"[WARN] Falha ao marcar modo {modo_id} como finalizado no skip: {e}")

        # Final skip navigation
        logger.debug(f"[RECEPÇÃO] Avançando fluxo pós-skip (❌) para usuário {user_id} em guilda {guild_id}, role_name={role_name}")
        await go_next(canal, user_id, guild_id, resultado=("get_reception_skipped_embed", role_name))
        logger.debug(f"[RECEPÇÃO] Fluxo de skip (❌) concluído para usuário {user_id}")

# Message event handler
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    guild_id = message.guild.id if message.guild else None
    
    # Priority check: block hashtag messages outside valid flows
    if message.content.startswith("#"):
        current = user_progress.get(guild_id, {}).get(user_id)
        estado = criando_modo.get(user_id)
        
        # Permitted hashtag states
        estados_validos_hashtag = [
            "get_edit_embed",
            "get_delete_mode_embed",
            "get_switch_mode_list_embed",
            "esperando_nome",
            "get_initial_create_embed",
            "iniciando_edicao",
            "nome_salvo",
            "nome_conflito",
            "nome_invalido",
            "selecionando_canal"
        ]
        
        if current not in estados_validos_hashtag and estado not in estados_validos_hashtag:
            return
    
    # Priority check: ignore non-commands outside active flow
    if not message.content.startswith(PREFIX) and user_id not in criando_modo:
        return

    # Language and state initialization
    idioma = obter_idioma(guild_id) if guild_id else "pt"
    estado = criando_modo.get(user_id)
    current = user_progress.get(guild_id, {}).get(user_id)
    logger.debug(f"[DEBUG] on_message - User: {user_id}, Current: {current}, Content: {message.content}")

    # Priority check: mode switching
    current = user_progress.get(guild_id, {}).get(user_id)
    if current == "get_switch_mode_list_embed" and message.content.startswith("#"):
        nome_modo = message.content[1:].strip()
        modo_id = modo_existe(guild_id, nome_modo)
        
        logger.debug(f"[TROCAR] Usuário {user_id} selecionou modo '{nome_modo}' para troca")

        if not modo_id:
            logger.warning(f"[TROCAR] Modo '{nome_modo}' não encontrado")
            embed = get_switch_not_found_embed(idioma, nome_modo)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            if guild_id not in user_progress:
                user_progress[guild_id] = {}
            user_progress[guild_id][user_id] = "get_switch_not_found_embed"
            return

        # Apply mode to server
        sucesso, resultado = await aplicar_modo_servidor(message.guild, modo_id, idioma, bot)
        
        if sucesso:
            embed = get_switch_success_embed(idioma, nome_modo)
            estado_resultado = "get_switch_success_embed"
        else:
            logger.error(f"[TROCAR] Falha ao aplicar modo {nome_modo}: {resultado}")
            embed = get_switch_error_embed(idioma, nome_modo)
            estado_resultado = "get_switch_error_embed"

        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("🔙")
        
        if guild_id not in user_progress:
            user_progress[guild_id] = {}
        user_progress[guild_id][user_id] = estado_resultado
        return

    # Priority check: channel selection step
    if estado == "selecionando_canal":
        logger.debug(f"[CANAL] Processando seleção de canal para user={user_id}")
        
        # Name-based channel input with #
        if message.content.startswith("#"):
            nome_canal = message.content[1:].strip()
            logger.debug(f"[CANAL] Tentativa de nome de canal com #: '{nome_canal}'")
            
            canal_encontrado = None
            for ch in message.guild.text_channels + message.guild.voice_channels + message.guild.categories:
                if ch.name.lower() == nome_canal.lower():
                    canal_encontrado = ch
                    break
            
            if canal_encontrado:
                logger.debug(f"[CANAL] Canal encontrado por nome: {canal_encontrado.name}")
                channels = [canal_encontrado]
            else:
                logger.debug(f"[CANAL] Nenhum canal válido encontrado para '{nome_canal}'.")
                embed = get_invalid_channel_embed(idioma)
                await limpar_mensagens(message.channel, bot.user, message.author)
                msg = await message.channel.send(embed=embed)
                user_progress[guild_id][user_id] = "get_invalid_channel_embed"
                await msg.add_reaction("🔙")
                mensagem_voltar_ids[str(guild_id)] = msg.id
                criando_modo[user_id] = "canal_invalido"
                push_embed(user_id, "get_channel_select_embed")
                return
        else:
            # Handle channel mentions or plain name
            channels = list(message.channel_mentions)
            content_lower = message.content.lower()

            for ch in message.guild.text_channels + message.guild.voice_channels + message.guild.categories:
                if ch.name.lower() == content_lower:
                    channels.append(ch)
                    logger.debug(f"[CANAL] Canal encontrado por nome: {ch.name}")

            if not channels:
                logger.debug(f"[CANAL] Nenhum canal válido encontrado para '{message.content}'.")
                embed = get_invalid_channel_embed(idioma)
                await limpar_mensagens(message.channel, bot.user, message.author)
                msg = await message.channel.send(embed=embed)
                user_progress[guild_id][user_id] = "get_invalid_channel_embed"
                await msg.add_reaction("🔙")
                mensagem_voltar_ids[str(guild_id)] = msg.id
                criando_modo[user_id] = "canal_invalido"
                push_embed(user_id, "get_channel_select_embed")
                return

        # Check for removed channels
        canais_removidos = [str(ch.id) for ch in channels if not message.guild.get_channel(ch.id)]
        if canais_removidos:
            logger.debug(f"[VALIDATION] Canais removidos detectados: {canais_removidos}")
            embed = get_channel_removed_warning_embed(idioma, canais_removidos)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            user_progress[guild_id][user_id] = "get_channel_removed_warning_embed"
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "erro_canal"
            push_embed(user_id, "get_channel_select_embed")
            return

        # Conflict check for new modes
        canais_conflito = []
        if not em_edicao.get(user_id, False):
            canais_usados = []
            modos_existentes = carregar_modos().get(str(guild_id), {}).get("modos", {})
            for mid, m in modos_existentes.items():
                if m.get("channels"):
                    canais_usados.extend([str(ch) for ch in m["channels"]])
            canais_conflito = [str(ch.id) for ch in channels if str(ch.id) in canais_usados]

        if canais_conflito:
            logger.debug(f"[VALIDATION] Conflito de canais detectado: {canais_conflito}")
            embed = get_channel_conflict_warning_embed(idioma, canais_conflito)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            user_progress[guild_id][user_id] = "get_channel_conflict_warning_embed"
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "erro_canal"
            push_embed(user_id, "get_channel_select_embed")
            return

        # Persist valid channel selection
        salvar_channels_modo(guild_id, modo_ids[user_id], channels)
        modos = carregar_modos()
        MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_ids[user_id]] = modos[str(guild_id)]["modos"][modo_ids[user_id]]
        salvar_modos(modos)
        logger.debug(f"[CANAL] Canais salvos: {[ch.name for ch in channels]}")

        # Send confirmation and update state
        embed = get_channel_saved_embed(idioma, ", ".join([ch.name for ch in channels]))
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("🔙")
        await msg.add_reaction("✅")

        user_progress.setdefault(guild_id, {})[user_id] = "get_channel_saved_embed"
        push_embed(user_id, "get_channel_select_embed")
        mensagem_voltar_ids[str(guild_id)] = msg.id
        mensagem_avancar_ids[str(guild_id)] = msg.id
        criando_modo[user_id] = "canal_salvo"
        return

    # Skip name input in specific views
    if current == "get_mode_selected_embed" and message.content.startswith("#"):
        logger.debug("[SKIP] Ignorando mensagem de nome dentro de get_mode_selected_embed.")
        return

    if current == "get_create_embed" and message.content.startswith("#"):
        logger.debug("[SKIP] Ignorando mensagem de nome dentro de get_create_embed.")
        return

    # Initialize guild data
    dados = carregar_modos()
    if guild_id and str(guild_id) not in dados:
        dados[str(guild_id)] = {"modos": {}}
        logger.info(f"Novo registro criado para guilda {guild_id} em 'dados'.")
        
    # Handling mode edition (get_edit_embed)
    current = user_progress.get(guild_id, {}).get(user_id)
    if current == "get_edit_embed" and message.content.startswith("#"):
        nome_modo = message.content[1:].strip()
        modo_id = modo_existe(guild_id, nome_modo)

        logger.debug(f"[EDIT] Usuário {user_id} iniciou tentativa de edição para o modo '{nome_modo}' no servidor {guild_id}.")

        if not modo_id:
            logger.warning(f"[EDIT] Modo '{nome_modo}' não encontrado no servidor {guild_id}. Enviando embed de erro.")
            embed = get_invalid_mode_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            user_progress[guild_id][user_id] = "get_invalid_mode_embed"
            criando_modo[user_id] = "erro_iniciacao_edicao"
            return

        # Backup creation before edition
        modos = carregar_modos()
        modo_antigo = modos.get(str(guild_id), {}).get("modos", {}).get(modo_id, {})
        
        cargos_antigos = modo_antigo.get("roles", [])[:]
        canais_antigos = modo_antigo.get("channels", [])[:]
        nome_antigo = modo_antigo.get("nome", "")
        
        logger.debug(f"[BACKUP] Backup feito ANTES da edição do modo {modo_id}")
        
        if 'backup_data' not in criando_modo:
            criando_modo['backup_data'] = {}
        criando_modo['backup_data'][user_id] = {
            'cargos_antigos': cargos_antigos,
            'canais_antigos': canais_antigos,
            'modo_id': modo_id,
            'nome_antigo': nome_antigo
        }

# Clean and prepare for editing
        dados = carregar_modos()
        if guild_id and str(guild_id) not in dados:
            dados[str(guild_id)] = {"modos": {}}
            logger.info(f"[EDIT] Criada nova estrutura de dados para guilda {guild_id}.")

        if modo_id not in dados[str(guild_id)]["modos"]:
            dados[str(guild_id)]["modos"][modo_id] = {}
            logger.info(f"[EDIT] Estrutura criada para modo {modo_id} em guilda {guild_id}.")

        dados[str(guild_id)]["modos"][modo_id]["em_edicao"] = True

        salvar_modos(dados)
        MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = dados[str(guild_id)]["modos"][modo_id]

        em_edicao[user_id] = True
        modo_atual[user_id] = modo_id
        modo_ids[user_id] = modo_id

        logger.info(f"[EDIT] Usuário {user_id} entrou em modo de edição para '{nome_modo}' (ID: {modo_id}) no servidor {guild_id}.")

        # Send selection embed and setup reactions
        embed = get_mode_selected_embed(nome_modo, idioma)
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("🔙")
        await msg.add_reaction("✅")
        mensagem_voltar_ids[str(guild_id)] = msg.id
        mensagem_avancar_ids[str(guild_id)] = msg.id
        user_progress[guild_id][user_id] = "get_mode_selected_embed"
        criando_modo[user_id] = "iniciando_edicao"

        logger.debug(f"[EDIT] Embed de edição enviado para o modo '{nome_modo}' com reações configuradas.")
        return

    # Delete mode stage
    current = user_progress.get(guild_id, {}).get(user_id)
    if current == "get_delete_mode_embed" and message.content.startswith("#"):
        logger.debug(f"[DELETE DEBUG] Entrando na seção de apagar - Content: {message.content}")
        nome_modo = message.content[1:].strip()
        modo_id = modo_existe(guild_id, nome_modo)
        logger.debug(f"[DELETE] Usuário {user_id} tentando apagar modo '{nome_modo}'")

        if not modo_id:
            logger.warning(f"[DELETE] Modo '{nome_modo}' não encontrado")
            embed = get_delete_error_embed(idioma, nome_modo)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            user_progress[guild_id][user_id] = "get_delete_error_embed"
            return

        # Save ID for confirmation
        modo_ids[user_id] = modo_id
        criando_modo[user_id] = "confirmando_exclusao"

        # Send confirmation embed
        embed = get_delete_confirm_embed(idioma, nome_modo)
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        
        await msg.add_reaction("🔙")
        await msg.add_reaction("✅")
        
        user_progress[guild_id][user_id] = "get_delete_confirm_embed"
        logger.debug(f"[DELETE] Confirmação de exclusão enviada para modo {modo_id}")
        return

    # Name stage for creation or edition
    if message.content.startswith("#"):
        # Extra check for delete flow
        current = user_progress.get(guild_id, {}).get(user_id)
        if current == "get_delete_mode_embed":
            return

        logger.debug(f"[FLOW] Detectado início da etapa de nome. Conteúdo: {message.content}")

        # Skip name messages during creation embed
        if current == "get_create_embed":
            logger.debug("[SKIP] Ignorando mensagem de nome dentro de get_create_embed.")
            return

        # Reset user state
        logger.debug(f"[STATE] Resetando estado do usuário {user_id} na guilda {guild_id}.")
        resetar_estado_usuario(guild_id, user_id)
        
        nome_modo = message.content[1:].strip()
        logger.debug(f"[INPUT] Nome do modo recebido: '{nome_modo}' (len={len(nome_modo)})")

        # Length validation
        if not 2 <= len(nome_modo) <= 15:
            logger.debug(f"[VALIDATION] Nome inválido: '{nome_modo}' (tamanho fora do limite).")
            embed = get_invalid_name_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            user_progress[guild_id][user_id] = "get_invalid_name_embed"
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "nome_invalido"
            push_embed(user_id, "get_create_embed")
            logger.debug(f"[STATE] Usuário {user_id} marcado como 'nome_invalido'. Embed de aviso enviada.")
            return

        # Load data and check edition status
        dados = carregar_modos()
        modo_id = modo_ids.get(user_id)
        
        esta_editando = (
            modo_id and 
            dados.get(str(guild_id), {}).get("modos", {}).get(modo_id, {}).get("em_edicao", False)
        )
        logger.debug(f"[CHECK] modo_id={modo_id}, está_editando={esta_editando}")

        estado_final = None
        embed_final = None

        if esta_editando:
            # Mode edition
            logger.debug(f"[EDIT] Editando modo existente (id={modo_id}) com novo nome: '{nome_modo}'")
            
            dados[str(guild_id)]["modos"][modo_id]["nome"] = nome_modo
            salvar_modos(dados)
            MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = dados[str(guild_id)]["modos"][modo_id]
            
            embed_final = get_name_saved_embed(idioma)
            criando_modo[user_id] = "nome_salvo"
            estado_final = "get_name_saved_embed"
            logger.debug(f"[EDIT] Nome do modo atualizado e salvo no cache.")
        else:
            # Mode creation
            logger.debug(f"[CREATE] Iniciando criação do modo '{nome_modo}'.")
            modo_id_existente = modo_existe(guild_id, nome_modo)
            if modo_id_existente:
                logger.debug(f"[CONFLICT] Modo '{nome_modo}' já existe (id={modo_id_existente}).")
                embed_final = get_name_conflict_embed(idioma, nome_modo)
                criando_modo[user_id] = "nome_conflito"
                estado_final = "get_name_conflict_embed"
            else:
                modo_id = criar_modo(guild_id, user_id, nome_modo)
                modo_ids[user_id] = modo_id
                logger.debug(f"[CREATE] Novo modo criado com id={modo_id}.")

                # Reload and ensure structure
                dados = carregar_modos()
                dados.setdefault(str(guild_id), {}).setdefault("modos", {}).setdefault(modo_id, {})
                dados[str(guild_id)]["modos"][modo_id]["em_edicao"] = True
                salvar_modos(dados)
                logger.debug(f"[DATA] Dados recarregados e estrutura garantida para o modo {modo_id}.")

                # Update cache
                MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = dados[str(guild_id)]["modos"][modo_id]
                logger.debug(f"[CACHE] Modo {modo_id} adicionado ao MODOS_CACHE.")

                embed_final = get_name_saved_embed(idioma)
                criando_modo[user_id] = "nome_salvo"
                estado_final = "get_name_saved_embed"
                logger.debug(f"[CREATE] Criação concluída para o modo '{nome_modo}'.")

        # Update history and send final embed
        push_embed(user_id, "get_create_embed")
        logger.debug(f"[UI] Atualizando histórico e enviando embed final para {user_id}.")
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed_final)
        await msg.add_reaction("🔙")
        
        if estado_final == "get_name_saved_embed":
            await msg.add_reaction("✅")
            logger.debug(f"[STATE] Reação ✅ adicionada para nome salvo")
        else:
            logger.debug(f"[STATE] NÃO adicionando ✅ para {estado_final}")
            
        mensagem_voltar_ids[str(guild_id)] = msg.id
        mensagem_avancar_ids[str(guild_id)] = msg.id
        user_progress.setdefault(guild_id, {})[user_id] = estado_final
        
        logger.debug(f"[STATE] Estado final: user_progress={estado_final}, criando_modo={criando_modo.get(user_id)}")
        return
    
    # Role stage
    if estado == "selecionando_cargo":
        logger.debug(f"[FLOW] Iniciando etapa de seleção de cargo para user={user_id}, guild={guild_id}.")
        
        # Check backup existence
        if 'backup_data' in criando_modo and user_id in criando_modo['backup_data']:
            backup = criando_modo['backup_data'][user_id]
            logger.debug(f"[DEBUG] Backup encontrado na etapa de cargo: cargos_antigos={backup['cargos_antigos']}, canais_antigos={backup['canais_antigos']}")
        else:
            logger.debug(f"[DEBUG] Nenhum backup encontrado para user {user_id}")
        
        roles = []

        # Parse role from message
        if message.role_mentions:
            roles = message.role_mentions
            logger.debug(f"[INPUT] Roles mencionadas diretamente: {[r.name for r in roles]}")
        else:
            m = re.search(r"<@&(\d+)>", message.content)
            if m:
                rid = int(m.group(1))
                role = message.guild.get_role(rid)
                if role:
                    roles = [role]
                    logger.debug(f"[INPUT] Role encontrada por ID: {role.name} (ID={rid})")
            else:
                nome = message.content.strip()
                if nome:
                    role = discord.utils.get(message.guild.roles, name=nome)
                    if role:
                        roles = [role]
                        logger.debug(f"[INPUT] Role encontrada por nome: {role.name}")

        # Invalid role handler
        if not roles:
            logger.debug(f"[VALIDATION] Nenhum cargo válido encontrado para '{message.content}'.")
            embed = get_invalid_role_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            user_progress[guild_id][user_id] = "get_invalid_role_embed"
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "cargo_invalido"
            logger.debug(f"[STATE] usuário {user_id} marcado como 'cargo_invalido'. Embed enviado.")
            return

        # Smart cleanup for old roles during edition
        if em_edicao.get(user_id, False) and modo_ids.get(user_id):
            modo_id = modo_ids[user_id]
            logger.debug(f"[CLEANUP] Modo em edição detectado. Executando limpeza inteligente para modo {modo_id}")
            
            modos = carregar_modos()
            guild_id_str = str(guild_id)
            
            if guild_id_str in modos and modo_id in modos[guild_id_str]["modos"]:
                modo = modos[guild_id_str]["modos"][modo_id]
                
                if modo.get("roles"):
                    cargo_antigo_id = int(modo["roles"][0])
                    cargo_antigo = message.guild.get_role(cargo_antigo_id)
                    
                    if cargo_antigo:
                        # Check bot permissions for role
                        bot_member = message.guild.get_member(bot.user.id)
                        bot_posicao = bot_member.top_role.position
                        cargo_posicao = cargo_antigo.position
                        
                        if cargo_posicao < bot_posicao:
                            if modo.get("channels"):
                                canais_limpos = []
                                erros_limpeza = []
                                
                                for canal_data in modo["channels"]:
                                    try:
                                        canal_id = int(canal_data.id) if hasattr(canal_data, "id") else int(canal_data)
                                        canal = message.guild.get_channel(canal_id)
                                        
                                        if canal:
                                            # Manage role permissions cleanup
                                            bot_permissions = canal.permissions_for(bot_member)
                                            if bot_permissions.manage_roles:
                                                await canal.set_permissions(cargo_antigo, overwrite=None)
                                                canais_limpos.append(canal)
                                                logger.debug(f"[CLEANUP] Cargo antigo {cargo_antigo.name} removido do canal {canal.name}")
                                            else:
                                                erros_limpeza.append(f"Sem permissão para gerenciar canal {canal.name}")
                                                logger.warning(f"[CLEANUP] Bot sem permissão para gerenciar canal {canal.name}")
                                    except Exception as e:
                                        erros_limpeza.append(f"Erro ao limpar canal {canal_id}: {str(e)}")
                                        logger.error(f"[CLEANUP] Falha ao remover cargo antigo de canal {canal_id}: {e}")
                                
                                if canais_limpos:
                                    logger.info(f"[CLEANUP] Limpeza concluída: cargo {cargo_antigo.name} removido de {len(canais_limpos)} canais")
                                
                                if erros_limpeza:
                                    logger.warning(f"[CLEANUP] Erros durante limpeza: {erros_limpeza}")
                            else:
                                logger.debug("[CLEANUP] Nenhum canal definido no modo para limpar")
                        else:
                            logger.warning(f"[CLEANUP] Bot não tem permissão para gerenciar cargo {cargo_antigo.name} (posição muito alta)")
                    else:
                        logger.warning(f"[CLEANUP] Cargo antigo com ID {cargo_antigo_id} não encontrado no servidor")

# Save role data and update cache
        try:
            salvar_roles_modo(guild_id, modo_ids[user_id], roles)
            salvar_modos(carregar_modos())
            logger.debug(f"[SAVE] Cargo(s) {[r.name for r in roles]} salvo(s) para o modo {modo_ids[user_id]}.")
        except Exception as e:
            logger.debug(f"[ERROR] salvar_roles_modo falhou: {e}")
            embed = get_invalid_role_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            user_progress[guild_id][user_id] = "get_invalid_role_embed"
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "cargo_invalido"
            return

        # UI Cleanup
        try:
            await message.delete()
            logger.debug(f"[UI] Mensagem original do usuário deletada.")
        except:
            logger.debug(f"[WARN] Falha ao deletar mensagem do usuário.")

        # Role confirmation and progress update
        role = roles[0]
        embed = get_role_saved_embed(idioma, role.name)
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("🔙")
        await msg.add_reaction("✅")
        user_progress.setdefault(guild_id, {})[user_id] = "get_role_saved_embed"
        criando_modo[user_id] = "cargo_salvo"
        mensagem_voltar_ids[str(guild_id)] = msg.id
        mensagem_avancar_ids[str(guild_id)] = msg.id
        logger.debug(f"[STATE] Cargo '{role.name}' salvo com sucesso. user_progress atualizado para 'get_role_saved_embed'.")
        return

    # Command processing
    await bot.process_commands(message)

# Bot commands
@bot.command(name="setup", aliases=["Setup", "SETUP"])
async def setup(ctx):
    # Setup initialization and state clearing
    logger.debug(f"[CMD] setup chamado por {ctx.author} ({ctx.author.id}) no servidor {ctx.guild.name} ({ctx.guild.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id)
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)
    idioma = obter_idioma(ctx.guild.id)
    embed = get_setup_embed(idioma)
    await enviar_embed(ctx.channel, ctx.author.id, embed)
    logger.debug("[CMD] setup finalizado")

@bot.command(name="criar", aliases=["Criar", "CRIAR", "create", "Create", "CREATE"])
async def criar(ctx):
    # Mode creation initialization
    logger.debug(f"[CMD] criar chamado por {ctx.author} ({ctx.author.id}) no servidor {ctx.guild.name} ({ctx.guild.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id)
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)

    user_id = ctx.author.id
    guild_id = ctx.guild.id

    # Reset edition flags
    if em_edicao.get(user_id):
        em_edicao[user_id] = False
        modo_atual[user_id] = None
        logger.debug(f"[CRIAÇÃO] Flags de edição resetadas para {user_id}")

    modo_ids.pop(user_id, None)
    criando_modo[user_id] = None
    if guild_id in user_progress:
        user_progress[guild_id].pop(user_id, None)

    # Reset unfinished modes in database
    dados = carregar_modos()
    if str(guild_id) in dados:
        for mid, m in dados[str(guild_id)].get("modos", {}).items():
            if m.get("em_edicao") and m.get("criador") == str(user_id):
                m["em_edicao"] = False
                logger.debug(f"[CRIAÇÃO] Reset em_edicao do modo {mid} do usuário {user_id}")
    salvar_modos(dados)

    # UI setup for creation flow
    embed = get_create_embed(ctx.guild)
    msg = await ctx.channel.send(embed=embed)

    if flow["get_create_embed"].get("back"):
        await msg.add_reaction("🔙")
    if flow["get_create_embed"].get("next"):
        await msg.add_reaction("✅")
        user_progress.setdefault(guild_id, {})[user_id] = "get_create_embed"
        logger.debug(f"[CRIAÇÃO] user_progress[{guild_id}][{user_id}] setado para 'get_create_embed'")

    criando_modo[user_id] = "esperando_nome"
    push_embed(user_id, "get_setup_embed")
    logger.debug(f"[CRIAÇÃO] criando_modo[{user_id}] setado para 'esperando_nome'")

@bot.command(name="editar", aliases=["Editar", "EDITAR", "edit", "Edit", "EDIT"])
async def editar(ctx):
    # Mode edition command
    logger.debug(f"[CMD] editar chamado por {ctx.author} ({ctx.author.id}) no servidor {ctx.guild.name} ({ctx.guild.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id)
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)

    user_id = ctx.author.id
    guild_id = ctx.guild.id
    idioma = obter_idioma(guild_id)

    criando_modo[user_id] = None
    embed = get_edit_embed(guild_id, idioma)
    msg = await ctx.channel.send(embed=embed)

    if flow["get_edit_embed"].get("back"):
        await msg.add_reaction("🔙")
    if flow["get_edit_embed"].get("next"):
        await msg.add_reaction("✅")

    user_progress.setdefault(guild_id, {})[user_id] = "get_edit_embed"
    push_embed(user_id, "get_setup_embed")
    logger.debug(f"[EDITAR] user_progress[{guild_id}][{user_id}] setado para 'get_edit_embed'")

@bot.command(name="verificar", aliases=["Verificar", "VERIFICAR", "check", "Check", "CHECK"])
async def verificar(ctx):
    # Check roles command
    logger.debug(f"[CMD] verificar chamado por {ctx.author} ({ctx.author.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id)
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)

    idioma = obter_idioma(ctx.guild.id)
    embed = get_roles_embed(ctx.guild.roles, idioma, ctx.guild)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🔙")

    mensagem_voltar_ids[str(ctx.guild.id)] = msg.id
    user_progress.setdefault(ctx.guild.id, {})[ctx.author.id] = "get_roles_embed"
    push_embed(ctx.author.id, "get_setup_embed")
    logger.debug(f"[VERIFICAR] user_progress[{ctx.guild.id}][{ctx.author.id}] setado para 'get_roles_embed'")

@bot.command(name="funções", aliases=["Funções", "FUNÇÕES", "functions", "Functions", "FUNCTIONS"])
async def funcoes(ctx):
    # Bot functions command
    logger.debug(f"[CMD] funcoes chamado por {ctx.author} ({ctx.author.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id)
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)

    idioma = obter_idioma(ctx.guild.id)
    embed = get_functions_embed(idioma, ctx.guild)
    msg = await ctx.channel.send(embed=embed)

    if flow["get_functions_embed"].get("back"):
        await msg.add_reaction("🔙")
    if flow["get_functions_embed"].get("next"):
        await msg.add_reaction("✅")
        user_progress.setdefault(ctx.guild.id, {})[ctx.author.id] = "get_functions_embed"

    user_progress.setdefault(ctx.guild.id, {})[ctx.author.id] = "get_functions_embed"
    push_embed(ctx.author.id, "get_setup_embed")
    logger.debug(f"[FUNCOES] user_progress[{ctx.guild.id}][{ctx.author.id}] setado para 'get_functions_embed'")

@bot.command(name="sobre", aliases=["Sobre", "SOBRE", "about", "About", "ABOUT"])
async def sobre(ctx):
    # Bot information command
    logger.debug(f"[CMD] sobre chamado por {ctx.author} ({ctx.author.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id)
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)

    idioma = obter_idioma(ctx.guild.id)
    embed = get_about_embed(idioma)
    msg = await ctx.channel.send(embed=embed)

    if flow["get_about_embed"].get("back"):
        await msg.add_reaction("🔙")
    if flow["get_about_embed"].get("next"):
        await msg.add_reaction("✅")
        user_progress.setdefault(ctx.guild.id, {})[ctx.author.id] = "get_about_embed"

    user_progress.setdefault(ctx.guild.id, {})[ctx.author.id] = "get_about_embed"
    push_embed(ctx.author.id, "get_setup_embed")
    logger.debug(f"[SOBRE] user_progress[{ctx.guild.id}][{ctx.author.id}] setado para 'get_about_embed'")

@bot.command(name="idioma", aliases=["Idioma", "IDIOMA", "language", "Language", "LANGUAGE"])
async def idioma(ctx):
    # Language selection command
    logger.debug(f"[CMD] idioma chamado por {ctx.author} ({ctx.author.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id)
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)

    user_id = ctx.author.id
    guild_id = ctx.guild.id
    
    # State reset
    if guild_id in user_progress and user_id in user_progress[guild_id]:
        user_progress[guild_id].pop(user_id, None)
    
    criando_modo.pop(user_id, None)
    modo_ids.pop(user_id, None)
    em_edicao.pop(user_id, None)
    modo_atual.pop(user_id, None)

    idioma_atual = obter_idioma(ctx.guild.id)
    embed = get_language_embed(idioma_atual, ctx.guild)
    msg = await ctx.send(embed=embed)

    await msg.add_reaction("🇺🇸")
    await msg.add_reaction("🇧🇷")

    # Update language message trackers
    mensagem_idioma_id[str(ctx.guild.id)] = msg.id
    resposta_enviada.discard(str(ctx.guild.id))
    logger.debug(f"[IDIOMA] mensagem de idioma enviada no servidor {ctx.guild.id}")

@bot.command(name="log", aliases=["Log", "LOG"])
@commands.has_permissions(manage_guild=True)
async def toggle_log(ctx):
    # Logger toggle command flow
    global logger

    logger.debug(f"[CMD] log chamado por {ctx.author} ({ctx.author.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id)
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)

    # Initialize log confirmation flow
    idioma = obter_idioma(ctx.guild.id)
    embed = get_log_info_embed(idioma)
    msg = await ctx.send(embed=embed)

    # Add flow reactions
    try:
        await msg.add_reaction("🔙")
    except Exception:
        logger.debug("[LOG] Falha ao adicionar reação 🔙.")
    try:
        await msg.add_reaction("✅")
    except Exception:
        logger.debug("[LOG] Falha ao adicionar reação ✅.")

    # Update navigation state
    mensagem_voltar_ids[str(ctx.guild.id)] = msg.id
    mensagem_avancar_ids[str(ctx.guild.id)] = msg.id
    user_progress.setdefault(ctx.guild.id, {})[ctx.author.id] = "get_log_info_embed"
    push_embed(ctx.author.id, "get_setup_embed")
    logger.debug(f"[LOG] Fluxo de confirmação de log iniciado para user={ctx.author.id} em guild={ctx.guild.id}")

@bot.command(name="limpar", aliases=["Limpar", "LIMPAR", "clean", "Clean", "CLEAN"])
async def limpar(ctx, quantidade: int = 50):
    # Message cleanup command
    logger.debug(f"[CMD] limpar chamado por {ctx.author} ({ctx.author.id}) com quantidade={quantidade}")
    try:
        await ctx.message.delete()
    except:
        pass

    quantidade_deletada = await limpar_mensagem_user(ctx.channel, quantidade)
    idioma = obter_idioma(ctx.guild.id)
    embed = get_clean_embed(idioma, quantidade_deletada, ctx.author)
    await ctx.send(embed=embed)

@bot.command(name="apagar", aliases=["Apagar", "APAGAR", "delete", "Delete", "DELETE"])
async def deletar(ctx):
    # Mode deletion command flow
    logger.debug(f"[CMD] deletar (modos) chamado por {ctx.author} ({ctx.author.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id)
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)

    user_id = ctx.author.id
    guild_id = ctx.guild.id
    idioma = obter_idioma(guild_id)
    
    modo_ids.pop(user_id, None)
    criando_modo[user_id] = None
    
    # Filter finished modes only
    modos = carregar_modos().get(str(guild_id), {}).get("modos", {})
    modos_finalizados = {mid: mdata for mid, mdata in modos.items() if mdata.get("finalizado")}
    
    # Handle empty mode list
    if not modos_finalizados:
        if idioma == "pt":
            embed = discord.Embed(
                title="❌ Nenhum Modo Disponível",
                description="Não há modos finalizados para apagar.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="❌ No Modes Available",
                description="There are no finished modes to delete.",
                color=discord.Color.red()
            )
        await ctx.send(embed=embed)
        return
    
    # Start deletion UI
    embed = get_delete_mode_embed(idioma, modos_finalizados)
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction("🔙")
    
    user_progress.setdefault(guild_id, {})[user_id] = "get_delete_mode_embed"
    criando_modo[user_id] = "apagando_modo"
    logger.debug(f"[DELETAR] Fluxo de exclusão iniciado para {user_id}")

@bot.command(name="trocar", aliases=["Trocar", "TROCAR", "switch", "Switch", "SWITCH"])
async def trocar(ctx):
    # Switch mode command flow
    logger.debug(f"[CMD] trocar chamado por {ctx.author} ({ctx.author.id}) no servidor {ctx.guild.name} ({ctx.guild.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id)
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)

    user_id = ctx.author.id
    guild_id = ctx.guild.id
    idioma = obter_idioma(guild_id)
    resetar_estado_usuario(guild_id, user_id)
    
    # Filter finished modes with assigned roles
    modos = carregar_modos().get(str(guild_id), {}).get("modos", {})
    modos_existentes = []
    for modo_id, modo_data in modos.items():
        if modo_data.get("finalizado") and modo_data.get("roles"):
            modos_existentes.append(modo_data["nome"])
    
    # Send switch mode list
    logger.debug(f"[TROCAR] Modos finalizados encontrados: {modos_existentes}")
    embed = get_switch_mode_list_embed(idioma, modos_existentes)
    msg = await ctx.channel.send(embed=embed)
    user_progress.setdefault(guild_id, {})[user_id] = "get_switch_mode_list_embed"
    criando_modo[user_id] = "selecionando_modo_trocar"
    await msg.add_reaction("🔙")
    
    logger.debug(f"[TROCAR] Lista de modos enviada para {user_id} | Modos: {modos_existentes}")

# Bot startup initialization
dbx = get_dropbox_client()

if not dbx:
    logger.critical("Dropbox indisponível, abortando inicialização")
    sys.exit(1)

# Files and state management
bootstrap_data_files(DATA_DIR, CONFIG_PATH)

state_manager = StateManager(dbx)
state_manager.load()
state_manager.state.setdefault("boot_count", 0)
state_manager.state["boot_count"] += 1
state_manager.save()

dropbox_task = None

@bot.event
async def setup_hook():
    # Background tasks setup
    global dropbox_task

    if dropbox_task is None:
        dropbox_task = bot.loop.create_task(run_setup_periodic())
        logger.info("Task Dropbox iniciada")

    bot.loop.create_task(create_periodic_state_save(state_manager))
    logger.info("Tarefa de sync do Dropbox agendada")

# Start bot
bot.run(TOKEN)
