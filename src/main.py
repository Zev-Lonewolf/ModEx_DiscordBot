import re
import os
import json
import discord
from utils.drive_sync import sync_file_to_drive
from discord.ext import commands, tasks
from config import TOKEN, PREFIX, CAMINHO_IDIOMAS, CAMINHO_MODOS
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

def resetar_estado_usuario(guild_id, user_id):
    criando_modo.pop(user_id, None)
    modo_ids.pop(user_id, None)
    user_progress.setdefault(guild_id, {}).pop(user_id, None)
    historico_embeds.pop(user_id, None)
    em_edicao.pop(user_id, None)
    modo_atual.pop(user_id, None)
    limpar_modos_usuario(guild_id, user_id)

# ----------------- BOT & INTENTS -----------------
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
MODOS_CACHE = carregar_modos()

@tasks.loop(hours=1)
async def backup_task():
    logger.info("Iniciando rotina de backup completo para o Drive.")
    
    try:
        salvar_modos(MODOS_CACHE) 
        logger.debug("Dados locais salvos com sucesso.")
        
        # Tenta sincronizar cada arquivo crítico com o Drive
        sync_file_to_drive(local_file_path=CAMINHO_MODOS, drive_file_name="modos_bot.json")
        sync_file_to_drive(local_file_path=CAMINHO_IDIOMAS, drive_file_name="idiomas_bot.json")
        sync_file_to_drive(local_file_path=CONFIG_PATH, drive_file_name="config_debug.json")
        
        logger.info("Rotina de backup finalizada. Arquivos atualizados no Google Drive.")

    except Exception as e:
        logger.error(f"Erro fatal na rotina de backup/sincronização: {e}", exc_info=True)

@backup_task.before_loop
async def before_backup():
    logger.debug("Aguardando o bot ligar para iniciar o loop de backup.")
    await bot.wait_until_ready()

# ----------------- VARIÁVEIS GLOBAIS -----------------
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

# ----------------- FLUXO DE EMBEDS -----------------
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

# ----------------- MAPEAMENTO ESTADO ↔ EMBED -----------------
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

# ----------------- DICIONÁRIO DE EMBEDS -----------------
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

# ----------------- FUNÇÕES AUXILIARES -----------------
# Esta linha foi removida porque já é carregada no módulo idiomas
logger.debug("[INIT] Módulo de idiomas inicializado")

def push_embed(user_id, estado, *args):
    historico_embeds.setdefault(user_id, []).append((estado, args))
    logger.debug(f"[EMBED] push_embed chamado | user_id={user_id}, estado={estado}, args={args}")

def inicializar_estado_usuario(guild_id, user_id):
    if guild_id not in user_progress:
        user_progress[guild_id] = {}
    
    user_progress[guild_id][user_id] = "get_greeting_embed"
    
    # Limpa qualquer estado anterior residual
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
        return not msg.pinned  # Não deleta mensagens fixadas
    
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

# ---------- FUNÇÃO DE AVANÇAR ----------
async def go_next(canal, user_id, guild_id, resultado=None):
    logger.debug(f"[FLOW] go_next iniciado | user={user_id}, guild={guild_id}, resultado={resultado}")
    logger.debug(f"[FLOW] Estado atual: {user_progress.get(guild_id, {}).get(user_id)}")

    # Garante que o usuário/servidor tem estado inicializado
    if guild_id not in user_progress:
        user_progress[guild_id] = {}
    
    if user_id not in user_progress[guild_id]:
        user_progress[guild_id][user_id] = "get_greeting_embed"
        logger.debug(f"[FLOW] Estado inicializado para user={user_id}")

    idioma = obter_idioma(guild_id)
    extra_args = ()

    # ---------- TRATAMENTO ESPECIAL PARA TUPLAS ----------
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

        # Limpar e enviar mensagem
        membro = canal.guild.get_member(user_id)
        await limpar_mensagens(canal, membro, bot.user)
        msg = await canal.send(embed=embed)

        # Adicionar reações baseadas no flow
        flow_config = flow.get(func_name, {})
        if flow_config.get("back"):
            await msg.add_reaction("🔙")
            logger.debug(f"[FLOW] Reação 🔙 adicionada para {func_name}")
        if flow_config.get("next"):
            await msg.add_reaction("✅")
            logger.debug(f"[FLOW] Reação ✅ adicionada para {func_name}")

        # Atualizar estados
        mensagem_voltar_ids[str(guild_id)] = msg.id
        mensagem_avancar_ids[str(guild_id)] = msg.id
        user_progress.setdefault(guild_id, {})[user_id] = func_name
        
        logger.debug(f"[FLOW] Tupla {func_name} processada com sucesso")
        return

    # ---------- LÓGICA NORMAL ----------
    current = user_progress.get(guild_id, {}).get(user_id)
    if not current:
        logger.debug("[FLOW] Nenhum estado atual encontrado")
        return

    logger.debug(f"[FLOW] Estado atual: {current}")
    next_step = flow[current].get("next")
    logger.debug(f"[FLOW] Próximo passo do flow: {next_step}")

    # Determinar próximo embed
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

    # Gerar embed
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

    # Atualizar estados
    user_progress[guild_id][user_id] = next_embed_name
    push_embed(user_id, next_embed_name, *extra_args)

    # Limpar e enviar mensagem
    membro = canal.guild.get_member(user_id)
    await limpar_mensagens(canal, membro, bot.user)
    msg = await canal.send(embed=embed)
    logger.debug(f"[FLOW] Embed {next_embed_name} enviado")

    # Lógica de reações mais específica
    flow_config = flow.get(next_embed_name, {})
    
    # Identificar corretamente os embeds de warning
    if next_embed_name in ["get_channel_conflict_warning_embed", "get_channel_removed_warning_embed"]:
        # Estes embeds só devem ter a reação de voltar
        await msg.add_reaction("🔙")
        logger.debug(f"[FLOW] Reação 🔙 adicionada para {next_embed_name} (warning - SEM ✅)")
    
    elif next_embed_name in ["get_name_conflict_embed", "get_invalid_name_embed"]:
        await msg.add_reaction("🔙")
        logger.debug(f"[FLOW] Reação 🔙 adicionada para {next_embed_name} (conflito/inválido - SEM ✅)")

    elif next_embed_name in ["get_delete_success_embed", "get_delete_error_embed"]:
        await msg.add_reaction("🔙")
        logger.debug(f"[FLOW] Reação 🔙 adicionada para {next_embed_name}")
    
    # Recepção tem reações especiais
    elif next_embed_name == "get_reception_mode_question_embed":
        try:
            await msg.add_reaction("🔙")
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            logger.debug(f"[FLOW] Reações 🔙✅❌ adicionadas para recepção")
        except Exception as e:
            logger.warning(f"[FLOW] Não foi possível adicionar reações de recepção: {e}")
    
    # Para outros embeds, seguir o flow normalmente
    else:
        if flow_config.get("back"):
            await msg.add_reaction("🔙")
            logger.debug(f"[FLOW] Reação 🔙 adicionada para {next_embed_name}")
        if flow_config.get("next"):
            await msg.add_reaction("✅")
            logger.debug(f"[FLOW] Reação ✅ adicionada para {next_embed_name}")

    # Atualizar estados específicos
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
        
        # Adicionar reação de voltar para o embed final
        await msg.add_reaction("🔙")
        
        user_progress.setdefault(guild_id, {})[user_id] = "get_finish_mode_embed"
        criando_modo[user_id] = None
        logger.debug(f"[FLOW] Estado final resetado para user={user_id}")
    except Exception as e:
        logger.error(f"[FLOW] Falha ao enviar embed final: {e}")

# ---------- FUNÇÃO DE VOLTAR ----------
async def go_back(canal, user_id, guild_id):
    logger.debug(f"[FLOW] go_back iniciado | user={user_id}, guild={guild_id}")

    current = user_progress.get(guild_id, {}).get(user_id)
    if not current:
        logger.debug("[FLOW] Nenhum estado atual encontrado para voltar")
        return

    logger.debug(f"[FLOW] Estado atual: {current}")
    idioma = obter_idioma(guild_id)

    # Determinar embed anterior
    back_embed = flow[current].get("back")
    logger.debug(f"[FLOW] Embed anterior do flow: {back_embed}")

    if not back_embed:
        logger.debug("[FLOW] Nenhum embed anterior definido")
        return

    # Tratamento especial para exclusão
    if back_embed == "get_delete_mode_embed":
        criando_modo[user_id] = "apagando_modo"
        logger.debug("[DELETE] Retornando para lista de modos para apagar")

    embed_func = EMBEDS.get(back_embed)
    if not embed_func:
        logger.error(f"[FLOW] Embed {back_embed} não encontrado")
        return

    # Gerar embed anterior
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
            # Adicionar parâmetro modos_existentes
            modos = carregar_modos().get(str(guild_id), {}).get("modos", {})
            embed = embed_func(idioma, modos)
        else:
            embed = embed_func(idioma)
        
        logger.debug(f"[FLOW] Embed {back_embed} gerado com sucesso")
    except Exception as e:
        logger.error(f"[FLOW] Erro ao gerar embed {back_embed}: {e}")
        return

    # Limpar e enviar mensagem
    membro = canal.guild.get_member(user_id)
    await limpar_mensagens(canal, membro, bot.user)
    msg = await canal.send(embed=embed)
    logger.debug(f"[FLOW] Embed {back_embed} enviado")

    # Adicionar reações APENAS se definidas no flow
    flow_config = flow.get(back_embed, {})

    if back_embed == "get_delete_mode_embed":
        await msg.add_reaction("🔙")
        logger.debug(f"[FLOW] Reação 🔙 adicionada para {back_embed} (exclusão)")
    else:
        # Para outros embeds, seguir o flow normalmente
        if flow_config.get("back"):
            await msg.add_reaction("🔙")
            logger.debug(f"[FLOW] Reação 🔙 adicionada para {back_embed}")
        if flow_config.get("next"):
            await msg.add_reaction("✅")
            logger.debug(f"[FLOW] Reação ✅ adicionada para {back_embed}")

    # Atualizar estados
    user_progress.setdefault(guild_id, {})[user_id] = back_embed
    
    # Atualizar criando_modo baseado no embed
    estado_correspondente = embed_to_estado.get(back_embed)
    if estado_correspondente:
        criando_modo[user_id] = estado_correspondente
        logger.debug(f"[FLOW] criando_modo atualizado para: {estado_correspondente}")

    # Limpar histórico duplicado
    if user_id in historico_embeds:
        historico_embeds[user_id] = [
            (e, a) for e, a in historico_embeds[user_id] 
            if e != back_embed and e != current
        ]

    # Adicionar ao histórico
    push_embed(user_id, back_embed)

    # Tratamentos especiais
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
    try:
        logger.debug(f"[DELETE] Iniciando apagamento completo do modo {modo_id} no servidor {guild_id}")
        
        modos = carregar_modos()
        guild_id_str = str(guild_id)
        
        if guild_id_str not in modos or modo_id not in modos[guild_id_str]["modos"]:
            logger.warning(f"[DELETE] Modo {modo_id} não encontrado no servidor {guild_id}")
            return False

        modo = modos[guild_id_str]["modos"][modo_id]
        modo_nome = modo.get("nome", "Desconhecido")
        
        # Obter a guild
        guild = bot.get_guild(guild_id)
        if not guild:
            logger.error(f"[DELETE] Guild {guild_id} não encontrada")
            return False

        # Resetar permissões dos canais antes de apagar o modo
        canais_para_resetar = modo.get("channels", [])
        cargo_id = modo.get("roles", [None])[0] if modo.get("roles") else None
        cargo = guild.get_role(int(cargo_id)) if cargo_id else None
        
        logger.debug(f"[DELETE] Resetando {len(canais_para_resetar)} canais do modo '{modo_nome}'")
        
        canais_resetados = 0
        erros_reset = []
        
        for canal_data in canais_para_resetar:
            try:
                canal_id = int(canal_data.id) if hasattr(canal_data, "id") else int(canal_data)
                canal = guild.get_channel(canal_id)
                
                if canal:
                    # Resetar permissões do canal
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

        # Agora apaga o modo usando a função existente
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
    try:
        # Remover permissões específicas do cargo do modo, se existir
        if cargo:
            try:
                await canal.set_permissions(cargo, overwrite=None)
                logger.debug(f"[DELETE] Permissões do cargo {cargo.name} removidas do canal {canal.name}")
            except Exception as e:
                logger.warning(f"[DELETE] Não foi possível remover permissões do cargo {cargo.name}: {e}")

        # Para um reset mais completo, definir permissões básicas para @everyone
        overwrites = {
            canal.guild.default_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                connect=True,
                speak=True
            )
        }
        
        # Aplicar as novas permissões
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

# ----------------- EVENTOS -----------------
@bot.event
async def on_ready():
    try:
        configurar_logger()
        carregar_config() 
    except Exception as e:
        print(f"ERRO CRÍTICO na inicialização do Logger/Config: {e}") 

    print(f"Usuário conectado: {bot.user}!")
    verificar_arquivo_idiomas()
    logger.info(f'Usuário conectado: {bot.user}! | Prefix usado: {PREFIX}')

    if not backup_task.is_running():
        try:
            backup_task.start()
            logger.info("Tarefa de backup iniciada com sucesso a cada 2 minutos (Teste).")
        except Exception as e:
            logger.error(f"Falha ao iniciar a backup_task: {e}", exc_info=True)

@bot.event
async def on_guild_join(guild):
    logger.info(f"Bot entrou no servidor: {guild.name} (ID: {guild.id})")

    # garante que o servidor tem uma entrada no sistema de idiomas
    obter_idioma(guild.id)
    
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            try:
                logger.debug(f"Enviando embed de idioma no canal: {channel.name} ({channel.id})")
                
                # Usa inglês como padrão inicial para a mensagem de idioma
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
    logger.debug(f"[EVENT] on_raw_reaction_add: user={payload.user_id}, emoji={payload.emoji.name}, guild={payload.guild_id}, channel={payload.channel_id}")

    # Ignora reações do próprio bot
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

    # --- TRATAMENTO ESPECIAL: confirmação do LOG ---
    if current == "get_log_info_embed" and payload.emoji.name == "✅":
        logger.debug(f"[LOG] Avançando de info para confirm | user={user_id}")

        # Limpeza básica antes de avançar
        finalizar_modos_em_edicao(guild_id, user_id)
        limpar_modos_usuario(guild_id, user_id)
        limpar_modos_incompletos(guild_id)

        # Tenta apagar a mensagem anterior (onde estava o embed de info)
        try:
            msg_antiga = await canal.fetch_message(payload.message_id)
            await msg_antiga.delete()
            logger.debug(f"[LOG] Mensagem anterior apagada antes de enviar o embed de confirmação")
        except Exception as e:
            logger.warning(f"[LOG] Não foi possível apagar a mensagem anterior: {e}")

        # Carrega config atual e envia embed mostrando o estado real do log
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

    # --- CONFIRMAÇÃO DO ESTADO DE LOG ---
    if current == "get_log_confirm_embed":
        member = guild.get_member(user_id)
        if not member or not member.guild_permissions.manage_guild:
            logger.warning(f"[LOG] Usuário {user_id} sem permissão para alterar logs em guild {guild_id}")
            return

        # Ativar logs
        if payload.emoji.name == "✅":
            try:
                config = carregar_config()
                config["debug_enabled"] = True
                config["debug_logs"] = True  # sincroniza
                salvar_config(config)
                configurar_logger()
                logger.info(f"[LOG] Debug mode ATIVADO via fluxo pelo usuário {user_id} no servidor {guild_id}")
            except Exception as e:
                logger.exception(f"[LOG] Falha ao ativar debug via fluxo: {e}")

            await go_next(canal, user_id, guild_id, resultado="get_log_activated_embed")
            return

        # Desativar logs
        if payload.emoji.name == "❌":
            try:
                config = carregar_config()
                config["debug_enabled"] = False
                config["debug_logs"] = False  # sincroniza
                salvar_config(config)
                configurar_logger()
                logger.info(f"[LOG] Debug mode DESATIVADO via fluxo pelo usuário {user_id} no servidor {guild_id}")
            except Exception as e:
                logger.exception(f"[LOG] Falha ao desativar debug via fluxo: {e}")

            await go_next(canal, user_id, guild_id, resultado="get_log_deactivated_embed")
            return

    # -------------------- SELEÇÃO DE IDIOMA --------------------
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
            # Remove a reação do usuário
            msg = await canal.fetch_message(payload.message_id)
            await msg.remove_reaction(payload.emoji, payload.member)
            logger.debug(f"[IDIOMA] Reação removida da mensagem")
        except Exception as e:
            logger.debug(f"[IDIOMA] Não foi possível remover reação: {e}")

        try:
            # Deleta a mensagem de idioma
            await msg.delete()
            logger.debug(f"[IDIOMA] Mensagem de idioma deletada")
            
            # INICIALIZA O ESTADO DO USUÁRIO
            if guild_id not in user_progress:
                user_progress[guild_id] = {}
            user_progress[guild_id][user_id] = "get_greeting_embed"
            
            # Envia o embed de greeting
            embed_greeting = get_greeting_embed(idioma)
            msg_greeting = await canal.send(embed=embed_greeting)
            
            # Adiciona reação para avançar
            await msg_greeting.add_reaction("✅")
            
            # Atualiza IDs para navegação
            mensagem_avancar_ids[str(guild_id)] = msg_greeting.id
            
            logger.debug(f"[IDIOMA] Embed de greeting enviado com sucesso")
            
        except Exception as e:
            logger.error(f"[IDIOMA] Erro no processamento pós-seleção: {e}", exc_info=True)
        return
    
    # -------------------- VOLTAR --------------------
    if payload.emoji.name == "🔙":
        logger.debug(f"[NAVEGAÇÃO] Usuário {user_id} reagiu com 🔙 em guild {guild_id}")
        
        # --- VOLTAR NA CONFIRMAÇÃO DE EXCLUSÃO ---
        if current == "get_delete_confirm_embed":
            logger.debug(f"[DELETE] Usuário {user_id} voltou da confirmação para lista de modos")
            modo_ids.pop(user_id, None)
            criando_modo[user_id] = "apagando_modo"
            await go_back(canal, user_id, guild_id)
            return
        
        await go_back(canal, user_id, guild_id)
        return

    # -------------------- TROCA DE MODO - FLOW SIMPLES --------------------
    if payload.emoji.name == "🔙" and current in ["get_switch_success_embed", "get_switch_error_embed", "get_switch_not_found_embed"]:
        logger.debug(f"[FLOW] Reação 🔙 detectada para {current} - seguindo flow")
        await go_back(canal, user_id, guild_id)
        return

    # -------------------- AVANÇAR --------------------
    elif payload.emoji.name == "✅":
        logger.debug(f"[NAVEGAÇÃO] Reação de AVANÇAR detectada | user={user_id} | current={current}")

        if current == "get_mode_selected_embed":
            logger.debug(f"[CRIAÇÃO] Usuário {user_id} entrou no modo de criação de modo (esperando nome)")
            criando_modo[user_id] = "esperando_nome"
            await go_next(canal, user_id, guild_id)
            return
        
    # -------------------- CONFIRMAÇÃO DE EXCLUSÃO --------------------
    if current == "get_delete_confirm_embed":
        modo_id = modo_ids.get(user_id)
        
        if payload.emoji.name == "✅":
            # Confirmar exclusão
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
            
            # Limpa estado
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

            # Normalizar canais
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

            # Validar canais
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

            # Pega canais válidos como objetos
            canais_validos = []
            for cid in raw_canais:
                ch = guild.get_channel(int(cid))
                if ch:
                    canais_validos.append(ch)

            logger.debug(f"[RECEPÇÃO] Canais válidos obtidos: {[ch.name for ch in canais_validos]}")

            recepcao_anterior = None
            
            # Atualiza recepção apenas se tiver cargo e canais
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

                    # Marca este modo como recepção e desmarca os demais
                    for mid, mdata in modos[str(guild_id)]["modos"].items():
                        mdata["recepcao"] = False
                    modos[str(guild_id)]["modos"][modo_id]["recepcao"] = True

                    # Salva modos atualizado
                    salvar_modos(modos)
                    MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = modos[str(guild_id)]["modos"][modo_id]

                    # Aplica recepção de fato
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

            # Próximo passo com embed
            if recepcao_anterior:
                old_role_id = modos.get(str(guild_id), {}).get("modos", {}).get(recepcao_anterior, {}).get("roles", [None])[0]
                old_role = guild.get_role(int(old_role_id)) if old_role_id else None
                old_name = old_role.name if old_role else "N/A"
                logger.debug(f"[RECEPÇÃO] Recepção substituída: {old_name} → {novo_role.name if novo_role else 'N/A'}")
                await go_next(canal, user_id, guild_id, resultado=("get_reception_replaced_embed", old_name, novo_role.name if novo_role else "N/A"))
            else:
                logger.debug(f"[RECEPÇÃO] Nova recepção atribuída: {novo_role.name if novo_role else 'N/A'}")
                await go_next(canal, user_id, guild_id, resultado=("get_reception_assigned_embed", novo_role.name if novo_role else "N/A"))
            
            # Marcar modo como finalizado corretamente
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

                    # Limpar backup
                    if 'backup_data' in criando_modo and user_id in criando_modo['backup_data']:
                        del criando_modo['backup_data'][user_id]
                        logger.debug(f"[BACKUP] Backup limpo para usuário {user_id}")
                        
            except Exception as e:
                logger.exception(f"[WARN] Falha ao marcar modo {modo_id} como finalizado: {e}")

            # Resetar flag em_edicao
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
    
    # -------------------- AVANÇAR (continuação) --------------------
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

            # Normalizar canais
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

            # Validar canais
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

            # Pega canais válidos como objetos
            canais_validos = []
            for cid in raw_canais:
                ch = guild.get_channel(int(cid))
                if ch:
                    canais_validos.append(ch)
            logger.debug(f"[RECEPÇÃO] Canais válidos resolvidos: {[c.name for c in canais_validos]}")

            recepcao_anterior = None
            
            # Atualiza recepção apenas se tiver cargo e canais
            if novo_role and canais_validos:
                try:
                    # Atualiza permissões
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

                    # Marca este modo como recepção e desmarca os demais
                    for mid, mdata in modos[str(guild_id)]["modos"].items():
                        mdata["recepcao"] = False
                    modos[str(guild_id)]["modos"][modo_id]["recepcao"] = True

                    # Salva modos atualizado
                    salvar_modos(modos)
                    MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = modos[str(guild_id)]["modos"][modo_id]
                    logger.info(f"[RECEPÇÃO] Modo {modo_id} definido como recepção principal no servidor {guild.name}")

                    # Aplica recepção de fato
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

            # Próximo passo com embed
            if recepcao_anterior:
                old_role_id = modos.get(str(guild_id), {}).get("modos", {}).get(recepcao_anterior, {}).get("roles", [None])[0]
                old_role = guild.get_role(int(old_role_id)) if old_role_id else None
                old_name = old_role.name if old_role else "N/A"
                logger.debug(f"[RECEPÇÃO] Recepção substituída: {old_name} → {novo_role.name if novo_role else 'N/A'}")
                await go_next(canal, user_id, guild_id, resultado=("get_reception_replaced_embed", old_name, novo_role.name if novo_role else "N/A"))
            else:
                logger.debug(f"[RECEPÇÃO] Nova recepção atribuída: {novo_role.name if novo_role else 'N/A'}")
                await go_next(canal, user_id, guild_id, resultado=("get_reception_assigned_embed", novo_role.name if novo_role else "N/A"))
            
            # Marcar modo como finalizado corretamente
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

            # Limpeza de estado do usuário
            resetar_estado_usuario(guild_id, user_id)
            logger.debug(f"[ESTADO] Estado do usuário {user_id} resetado em {guild_id}")

            # Resetar flag em_edicao
            try:
                modos[str(guild_id)]["modos"][modo_id]["em_edicao"] = False
                salvar_modos(modos)
                MODOS_CACHE[str(guild_id)]["modos"][modo_id] = modos[str(guild_id)]["modos"][modo_id]
                logger.debug(f"[CRIAÇÃO] Flag 'em_edicao' resetada para modo {modo_id}")
            except Exception as e:
                logger.warning(f"[WARN] Não foi possível resetar 'em_edicao' para modo {modo_id}: {e}", exc_info=True)

        elif current == "get_finish_mode_embed": 
            # RESET o estado do usuário só aqui, depois que todos os embeds finais foram enviados
            resetar_estado_usuario(guild_id, user_id)
            logger.debug(f"[ESTADO] Estado do usuário {user_id} resetado (etapa final)")
            return
        else:
            await go_next(canal, user_id, guild_id)
            logger.debug(f"[NAVEGAÇÃO] Avançando para o próximo passo de {user_id} em {guild_id}")

    # -------------------- RECEPÇÃO REPLACED/SKIPPED --------------------
    elif current in ("get_reception_replaced_embed", "get_reception_skipped_embed", "get_reception_assigned_embed"):
        logger.debug(f"[RECEPÇÃO] Recepção ({current}) detectada para usuário {user_id} em {guild_id}. Avançando para o próximo passo")
        await go_next(canal, user_id, guild_id)
        logger.info(f"[RECEPÇÃO] Usuário {user_id} avançou após recepção ({current}) em {guild_id}")
        return
    
    # -------------------- PULAR --------------------
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

        raw_canais = modo.get("channels", [])  # IDs do modo
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

        # Corrigido: definir variável que faltava
        canais_existentes_no_modo_atual = modo.get("channels", []) or []

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

        # Transformar IDs em objetos Channel
        canais_validos = []
        for cid in raw_canais:
            ch = guild.get_channel(int(cid))
            if ch:  # só adiciona canais que existem
                canais_validos.append(ch)

        # Atualiza permissões do cargo
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

        # Continua o fluxo normal
        role_name = role.name if role else "N/A"
        logger.debug(f"[RECEPÇÃO] Fluxo de ❌ concluído para usuário {user_id} ({role_name})")

        # Finalizar corretamente antes de avançar
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

        # Continua o fluxo normalmente após finalizar
        logger.debug(f"[RECEPÇÃO] Avançando fluxo pós-skip (❌) para usuário {user_id} em guilda {guild_id}, role_name={role_name}")
        await go_next(canal, user_id, guild_id, resultado=("get_reception_skipped_embed", role_name))
        logger.debug(f"[RECEPÇÃO] Fluxo de skip (❌) concluído para usuário {user_id}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    guild_id = message.guild.id if message.guild else None
    
    # SE NÃO É COMANDO E NÃO ESTÁ NO FLUXO ATIVO, IGNORA
    if not message.content.startswith(PREFIX) and user_id not in criando_modo:
        logger.debug(f"[SKIP] Mensagem normal ignorada: {message.content[:50]}...")
        return

    idioma = obter_idioma(guild_id) if guild_id else "pt"
    estado = criando_modo.get(user_id)
    current = user_progress.get(guild_id, {}).get(user_id)
    logger.debug(f"[DEBUG] on_message - User: {user_id}, Current: {current}, Content: {message.content}, Estado: {criando_modo.get(user_id)}")
    logger.debug(f"Mensagem recebida de {message.author} (ID: {user_id}) no servidor {guild_id or 'DM'} | Estado atual: {estado}, Current: {current}")

    # --- VERIFICAÇÃO PRIORITÁRIA: TROCAR MODO ---
    # Esta verificação deve vir ANTES das outras para evitar conflitos
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
            # Define o estado para a tela de "modo não encontrado"
            if guild_id not in user_progress:
                user_progress[guild_id] = {}
            user_progress[guild_id][user_id] = "get_switch_not_found_embed"
            return

        # Aplica o modo a todos os membros
        sucesso, resultado = await aplicar_modo_servidor(message.guild, modo_id, idioma, bot)
        
        if sucesso:
            embed = get_switch_success_embed(idioma, nome_modo)
            # Define o estado para a tela de sucesso
            estado_resultado = "get_switch_success_embed"
        else:
            logger.error(f"[TROCAR] Falha ao aplicar modo {nome_modo}: {resultado}")
            embed = get_switch_error_embed(idioma, nome_modo)
            # Define o estado para a tela de erro
            estado_resultado = "get_switch_error_embed"

        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("🔙")
        
        # Define o estado apropriado baseado no resultado
        if guild_id not in user_progress:
            user_progress[guild_id] = {}
        user_progress[guild_id][user_id] = estado_resultado
        return

    # --- VERIFICAÇÃO PRIORITÁRIA: ETAPA DE SELEÇÃO DE CANAL ---
    if estado == "selecionando_canal":
        logger.debug(f"[CANAL] Processando seleção de canal para user={user_id}")
        
        # Se a mensagem começa com #, tratar como tentativa de nome de canal
        if message.content.startswith("#"):
            nome_canal = message.content[1:].strip()
            logger.debug(f"[CANAL] Tentativa de nome de canal com #: '{nome_canal}'")
            
            # Buscar canal por nome (sem o #)
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
                
                # Garantir que volte para seleção de canal
                push_embed(user_id, "get_channel_select_embed")
                return
        else:
            # Processar menções de canal ou outros formatos
            channels = list(message.channel_mentions)
            content_lower = message.content.lower()

            # Buscar canais por nome (para mensagens sem #)
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
                
                # Garantir que volte para seleção de canal
                push_embed(user_id, "get_channel_select_embed")
                return

        # Validação de canais removidos
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
            
            # Garantir que volte para seleção de canal
            push_embed(user_id, "get_channel_select_embed")
            return

        # Validação de conflito
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
            
            # Garantir que volte para seleção de canal
            push_embed(user_id, "get_channel_select_embed")
            return

        # Se chegou aqui, canais são válidos
        salvar_channels_modo(guild_id, modo_ids[user_id], channels)
        modos = carregar_modos()
        MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_ids[user_id]] = modos[str(guild_id)]["modos"][modo_ids[user_id]]
        salvar_modos(modos)
        logger.debug(f"[CANAL] Canais salvos: {[ch.name for ch in channels]}")

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
        logger.debug(f"[STATE] Canais do usuário {user_id} salvos com sucesso. user_progress atualizado para 'get_channel_saved_embed'.")
        return

    # --- NOVA VERIFICAÇÃO: Ignorar mensagens com # no get_mode_selected_embed ---
    if current == "get_mode_selected_embed" and message.content.startswith("#"):
        logger.debug("[SKIP] Ignorando mensagem de nome dentro de get_mode_selected_embed.")
        return

    # --- VERIFICAÇÃO EXISTENTE: Ignorar mensagens com # no get_create_embed ---
    if current == "get_create_embed" and message.content.startswith("#"):
        logger.debug("[SKIP] Ignorando mensagem de nome dentro de get_create_embed.")
        return

    dados = carregar_modos()
    if guild_id and str(guild_id) not in dados:
        dados[str(guild_id)] = {"modos": {}}
        logger.info(f"Novo registro criado para guilda {guild_id} em 'dados'.")
        
    # -------------------- ETAPA EDIÇÃO (get_edit_embed) --------------------
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

        # FAZER BACKUP ANTES DE QUALQUER OUTRA OPERAÇÃO
        modos = carregar_modos()
        modo_antigo = modos.get(str(guild_id), {}).get("modos", {}).get(modo_id, {})
        
        # Backup dos dados ANTIGOS antes de limpar
        cargos_antigos = modo_antigo.get("roles", [])[:]  # Faz uma cópia
        canais_antigos = modo_antigo.get("channels", [])[:]  # Faz uma cópia
        nome_antigo = modo_antigo.get("nome", "")
        
        logger.debug(f"[BACKUP] Backup feito ANTES da edição:")
        logger.debug(f"[BACKUP] - Modo ID: {modo_id}")
        logger.debug(f"[BACKUP] - Nome antigo: {nome_antigo}") 
        logger.debug(f"[BACKUP] - Cargos antigos: {cargos_antigos}")
        logger.debug(f"[BACKUP] - Canais antigos: {canais_antigos}")
        
        # Salva o backup no estado do usuário
        if 'backup_data' not in criando_modo:
            criando_modo['backup_data'] = {}
        criando_modo['backup_data'][user_id] = {
            'cargos_antigos': cargos_antigos,
            'canais_antigos': canais_antigos,
            'modo_id': modo_id,
            'nome_antigo': nome_antigo
        }

        # limpar e preparar para a edição
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

    # -------------------- ETAPA APAGAR MODO --------------------
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

        # Salva o modo_id para confirmação
        modo_ids[user_id] = modo_id
        criando_modo[user_id] = "confirmando_exclusao"

        # Envia embed de confirmação
        embed = get_delete_confirm_embed(idioma, nome_modo)
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        
        await msg.add_reaction("🔙")
        await msg.add_reaction("✅")
        
        user_progress[guild_id][user_id] = "get_delete_confirm_embed"
        logger.debug(f"[DELETE] Confirmação de exclusão enviada para modo {modo_id}")
        return

    # -------------------- ETAPA NOME (criação ou edição) --------------------
    if message.content.startswith("#"):
        # VERIFICAÇÃO EXTRA: Se está no fluxo de apagar, NÃO processa como criação
        current = user_progress.get(guild_id, {}).get(user_id)
        if current == "get_delete_mode_embed":
            logger.debug("[SKIP] Mensagem # ignorada - usuário está no fluxo de apagar.")
            return

        logger.debug(f"[FLOW] Detectado início da etapa de nome. Conteúdo: {message.content}")

        # Ignora mensagens de nome dentro do get_create_embed
        if current == "get_create_embed":
            logger.debug("[SKIP] Ignorando mensagem de nome dentro de get_create_embed.")
            return

        logger.debug(f"[STATE] Resetando estado do usuário {user_id} na guilda {guild_id}.")
        resetar_estado_usuario(guild_id, user_id)
        
        nome_modo = message.content[1:].strip()
        logger.debug(f"[INPUT] Nome do modo recebido: '{nome_modo}' (len={len(nome_modo)})")

        # Validação de tamanho
        if not 2 <= len(nome_modo) <= 15:
            logger.debug(f"[VALIDATION] Nome inválido: '{nome_modo}' (tamanho fora do limite).")
            embed = get_invalid_name_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            user_progress[guild_id][user_id] = "get_invalid_name_embed"  # ATUALIZA ESTADO
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "nome_invalido"
            push_embed(user_id, "get_create_embed")
            logger.debug(f"[STATE] Usuário {user_id} marcado como 'nome_invalido'. Embed de aviso enviada.")
            return

        # Carregar dados ANTES de verificar edição
        dados = carregar_modos()
        modo_id = modo_ids.get(user_id)
        
        # Verificar se está editando usando o backup_data
        esta_editando = (
            modo_id and 
            dados.get(str(guild_id), {}).get("modos", {}).get(modo_id, {}).get("em_edicao", False)
        )
        logger.debug(f"[CHECK] modo_id={modo_id}, está_editando={esta_editando}")

        # Variável para controlar o estado final
        estado_final = None
        embed_final = None

        if esta_editando:
            # -------------------- EDIÇÃO --------------------
            logger.debug(f"[EDIT] Editando modo existente (id={modo_id}) com novo nome: '{nome_modo}'")
            
            # MANTER os dados antigos do backup, só atualizar o nome
            dados[str(guild_id)]["modos"][modo_id]["nome"] = nome_modo
            salvar_modos(dados)
            MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = dados[str(guild_id)]["modos"][modo_id]
            
            embed_final = get_name_saved_embed(idioma)
            criando_modo[user_id] = "nome_salvo"
            estado_final = "get_name_saved_embed"
            logger.debug(f"[EDIT] Nome do modo atualizado e salvo no cache.")
        else:
            # -------------------- CRIAÇÃO --------------------
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

                # Recarrega dados e garante estrutura
                dados = carregar_modos()
                dados.setdefault(str(guild_id), {}).setdefault("modos", {}).setdefault(modo_id, {})
                dados[str(guild_id)]["modos"][modo_id]["em_edicao"] = True
                salvar_modos(dados)
                logger.debug(f"[DATA] Dados recarregados e estrutura garantida para o modo {modo_id}.")

                # Atualiza cache
                MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = dados[str(guild_id)]["modos"][modo_id]
                logger.debug(f"[CACHE] Modo {modo_id} adicionado ao MODOS_CACHE.")

                embed_final = get_name_saved_embed(idioma)
                criando_modo[user_id] = "nome_salvo"
                estado_final = "get_name_saved_embed"
                logger.debug(f"[CREATE] Criação concluída para o modo '{nome_modo}'.")

        # Atualiza histórico e envia embed final
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
        
        # Usar o estado_final correto
        user_progress.setdefault(guild_id, {})[user_id] = estado_final
        
        logger.debug(f"[STATE] Estado final: user_progress={estado_final}, criando_modo={criando_modo.get(user_id)}")
        return
    
    # -------------------- ETAPA CARGO --------------------
    if estado == "selecionando_cargo":
        logger.debug(f"[FLOW] Iniciando etapa de seleção de cargo para user={user_id}, guild={guild_id}.")
        
        # DEBUG: Verificar se temos backup
        if 'backup_data' in criando_modo and user_id in criando_modo['backup_data']:
            backup = criando_modo['backup_data'][user_id]
            logger.debug(f"[DEBUG] Backup encontrado na etapa de cargo: cargos_antigos={backup['cargos_antigos']}, canais_antigos={backup['canais_antigos']}")
        else:
            logger.debug(f"[DEBUG] Nenhum backup encontrado para user {user_id}")
        
        roles = []

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

        if not roles:
            logger.debug(f"[VALIDATION] Nenhum cargo válido encontrado para '{message.content}'.")
            embed = get_invalid_role_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            user_progress[guild_id][user_id] = "get_invalid_role_embed"  # ATUALIZA ESTADO
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "cargo_invalido"
            logger.debug(f"[STATE] usuário {user_id} marcado como 'cargo_invalido'. Embed enviado.")
            return

        # --- NOVA FUNCIONALIDADE: Limpeza inteligente de cargos antigos durante EDIÇÃO ---
        if em_edicao.get(user_id, False) and modo_ids.get(user_id):
            modo_id = modo_ids[user_id]
            logger.debug(f"[CLEANUP] Modo em edição detectado. Executando limpeza inteligente para modo {modo_id}")
            
            # Carrega dados do modo atual
            modos = carregar_modos()
            guild_id_str = str(guild_id)
            
            if guild_id_str in modos and modo_id in modos[guild_id_str]["modos"]:
                modo = modos[guild_id_str]["modos"][modo_id]
                
                # Verifica se tem cargo antigo definido
                if modo.get("roles"):
                    cargo_antigo_id = int(modo["roles"][0])
                    cargo_antigo = message.guild.get_role(cargo_antigo_id)
                    
                    if cargo_antigo:
                        # Verifica se o bot pode gerenciar este cargo
                        bot_member = message.guild.get_member(bot.user.id)
                        bot_posicao = bot_member.top_role.position
                        cargo_posicao = cargo_antigo.position
                        
                        if cargo_posicao < bot_posicao:
                            # Bot tem permissão para gerenciar este cargo
                            if modo.get("channels"):
                                canais_limpos = []
                                erros_limpeza = []
                                
                                for canal_data in modo["channels"]:
                                    try:
                                        canal_id = int(canal_data.id) if hasattr(canal_data, "id") else int(canal_data)
                                        canal = message.guild.get_channel(canal_id)
                                        
                                        if canal:
                                            # Verifica se o bot tem permissão de gerenciar canais
                                            bot_permissions = canal.permissions_for(bot_member)
                                            if bot_permissions.manage_roles:
                                                # Remove as permissões do cargo antigo
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

        try:
            salvar_roles_modo(guild_id, modo_ids[user_id], roles)
            salvar_modos(carregar_modos())
            logger.debug(f"[SAVE] Cargo(s) {[r.name for r in roles]} salvo(s) para o modo {modo_ids[user_id]}.")
        except Exception as e:
            logger.debug(f"[ERROR] salvar_roles_modo falhou: {e}")
            embed = get_invalid_role_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            user_progress[guild_id][user_id] = "get_invalid_role_embed"  # ATUALIZA ESTADO
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "cargo_invalido"
            return

        try:
            await message.delete()
            logger.debug(f"[UI] Mensagem original do usuário deletada.")
        except:
            logger.debug(f"[WARN] Falha ao deletar mensagem do usuário.")

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

    # ----------------- CHAMADA DOS COMANDOS -----------------
    await bot.process_commands(message) #Não remova, se não os comandos não serão chamados.

# ----------------- COMANDOS -----------------
@bot.command(name="setup", aliases=["Setup", "SETUP"])
async def setup(ctx):
    logger.debug(f"[CMD] setup chamado por {ctx.author} ({ctx.author.id}) no servidor {ctx.guild.name} ({ctx.guild.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id) #Não inverta a ordem de finalização e limpeza!
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)
    idioma = obter_idioma(ctx.guild.id)
    embed = get_setup_embed(idioma)
    await enviar_embed(ctx.channel, ctx.author.id, embed)
    logger.debug("[CMD] setup finalizado")

@bot.command(name="criar", aliases=["Criar", "CRIAR", "create", "Create", "CREATE"])
async def criar(ctx):
    logger.debug(f"[CMD] criar chamado por {ctx.author} ({ctx.author.id}) no servidor {ctx.guild.name} ({ctx.guild.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id) #Não inverta a ordem de finalização e limpeza!
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)

    user_id = ctx.author.id
    guild_id = ctx.guild.id

    # Reseta flags de edição
    if em_edicao.get(user_id):
        em_edicao[user_id] = False
        modo_atual[user_id] = None
        logger.debug(f"[CRIAÇÃO] Flags de edição resetadas para {user_id}")

    modo_ids.pop(user_id, None)
    criando_modo[user_id] = None
    if guild_id in user_progress:
        user_progress[guild_id].pop(user_id, None)

    # Garante que todos os modos antigos em edição sejam resetados
    dados = carregar_modos()
    if str(guild_id) in dados:
        for mid, m in dados[str(guild_id)].get("modos", {}).items():
            if m.get("em_edicao") and m.get("criador") == str(user_id):
                m["em_edicao"] = False
                logger.debug(f"[CRIAÇÃO] Reset em_edicao do modo {mid} do usuário {user_id}")
    salvar_modos(dados)

    embed = get_create_embed(ctx.guild)  # só passa o guild
    msg = await ctx.channel.send(embed=embed)

    # Reações de navegação
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
    logger.debug(f"[CMD] editar chamado por {ctx.author} ({ctx.author.id}) no servidor {ctx.guild.name} ({ctx.guild.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id) #Não inverta a ordem de finalização e limpeza!
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
    logger.debug(f"[CMD] verificar chamado por {ctx.author} ({ctx.author.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id) #Não inverta a ordem de finalização e limpeza!
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
    logger.debug(f"[CMD] funcoes chamado por {ctx.author} ({ctx.author.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id) #Não inverta a ordem de finalização e limpeza!
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
    logger.debug(f"[CMD] sobre chamado por {ctx.author} ({ctx.author.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id) #Não inverta a ordem de finalização e limpeza!
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
    logger.debug(f"[CMD] idioma chamado por {ctx.author} ({ctx.author.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id)  # Não inverta a ordem de finalização e limpeza!
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)

    user_id = ctx.author.id
    guild_id = ctx.guild.id
    
    # Reseta o estado atual do usuário
    if guild_id in user_progress and user_id in user_progress[guild_id]:
        user_progress[guild_id].pop(user_id, None)
    
    # Limpa qualquer estado de criação/edição
    criando_modo.pop(user_id, None)
    modo_ids.pop(user_id, None)
    em_edicao.pop(user_id, None)
    modo_atual.pop(user_id, None)

    idioma_atual = obter_idioma(ctx.guild.id)
    embed = get_language_embed(idioma_atual, ctx.guild)
    msg = await ctx.send(embed=embed)

    await msg.add_reaction("🇺🇸")
    await msg.add_reaction("🇧🇷")

    # Atualiza a mensagem de idioma corretamente
    mensagem_idioma_id[str(ctx.guild.id)] = msg.id
    resposta_enviada.discard(str(ctx.guild.id))
    logger.debug(f"[IDIOMA] mensagem de idioma enviada no servidor {ctx.guild.id}")

@bot.command(name="log", aliases=["Log", "LOG"])
@commands.has_permissions(manage_guild=True)
async def toggle_log(ctx):
    global logger

    logger.debug(f"[CMD] log chamado por {ctx.author} ({ctx.author.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id) #Não inverta a ordem de finalização e limpeza!
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)

    # Em vez de alternar imediatamente, inicia o fluxo de confirmação via embeds
    idioma = obter_idioma(ctx.guild.id)
    embed = get_log_info_embed(idioma)
    msg = await ctx.send(embed=embed)

    # Adiciona reações: voltar, confirmar (ativar), negar (desativar)
    try:
        await msg.add_reaction("🔙")
    except Exception:
        logger.debug("[LOG] Falha ao adicionar reação 🔙 (pode ser permissão).")
    try:
        await msg.add_reaction("✅")
    except Exception:
        logger.debug("[LOG] Falha ao adicionar reação ✅ (pode ser permissão).")

    # Atualiza estados para iniciar fluxo
    mensagem_voltar_ids[str(ctx.guild.id)] = msg.id
    mensagem_avancar_ids[str(ctx.guild.id)] = msg.id
    user_progress.setdefault(ctx.guild.id, {})[ctx.author.id] = "get_log_info_embed"
    push_embed(ctx.author.id, "get_setup_embed")
    logger.debug(f"[LOG] Fluxo de confirmação de log iniciado para user={ctx.author.id} em guild={ctx.guild.id}")

@bot.command(name="limpar", aliases=["Limpar", "LIMPAR", "clean", "Clean", "CLEAN"])
async def limpar(ctx, quantidade: int = 50):
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
    logger.debug(f"[CMD] deletar (modos) chamado por {ctx.author} ({ctx.author.id})")
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    finalizar_modos_em_edicao(ctx.guild.id, ctx.author.id)
    limpar_modos_usuario(ctx.guild.id, ctx.author.id)
    limpar_modos_incompletos(ctx.guild.id)

    user_id = ctx.author.id
    guild_id = ctx.guild.id
    idioma = obter_idioma(guild_id)
    
    # Limpa estados anteriores
    modo_ids.pop(user_id, None)
    criando_modo[user_id] = None
    
    # Envia o embed para apagar modos
    modos = carregar_modos().get(str(guild_id), {}).get("modos", {})
    
    # Filtra apenas modos finalizados (evita apagar modos em edição)
    modos_finalizados = {}
    for modo_id, modo_data in modos.items():
        if modo_data.get("finalizado"):
            modos_finalizados[modo_id] = modo_data
    
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
    
    embed = get_delete_mode_embed(idioma, modos_finalizados)
    msg = await ctx.channel.send(embed=embed)
    
    # Adiciona reações
    await msg.add_reaction("🔙")
    
    # Atualiza estados
    user_progress.setdefault(guild_id, {})[user_id] = "get_delete_mode_embed"
    criando_modo[user_id] = "apagando_modo"
    logger.debug(f"[DELETAR] Fluxo de exclusão iniciado para {user_id}")

@bot.command(name="trocar", aliases=["Trocar", "TROCAR", "switch", "Switch", "SWITCH"])
async def trocar(ctx):
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
    
    modos = carregar_modos().get(str(guild_id), {}).get("modos", {})
    modos_existentes = []
    for modo_id, modo_data in modos.items():
        if modo_data.get("finalizado") and modo_data.get("roles"):
            modos_existentes.append(modo_data["nome"])
    
    logger.debug(f"[TROCAR] Modos finalizados encontrados: {modos_existentes}")
    embed = get_switch_mode_list_embed(idioma, modos_existentes)
    msg = await ctx.channel.send(embed=embed)
    user_progress.setdefault(guild_id, {})[user_id] = "get_switch_mode_list_embed"
    criando_modo[user_id] = "selecionando_modo_trocar"
    await msg.add_reaction("🔙")
    
    logger.debug(f"[TROCAR] Lista de modos enviada para {user_id} | Modos: {modos_existentes}")
# ----------------- RODA O BOT -----------------
bot.run(TOKEN)
