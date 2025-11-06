import re
import discord
from discord.ext import commands
from config import TOKEN, PREFIX, CAMINHO_IDIOMAS
from utils.logger_manager import logger, carregar_config, salvar_config, configurar_logger
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
    finalizar_modos_em_edicao
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
    get_channel_removed_warning_embed
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
        "back": "get_reception_mode_question_embed",
        "next": "get_finish_mode_embed"
    },
    "get_channel_removed_warning_embed": {
        "back": "get_reception_mode_question_embed",
        "next": "get_finish_mode_embed"
    },
    "get_reception_skipped_embed": {
        "back": "get_reception_mode_question_embed",
        "next": "get_finish_mode_embed"
    },
    "get_finish_mode_embed": {
        "back": "get_setup_embed",
        "next": None
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
    "finalizado": "get_finish_mode_embed"
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
}

# ----------------- FUNÇÕES AUXILIARES -----------------
idiomas = carregar_idiomas()
logger.debug("[INIT] Idiomas carregados com sucesso.")

def push_embed(user_id, estado, *args):
    historico_embeds.setdefault(user_id, []).append((estado, args))
    logger.debug(f"[EMBED] push_embed chamado | user_id={user_id}, estado={estado}, args={args}")

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
    try:
        await canal.purge(limit=quantidade, check=check)
        logger.debug(f"[MSG] Mensagens limpas via purge | canal={canal}, autores=({autor1}, {autor2})")
    except Exception as e:
        logger.debug(f"[MSG] Falha no purge ({e}) — usando fallback para deletar manualmente.")
        async for m in canal.history(limit=50):
            if m.author in [autor1, autor2]:
                try:
                    await m.delete()
                    logger.debug(f"[MSG] Mensagem manualmente deletada | autor={m.author}")
                except Exception as e:
                    logger.debug(f"[MSG] Falha ao deletar mensagem manualmente: {e}")

async def enviar_embed(canal, user_id, embed):
    try:
        await canal.send(embed=embed)
        logger.debug(f"[EMBED] Enviado com sucesso | user={user_id}, canal={canal}")
    except Exception as e:
        logger.debug(f"[EMBED] Erro ao enviar embed para user={user_id}, canal={canal}: {e}")

async def go_next(canal, user_id, guild_id, resultado=None):
    logger.debug(f"[FLOW] user_progress atual no início: {user_progress.get(guild_id, {}).get(user_id)}")
    logger.debug(f"[FLOW] go_next iniciado | user={user_id}, guild={guild_id}, resultado={resultado}")

    idioma = obter_idioma(guild_id)
    extra_args = ()

    # ---------- PATCH: tratamento especial se for tupla (ex: assigned/skipped) ----------
    logger.debug("[FLOW] Verificando se resultado é tupla...")
    if isinstance(resultado, tuple):
        logger.debug("[FLOW] Resultado é tupla. Iniciando bloco especial.")
        func_name, *extra_args = resultado
        embed_func = EMBEDS.get(func_name) or globals().get(func_name)
        if not embed_func:
            logger.debug(f"[ERROR] Embed {func_name} não encontrado (tuple path)")
            return
        try:
            logger.debug(f"[FLOW] Gerando embed da tupla: {func_name}")
            embed = embed_func(idioma, *extra_args)
        except Exception as e:
            logger.debug(f"[ERROR] ao gerar embed {func_name}: {e}")
            return

        logger.debug("[FLOW] Obtendo membro do canal...")
        membro = canal.guild.get_member(user_id)
        logger.debug("[FLOW] Limpando mensagens anteriores...")
        await limpar_mensagens(canal, membro, bot.user)
        logger.debug("[FLOW] Enviando embed da tupla...")
        msg = await canal.send(embed=embed)

        if flow.get(func_name, {}).get("back"):
            await msg.add_reaction("🔙")
            logger.debug(f"[FLOW] Reação 🔙 adicionada para {func_name}")
        if flow.get(func_name, {}).get("next"):
            await msg.add_reaction("✅")
            logger.debug(f"[FLOW] Reação ✅ adicionada para {func_name}")

        mensagem_voltar_ids[str(guild_id)] = msg.id
        mensagem_avancar_ids[str(guild_id)] = msg.id
        user_progress.setdefault(guild_id, {})[user_id] = func_name
        logger.debug(f"[FLOW] Tupla {func_name} enviada e user_progress atualizado.")
        
        logger.debug(f"[STATE] user_progress após tupla: {user_progress.get(guild_id, {}).get(user_id)}")
        logger.debug(f"[STATE] criando_modo após tupla: {criando_modo.get(user_id)}")
        
        return
    logger.debug("[FLOW] Resultado não é tupla. Seguindo fluxo normal.")

    # ---------- LÓGICA NORMAL (precisa de current) ----------
    current = user_progress.get(guild_id, {}).get(user_id)
    logger.debug(f"[TRACE] Current embed: {current}")
    if not current:
        logger.debug("[TRACE] Nenhum current encontrado. Encerrando go_next.")
        return

    idioma = obter_idioma(guild_id)
    # ---------- LÓGICA NORMAL ----------
    next_step = flow[current].get("next")
    logger.debug(f"[TRACE] Próximo passo obtido do flow: {next_step}")

    if isinstance(next_step, list):
        if resultado and resultado in next_step:
            next_embed_name = resultado
        else:
            next_embed_name = next_step[0]
    else:
        next_embed_name = next_step

    logger.debug(f"[TRACE] Próximo embed definido: {next_embed_name}")

    if not next_embed_name:
        logger.debug("[TRACE] Nenhum próximo embed definido. Encerrando.")
        return

    embed_func = EMBEDS.get(next_embed_name)
    if not embed_func:
        logger.error(f"Embed {next_embed_name} não encontrado.")
        return

    logger.debug(f"[TRACE] Gerando embed {next_embed_name}...")
    embed = None
    try:
        if next_embed_name == "get_role_select_embed":
            logger.debug("[TRACE] Gerando embed de seleção de cargo...")
            roles = [role for role in canal.guild.roles if role.name != "@everyone"]
            try:
                embed = embed_func(idioma, roles)
            except TypeError:
                try:
                    embed = embed_func(roles, idioma)
                except TypeError:
                    embed = embed_func(idioma)
        elif next_embed_name in ("get_channel_select_embed",):
            logger.debug("[TRACE] Gerando embed de seleção de canal...")
            channels = canal.guild.channels
            try:
                embed = embed_func(channels, idioma)
            except TypeError:
                try:
                    embed = embed_func(idioma, channels)
                except TypeError:
                    embed = embed_func(idioma)
        else:
            embed = embed_func(idioma)
        logger.debug(f"[TRACE] Embed {next_embed_name} gerado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao gerar embed {next_embed_name}: {e}")
        return

    user_progress[guild_id][user_id] = next_embed_name
    push_embed(user_id, next_embed_name, *extra_args)

    logger.debug("[TRACE] Obtendo membro do canal para envio do embed...")
    membro = canal.guild.get_member(user_id)
    logger.debug("[TRACE] Limpando mensagens antigas...")
    await limpar_mensagens(canal, membro, bot.user)
    logger.debug("[TRACE] Enviando novo embed...")
    msg = await canal.send(embed=embed)
    logger.debug(f"[TRACE] Embed {next_embed_name} enviado com sucesso.")

    if flow[next_embed_name].get("back"):
        await msg.add_reaction("🔙")
        logger.debug("[TRACE] Reação 🔙 adicionada.")
    if flow[next_embed_name].get("next"):
        await msg.add_reaction("✅")
        logger.debug("[TRACE] Reação ✅ adicionada.")

    if next_embed_name == "get_reception_mode_question_embed":
        try:
            logger.debug("[TRACE] Adicionando reações de recepção (✅❌)...")
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
        except Exception as e:
            logger.warning(f"Não foi possível adicionar reações de recepção: {e}")
    else:
        if flow[next_embed_name].get("back"):
            await msg.add_reaction("🔙")
        if flow[next_embed_name].get("next"):
            await msg.add_reaction("✅")

    logger.debug(f"[TRACE] Atualizando progresso e estado do usuário (current={current}, next={next_embed_name})...")
    if current == "get_name_saved_embed":
        next_embed_name = "get_role_select_embed"
        criando_modo[user_id] = "selecionando_cargo"
        user_progress.setdefault(guild_id, {})[user_id] = next_embed_name
    elif current == "get_role_saved_embed":
        next_embed_name = "get_channel_select_embed"
        criando_modo[user_id] = "selecionando_canal"
        user_progress.setdefault(guild_id, {})[user_id] = next_embed_name
    elif next_embed_name == "get_name_saved_embed":
        criando_modo[user_id] = "nome_salvo"
        user_progress.setdefault(guild_id, {})[user_id] = next_embed_name
    elif next_embed_name == "get_finish_mode_embed":
        logger.debug("[TRACE] Entrando na etapa de finalização do modo...")
        modos = carregar_modos()
        guild_id_str = str(guild_id)
        modo_id = modo_ids.get(user_id)
        logger.debug(f"[TRACE] modo_id = {modo_id}")

        if modo_id:
            modo_atual_guild = modos.get(guild_id_str, {}).get("modos", {}).get(modo_id)
            if modo_atual_guild:
                logger.debug(f"[TRACE] Modo encontrado: {modo_atual_guild.get('nome', 'Sem nome')}")
                if modo_atual_guild.get("finalizado"):
                    logger.debug("[TRACE] Modo já finalizado. Encerrando.")
                    return
                modo_atual_guild["finalizado"] = True
                modo_atual_guild["em_edicao"] = False
                salvar_modos(modos)
                MODOS_CACHE[guild_id_str]["modos"][modo_id] = modo_atual_guild
                logger.debug("[TRACE] Modo finalizado e salvo com sucesso.")
            else:
                logger.warning(f"Modo {modo_id} não encontrado no servidor — pode ser modo fantasma.")
        else:
            logger.warning(f"Nenhum modo_id registrado para o usuário {user_id}.")

        resetar_estado_usuario(guild_id, user_id)

        criando_modo[user_id] = "finalizado"
        user_progress.setdefault(guild_id, {})[user_id] = next_embed_name

        try:
            logger.debug("[TRACE] Enviando embed final de conclusão...")
            embed = get_finish_mode_embed(idioma)
            membro = canal.guild.get_member(user_id)
            await limpar_mensagens(canal, membro, bot.user)
            msg = await canal.send(embed=embed)
            logger.debug("[TRACE] Embed final enviado com sucesso.")

            user_progress.setdefault(guild_id, {})[user_id] = "finished"
            criando_modo[user_id] = None
            logger.debug("[TRACE] Estado final do usuário resetado com sucesso.")
        except Exception as e:
            logger.error(f"Falha ao enviar embed final de modo: {e}")

    elif next_embed_name == "get_role_select_embed":
        criando_modo[user_id] = "selecionando_cargo"
    elif next_embed_name == "get_channel_select_embed":
        criando_modo[user_id] = "selecionando_canal"

    user_progress.setdefault(guild_id, {})[user_id] = next_embed_name
    logger.debug(f"[TRACE] go_next finalizado com sucesso para user={user_id}, next={next_embed_name}")
# ---------- FUNÇÃO DE VOLTAR ----------
async def go_back(canal, user_id, guild_id):
    logger.debug(f"[TRACE] Iniciando go_back | user={user_id}, guild={guild_id}")

    current = user_progress.get(guild_id, {}).get(user_id)
    logger.debug(f"[TRACE] Current embed: {current}")
    idioma = obter_idioma(guild_id)

    if current == "get_finish_mode_embed":
        logger.debug("[TRACE] Usuário está na tela final, tentando voltar um passo...")
        back_embed = flow[current].get("back")
        logger.debug(f"[TRACE] Back embed encontrado: {back_embed}")

        if not back_embed:
            logger.debug("[TRACE] Nenhum embed anterior encontrado, encerrando go_back.")
            return

        embed_func = EMBEDS.get(back_embed)
        if not embed_func:
            logger.error(f"Embed {back_embed} não encontrado.")
            return

        try:
            logger.debug(f"[TRACE] Gerando embed {back_embed}...")
            embed = embed_func(idioma)
            logger.debug(f"[TRACE] Embed {back_embed} gerado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao gerar embed {back_embed}: {e}")
            return

        membro = canal.guild.get_member(user_id)
        logger.debug("[TRACE] Limpando mensagens anteriores...")
        await limpar_mensagens(canal, membro, bot.user)

        logger.debug("[TRACE] Enviando embed anterior...")
        msg = await canal.send(embed=embed)
        logger.debug(f"[TRACE] Embed {back_embed} enviado com sucesso.")

        if flow[back_embed].get("back"):
            await msg.add_reaction("🔙")
            logger.debug("[TRACE] Reação 🔙 adicionada.")
        if flow[back_embed].get("next"):
            await msg.add_reaction("✅")
            logger.debug("[TRACE] Reação ✅ adicionada.")

        user_progress.setdefault(guild_id, {})[user_id] = back_embed
        logger.debug(f"[TRACE] Progresso atualizado para embed anterior: {back_embed}")
        return
    
    # ----------------- Lógica normal (com histórico) -----------------
    logger.debug(f"[TRACE] Iniciando lógica normal de go_back para user={user_id}, guild={guild_id}")
    
    if not historico_embeds.get(user_id):
        logger.debug("[TRACE] Nenhum histórico de embeds encontrado para o usuário. Encerrando go_back.")
        return

    logger.debug(f"[TRACE] Histórico atual de embeds: {len(historico_embeds[user_id])} itens")

    while historico_embeds[user_id] and historico_embeds[user_id][-1][0] == current:
        logger.debug(f"[TRACE] Removendo embed duplicado do histórico: {historico_embeds[user_id][-1][0]}")
        historico_embeds[user_id].pop()

    last_embed, args = pop_embed(user_id)
    logger.debug(f"[TRACE] Último embed obtido do histórico: {last_embed}")

    if not last_embed:
        logger.debug("[TRACE] Nenhum embed anterior encontrado no histórico. Encerrando go_back.")
        return
    
    # Se for voltar para setup, desativa a edição automaticamente
    if last_embed == "get_setup_embed":
        logger.debug(f"[TRACE] Retornando para setup — resetando estado de edição do usuário {user_id} no servidor {guild_id}.")
        reset_edicao(guild_id, user_id)
        em_edicao[user_id] = False
        modo_atual[user_id] = None
        modo_ids.pop(user_id, None)
        criando_modo[user_id] = None

        limpar_modos_incompletos(guild_id)
        logger.debug("[TRACE] Estado de edição resetado e modos incompletos limpos com sucesso.")

    embed_func = EMBEDS.get(last_embed)
    if not embed_func:
        logger.error(f"[ERROR] Embed {last_embed} não encontrado em EMBEDS.")
        return
    
    # --- PATCH: tratamento especial para get_role_select_embed ---
    if last_embed == "get_role_select_embed":
        logger.debug(f"[TRACE] Retornando para {last_embed} — iniciando geração do embed de seleção de cargo.")
        try:
            roles = [r for r in canal.guild.roles if not r.is_default()]
            logger.debug(f"[TRACE] Total de cargos encontrados: {len(roles)}")
            embed = embed_func(idioma, roles)

            membro = canal.guild.get_member(user_id)
            await limpar_mensagens(canal, membro, bot.user)
            msg = await canal.send(embed=embed)
            logger.debug(f"[TRACE] Embed {last_embed} enviado com sucesso para o usuário {user_id}.")

            if flow[last_embed].get("back"):
                await msg.add_reaction("🔙")
                logger.debug("[TRACE] Reação 🔙 adicionada.")
            if flow[last_embed].get("next"):
                await msg.add_reaction("✅")
                logger.debug("[TRACE] Reação ✅ adicionada.")

            user_progress.setdefault(guild_id, {})[user_id] = last_embed
            logger.debug(f"[TRACE] user_progress atualizado para {last_embed}")
            return

        except Exception as e:
            logger.error(f"[ERROR] falha ao gerar embed {last_embed}: {e}", exc_info=True)
            return
        
    if last_embed == "get_create_embed":
        logger.debug("[TRACE] Tentando gerar embed get_create_embed.")
        try:
            embed = get_create_embed(canal.guild)  # guild atual passada, idioma é lido dentro da função
            logger.debug("[TRACE] Embed get_create_embed gerado com sucesso.")
            return embed
        except Exception as e:
            logger.error(f"[ERROR] falha ao gerar embed get_create_embed: {e}", exc_info=True)
            return

    # --- PATCH: tratamento especial para get_channel_select_embed ---
    if last_embed == "get_channel_select_embed":
        criando_modo[user_id] = "selecionando_canal"  # garante estado correto
        user_progress[guild_id][user_id] = "get_channel_select_embed"

        try:
            embed = embed_func(idioma)  # só passa idioma
        except Exception as e:
            logger.error(f"Falha ao gerar embed get_channel_select_embed: {e}", exc_info=True)
            return

        membro = canal.guild.get_member(user_id)
        await limpar_mensagens(canal, membro, bot.user)
        msg = await canal.send(embed=embed)

        if flow[last_embed].get("back"):
            await msg.add_reaction("🔙")
        if flow[last_embed].get("next"):
            await msg.add_reaction("✅")

        return
    
    # ---------- GERAR E ENVIAR EMBED (LÓGICA CENTRAL DE RETORNO) ----------
    embed = None
    try:
        import inspect
        sig = inspect.signature(embed_func)
        num_params = len(sig.parameters)

        # Normaliza possíveis args vindos do histórico:
        def sanitize_arg(arg, canal):
            # Se for lista, tenta converter itens numéricos para Role/Channel
            if isinstance(arg, (list, tuple)):
                out = []
                for item in arg:
                    s = str(item)
                    if s.isdigit():
                        r = canal.guild.get_role(int(s))
                        if r:
                            out.append(r)
                            continue
                        ch = canal.guild.get_channel(int(s))
                        if ch:
                            out.append(ch)
                            continue
                        out.append(s)
                    else:
                        out.append(s)
                return out
            if isinstance(arg, str) and arg.isdigit():
                r = canal.guild.get_role(int(arg))
                if r:
                    return r
                ch = canal.guild.get_channel(int(arg))
                if ch:
                    return ch
                return arg
            return arg

        sanitized_args = tuple(sanitize_arg(a, canal) for a in args)

        if last_embed in ("get_roles_embed", "get_create_embed"):
            roles = [role for role in canal.guild.roles if not role.is_default()]
            if num_params > 1:
                try:
                    embed = embed_func(idioma, roles)
                except TypeError:
                    embed = embed_func(roles, idioma)
            else:
                embed = embed_func(idioma)

        elif last_embed == "get_channel_select_embed":

            dados = carregar_modos()
            guild_id_str = str(canal.guild.id)

            for modo_id, modo in dados.get(guild_id_str, {}).get("modos", {}).items():
                if modo.get("criador") == str(user_id) and modo.get("em_edicao", False):
                    # limpa os canais antigos
                    salvar_channels_modo(canal.guild.id, modo_id, [])

            # Sincroniza o progresso do usuário
            user_progress.setdefault(canal.guild.id, {})[user_id] = "get_channel_select_embed"

            # Limpa histórico antigo da etapa para que o próximo botão funcione
            if user_id in historico_embeds:
                historico_embeds[user_id] = [
                    (e, a) for e, a in historico_embeds[user_id] if e != "get_channel_select_embed"
                ]

            # Agora gera o embed
            channels = canal.guild.channels
            try:
                embed = embed_func(idioma, channels)
            except TypeError:
                embed = embed_func(channels, idioma)

        else:
            try:
                embed = embed_func(idioma) if num_params == 1 else embed_func(idioma, *sanitized_args)
            except Exception:
                try:
                    embed = embed_func(idioma) if num_params == 1 else embed_func(idioma, *args)
                except Exception as e:
                    logger.error(f"Falha ao gerar embed (fallback) {last_embed}: {e}", exc_info=True)
                    raise

    except Exception as e:
        logger.error(f"Falha ao gerar embed {last_embed}: {e}", exc_info=True)
        return

    membro = canal.guild.get_member(user_id)
    await limpar_mensagens(canal, membro, bot.user)
    msg = await canal.send(embed=embed)

    if flow[last_embed].get("back"):
        await msg.add_reaction("🔙")
    if flow[last_embed].get("next"):
        await msg.add_reaction("✅")

    user_progress.setdefault(guild_id, {})[user_id] = last_embed

# ----------------- EVENTOS -----------------
@bot.event
async def on_ready():
    print(f"Usuário conectado: {bot.user}!")

@bot.event
async def on_guild_join(guild):
    logger.info(f"Bot entrou no servidor: {guild.name} (ID: {guild.id})")

    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            try:
                logger.debug(f"Enviando embed de idioma no canal: {channel.name} ({channel.id})")
                embed = get_language_embed(idioma, guild)
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
    logger.debug(f"Evento on_raw_reaction_add detectado: user={payload.user_id}, emoji={payload.emoji.name}, guild={payload.guild_id}, channel={payload.channel_id}")

    # Ignora reações do próprio bot
    if payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    canal = bot.get_channel(payload.channel_id)
    if not guild or not canal:
        logger.debug(f"[WARN] Guild ou canal não encontrados para o payload {payload.message_id}")
        return

    user_id = payload.user_id
    guild_id = payload.guild_id  # Principal função para a reação de OK funcionar, não mexa. :D
    idioma = obter_idioma(guild_id)
    current = user_progress.get(guild_id, {}).get(user_id)

    logger.debug(f"[TRACE] Reação adicionada por {user_id} em guild {guild_id} | Emoji: {payload.emoji.name} | Current: {current}")

    # -------------------- SELEÇÃO DE IDIOMA --------------------
    if mensagem_idioma_id.get(guild_id) == payload.message_id:
        if payload.emoji.name == "🇧🇷":
            definir_idioma(guild_id, "pt")
            idioma = "pt"
        elif payload.emoji.name == "🇺🇸":
            definir_idioma(guild_id, "en")
            idioma = "en"
        else:
            return

        try:
            msg = await canal.fetch_message(payload.message_id)
            await msg.delete()
        except Exception as e:
            logger.error(f"Não foi possível deletar a mensagem de idioma: {e}", exc_info=True)

        try:
            embed_greeting = get_greeting_embed(idioma)
            await canal.send(embed=embed_greeting)
        except Exception as e:
            logger.error(f"Não foi possível enviar o embed de saudação: {e}", exc_info=True)
        return
    
    # -------------------- VOLTAR --------------------
    if payload.emoji.name == "🔙":
        logger.debug(f"Usuário {user_id} reagiu com 🔙 em guild {guild_id}. Chamando go_back().")
        await go_back(canal, user_id, guild_id)
        return
    
    # -------------------- AVANÇAR --------------------
    elif payload.emoji.name == "✅":
        logger.debug(f"[TRACE] Reação de AVANÇAR detectada | user={user_id} | current={current}")

        if current == "get_mode_selected_embed":
            logger.debug(f"[INFO] Usuário {user_id} entrou no modo de criação de modo (esperando nome)")
            criando_modo[user_id] = "esperando_nome"
            await go_next(canal, user_id, guild_id)
            return

        elif current == "get_reception_mode_question_embed":
            logger.debug(f"[TRACE] Usuário {user_id} confirmou recepção | guild={guild_id}")
            modo_id = modo_ids.get(user_id)
            if not modo_id:
                logger.warning(f"[WARN] Nenhum modo_id encontrado para o usuário {user_id}")
                return

            modos = carregar_modos()
            modo = modos.get(str(guild_id), {}).get("modos", {}).get(modo_id)
            if not modo:
                logger.warning(f"[WARN] Modo {modo_id} não encontrado para guild {guild_id}")
                return

            novo_cargo_id = int(modo["roles"][0]) if modo.get("roles") else None
            cargo_antigo_id, novo_cargo_id = substituir_cargo(modos, guild_id, modo_id, novo_cargo_id)
            logger.debug(f"[TRACE] Cargo antigo: {cargo_antigo_id} | Novo cargo: {novo_cargo_id}")

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

            logger.debug(f"[TRACE] Canais normalizados: {canais_existentes}")

            # Validar canais
            try:
                canais_existentes_no_modo_atual = modo.get("channels", []) or []
                canais_validos, canais_invalidos = validar_canais(guild, canais_existentes, canais_existentes_no_modo_atual)
                logger.debug(f"[TRACE] Validação de canais: válidos={canais_validos}, inválidos={canais_invalidos}")
            except Exception as e:
                logger.exception(f"[ERROR] validar_canais falhou: {e}")
                embed = get_channel_removed_warning_embed(idioma, ["(erro ao validar canais)"])
                await canal.send(embed=embed)
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
                await canal.send(embed=embed)
                return
            if canais_conflitantes:
                logger.debug(f"[WARN] Canais conflitantes: {canais_conflitantes}")
                embed = get_channel_conflict_warning_embed(idioma, canais_conflitantes)
                await canal.send(embed=embed)
                return

            novo_role = guild.get_role(novo_cargo_id) if novo_cargo_id else None

            # Pega canais válidos como objetos
            canais_validos = []
            for cid in raw_canais:
                ch = guild.get_channel(int(cid))
                if ch:
                    canais_validos.append(ch)

            logger.debug(f"[TRACE] Canais válidos obtidos: {[ch.name for ch in canais_validos]}")

            # Atualiza recepção apenas se tiver cargo e canais
            if novo_role and canais_validos:
                try:
                    # Atualiza permissões
                    for ch in canais_validos:
                        await atualizar_permissoes_canal(ch, novo_role, overwrite=em_edicao.get(user_id, False))

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
                    logger.debug(f"[INFO] Recepção atualizada: cargo={novo_role.name}, canais={len(canais_validos)}")

                except Exception as e:
                    logger.exception(f"[ERROR] Falha ao aplicar recepção para {novo_role.name if novo_role else 'N/A'}: {e}")
            else:
                recepcao_anterior = None
                logger.info("[INFO] Nenhum cargo ou canal válido — recepção permanece inalterada")

            # Próximo passo com embed
            if recepcao_anterior:
                old_role_id = modos.get(str(guild_id), {}).get("modos", {}).get(recepcao_anterior, {}).get("roles", [None])[0]
                old_role = guild.get_role(int(old_role_id)) if old_role_id else None
                old_name = old_role.name if old_role else "N/A"
                logger.debug(f"[TRACE] Recepção substituída: {old_name} → {novo_role.name if novo_role else 'N/A'}")
                await go_next(canal, user_id, guild_id, resultado=("get_reception_replaced_embed", old_name, novo_role.name if novo_role else "N/A"))
            else:
                logger.debug(f"[TRACE] Nova recepção atribuída: {novo_role.name if novo_role else 'N/A'}")
                await go_next(canal, user_id, guild_id, resultado=("get_reception_assigned_embed", novo_role.name if novo_role else "N/A"))
            
            # --- PATCH: Marcar modo como finalizado corretamente ---
            try:
                modo = modos[str(guild_id)]["modos"][modo_id]
                if modo.get("finalizado"):
                    logger.debug(f"[SKIP] Modo {modo_id} já estava finalizado — pulando duplicação no ✅.")
                else:
                    modo["finalizado"] = True
                    modo["em_edicao"] = False
                    salvar_modos(modos)
                    MODOS_CACHE[str(guild_id)]["modos"][modo_id] = modo
                    logger.info(f"[INFO] Modo {modo_id} marcado como finalizado com sucesso.")
            except Exception as e:
                logger.exception(f"[WARN] Falha ao marcar modo {modo_id} como finalizado no ✅: {e}")

            # Resetar flag em_edicao
            try:
                modos[str(guild_id)]["modos"][modo_id]["em_edicao"] = False
                salvar_modos(modos)
                MODOS_CACHE[str(guild_id)]["modos"][modo_id] = modos[str(guild_id)]["modos"][modo_id]
                logger.debug(f"[TRACE] Flag 'em_edicao' resetada para o modo {modo_id}")
            except Exception as e:
                logger.warning(f"[WARN] Não foi possível resetar 'em_edicao' para o modo {modo_id}: {e}")

        else:
            await go_next(canal, user_id, guild_id)
            logger.debug(f"[TRACE] Avançando para o próximo passo após reação ✅ para user_id={user_id}")
    # -------------------- AVANÇAR --------------------
    elif payload.emoji.name == "✅":
        if current == "get_mode_selected_embed":
            logger.debug(f"Usuário {user_id} confirmou seleção de modo — aguardando nome.")
            criando_modo[user_id] = "esperando_nome"
            await go_next(canal, user_id, guild_id)
            return

        elif current == "get_reception_mode_question_embed":
            modo_id = modo_ids.get(user_id)
            if not modo_id:
                logger.warning(f"[{guild_id}] Nenhum modo_id encontrado para usuário {user_id}.")
                return

            modos = carregar_modos()
            modo = modos.get(str(guild_id), {}).get("modos", {}).get(modo_id)
            if not modo:
                logger.warning(f"[{guild_id}] Modo {modo_id} não encontrado para o usuário {user_id}.")
                return

            novo_cargo_id = int(modo["roles"][0]) if modo.get("roles") else None
            cargo_antigo_id, novo_cargo_id = substituir_cargo(modos, guild_id, modo_id, novo_cargo_id)
            logger.debug(f"Substituição de cargo concluída: antigo={cargo_antigo_id}, novo={novo_cargo_id}")

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
            logger.debug(f"Canais normalizados para o modo {modo_id}: {canais_existentes}")

            # Validar canais
            try:
                canais_existentes_no_modo_atual = modo.get("channels", []) or []
                canais_validos, canais_invalidos = validar_canais(guild, canais_existentes, canais_existentes_no_modo_atual)
                logger.debug(f"Canais válidos: {canais_validos} | inválidos: {canais_invalidos}")
            except Exception as e:
                logger.error(f"Erro ao validar canais no modo {modo_id}: {e}", exc_info=True)
                embed = get_channel_removed_warning_embed(idioma, ["(erro ao validar canais)"])
                await canal.send(embed=embed)
                return

            canais_removidos, canais_conflitantes = [], []
            for cid in canais_invalidos:
                ch = guild.get_channel(int(cid))
                if ch:
                    canais_conflitantes.append(cid)
                else:
                    canais_removidos.append(cid)

            if canais_removidos:
                logger.info(f"Canais removidos detectados: {canais_removidos}")
                embed = get_channel_removed_warning_embed(idioma, canais_removidos)
                await canal.send(embed=embed)
                return
            if canais_conflitantes:
                logger.info(f"Canais conflitantes detectados: {canais_conflitantes}")
                embed = get_channel_conflict_warning_embed(idioma, canais_conflitantes)
                await canal.send(embed=embed)
                return

            novo_role = guild.get_role(novo_cargo_id) if novo_cargo_id else None

            # Pega canais válidos como objetos
            canais_validos = []
            for cid in raw_canais:
                ch = guild.get_channel(int(cid))
                if ch:
                    canais_validos.append(ch)
            logger.debug(f"Canais válidos resolvidos: {[c.name for c in canais_validos]}")

            # Atualiza recepção apenas se tiver cargo e canais
            if novo_role and canais_validos:
                try:
                    # Atualiza permissões
                    for ch in canais_validos:
                        await atualizar_permissoes_canal(ch, novo_role, overwrite=em_edicao.get(user_id, False))
                    logger.info(f"Permissões atualizadas para cargo '{novo_role.name}' em {len(canais_validos)} canais.")

                    # Marca este modo como recepção e desmarca os demais
                    for mid, mdata in modos[str(guild_id)]["modos"].items():
                        mdata["recepcao"] = False
                    modos[str(guild_id)]["modos"][modo_id]["recepcao"] = True

                    # Salva modos atualizado
                    salvar_modos(modos)
                    MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = modos[str(guild_id)]["modos"][modo_id]
                    logger.info(f"Modo {modo_id} definido como recepção principal no servidor {guild.name}.")

                    # Aplica recepção de fato
                    recepcao_anterior = await atribuir_recepcao(
                        guild,
                        modo_id,
                        canais_validos,
                        novo_role,
                        overwrite=True
                    )
                except Exception as e:
                    logger.error(f"Falha ao aplicar recepção para '{novo_role.name if novo_role else 'N/A'}': {e}", exc_info=True)
            else:
                recepcao_anterior = None
                logger.info("Nenhum cargo definido — recepção permanece inalterada.")

            # Próximo passo com embed
            if recepcao_anterior:
                old_role_id = modos.get(str(guild_id), {}).get("modos", {}).get(recepcao_anterior, {}).get("roles", [None])[0]
                old_role = guild.get_role(int(old_role_id)) if old_role_id else None
                old_name = old_role.name if old_role else "N/A"
                logger.debug(f"Recepção substituída: {old_name} → {novo_role.name if novo_role else 'N/A'}")
                await go_next(canal, user_id, guild_id, resultado=("get_reception_replaced_embed", old_name, novo_role.name if novo_role else "N/A"))
            else:
                logger.debug(f"Nova recepção atribuída: {novo_role.name if novo_role else 'N/A'}")
                await go_next(canal, user_id, guild_id, resultado=("get_reception_assigned_embed", novo_role.name if novo_role else "N/A"))
            
            # --- PATCH: Marcar modo como finalizado corretamente ---
            try:
                modo = modos[str(guild_id)]["modos"][modo_id]
                if modo.get("finalizado"):
                    logger.info(f"[SKIP] Modo {modo_id} já estava finalizado — pulando duplicação no ✅.")
                else:
                    modo["finalizado"] = True
                    modo["em_edicao"] = False
                    salvar_modos(modos)
                    MODOS_CACHE[str(guild_id)]["modos"][modo_id] = modo
                    logger.info(f"[OK] Modo {modo_id} marcado como finalizado com sucesso.")
            except Exception as e:
                logger.warning(f"Falha ao marcar modo {modo_id} como finalizado no ✅: {e}", exc_info=True)

            # --- Limpeza de estado do usuário ---
            resetar_estado_usuario(guild_id, user_id)
            logger.debug(f"Estado do usuário {user_id} resetado em {guild_id}.")

            # Resetar flag em_edicao
            try:
                modos[str(guild_id)]["modos"][modo_id]["em_edicao"] = False
                salvar_modos(modos)
                MODOS_CACHE[str(guild_id)]["modos"][modo_id] = modos[str(guild_id)]["modos"][modo_id]
                logger.debug(f"Flag 'em_edicao' resetada para modo {modo_id}.")
            except Exception as e:
                logger.warning(f"Não foi possível resetar 'em_edicao' para modo {modo_id}: {e}", exc_info=True)

        elif current == "get_finish_mode_embed": 
            # RESET o estado do usuário só aqui, depois que todos os embeds finais foram enviados.
            # Evita travamento ou perda de progresso se chamado antes.
            resetar_estado_usuario(guild_id, user_id)
            logger.debug(f"Estado do usuário {user_id} resetado (etapa final).")
            return
        else:
            await go_next(canal, user_id, guild_id)
            logger.debug(f"Avançando para o próximo passo de {user_id} em {guild_id}.")

    # -------------------- RECEPÇÃO REPLACED/SKIPPED --------------------
    elif current in ("get_reception_replaced_embed", "get_reception_skipped_embed", "get_reception_assigned_embed"):
        logger.debug(f"Recepção ({current}) detectada para usuário {user_id} em {guild_id}. Avançando para o próximo passo...")
        await go_next(canal, user_id, guild_id)
        logger.info(f"Usuário {user_id} avançou após recepção ({current}) em {guild_id}.")
        return
    
    # -------------------- PULAR --------------------
    elif payload.emoji.name == "❌" and current == "get_reception_mode_question_embed":
        logger.debug(f"Reação ❌ detectada — usuário {user_id}, guilda {guild_id}. Iniciando rotina de pular recepção...")
        modo_id = modo_ids.get(user_id)
        if not modo_id:
            logger.warning(f"[SKIP] Nenhum modo_id encontrado para usuário {user_id} em guilda {guild_id}.")
            return

        modos = carregar_modos()
        modo = modos.get(str(guild_id), {}).get("modos", {}).get(modo_id)
        if not modo:
            logger.warning(f"[SKIP] Modo inexistente ({modo_id}) para usuário {user_id} em guilda {guild_id}.")
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
            logger.exception(f"Erro ao validar canais no ❌ (usuário {user_id}, guilda {guild_id}): {e}")
            print(f"[ERROR] validar_canais falhou: {e}")
            embed = get_channel_removed_warning_embed(idioma, ["(erro ao validar canais)"])
            await canal.send(embed=embed)
            return

        canais_removidos, canais_conflitantes = [], []
        for cid in canais_invalidos:
            ch = guild.get_channel(int(cid))
            if ch:
                canais_conflitantes.append(cid)
            else:
                canais_removidos.append(cid)

        if canais_removidos:
            logger.warning(f"Canais removidos detectados no ❌: {canais_removidos}")
            embed = get_channel_removed_warning_embed(idioma, canais_removidos)
            await canal.send(embed=embed)
            return
        if canais_conflitantes:
            logger.warning(f"Canais conflitantes detectados no ❌: {canais_conflitantes}")
            embed = get_channel_conflict_warning_embed(idioma, canais_conflitantes)
            await canal.send(embed=embed)
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
                    await atualizar_permissoes_canal(ch, role, overwrite=True)
                logger.info(f"Permissões atualizadas para cargo '{role.name}' ({role.id}) nos canais válidos: {len(canais_validos)}")
            except Exception as e:
                logger.exception(f"Falha ao atualizar permissões no ❌ (cargo {role.name if role else 'N/A'}) — {e}")
                print(f"[ERROR] Falha ao privar canais no ❌: {e}")

        # Continua o fluxo normal
        role_name = role.name if role else "N/A"
        logger.debug(f"Fluxo de ❌ concluído para usuário {user_id} ({role_name}).")

        # --- PATCH: Finalizar corretamente antes de avançar ---
        try:
            modo = modos[str(guild_id)]["modos"][modo_id]
            if modo.get("finalizado"):
                print(f"[SKIP] Modo {modo_id} já estava finalizado — pulando duplicação no ❌.")
                logger.warning(f"Modo {modo_id} já estava finalizado — duplicação evitada no skip (usuário {user_id}, guilda {guild_id}).")
            else:
                modo["finalizado"] = True
                modo["em_edicao"] = False
                salvar_modos(modos)
                MODOS_CACHE[str(guild_id)]["modos"][modo_id] = modo
                print(f"[INFO] Modo {modo_id} finalizado corretamente antes do skip (❌).")
                logger.info(f"Modo {modo_id} finalizado com sucesso antes de pular (usuário {user_id}, guilda {guild_id}).")
        except Exception as e:
            print(f"[WARN] Falha ao marcar modo {modo_id} como finalizado no skip: {e}")
            logger.exception(f"Falha ao marcar modo {modo_id} como finalizado no skip (usuário {user_id}, guilda {guild_id}): {e}")

        # --- Continua o fluxo normalmente após finalizar ---
        logger.debug(f"Avançando fluxo pós-skip (❌) para usuário {user_id} em guilda {guild_id}, role_name={role_name}.")
        await go_next(canal, user_id, guild_id, resultado=("get_reception_skipped_embed", role_name))
        logger.debug(f"Fluxo de skip (❌) concluído para usuário {user_id}.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    guild_id = message.guild.id if message.guild else None
    idioma = obter_idioma(guild_id) if guild_id else "pt"
    estado = criando_modo.get(user_id)
    current = user_progress.get(guild_id, {}).get(user_id)

    logger.debug(f"Mensagem recebida de {message.author} (ID: {user_id}) no servidor {guild_id or 'DM'} | Estado atual: {estado}, Current: {current}")

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

        if str(guild_id) not in dados:
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
    # -------------------- ETAPA NOME (criação ou edição) --------------------
    if message.content.startswith("#"):
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
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "nome_invalido"
            push_embed(user_id, "get_create_embed")
            logger.debug(f"[STATE] Usuário {user_id} marcado como 'nome_invalido'. Embed de aviso enviada.")
            return

        modo_id = modo_ids.get(user_id)
        esta_editando = (
            modo_id and dados.get(str(guild_id), {}).get("modos", {}).get(modo_id, {}).get("em_edicao", False)
        )
        logger.debug(f"[CHECK] modo_id={modo_id}, está_editando={esta_editando}")

        if esta_editando:
            # -------------------- EDIÇÃO --------------------
            logger.debug(f"[EDIT] Editando modo existente (id={modo_id}) com novo nome: '{nome_modo}'")
            dados[str(guild_id)]["modos"][modo_id]["nome"] = nome_modo
            salvar_modos(dados)
            MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = dados[str(guild_id)]["modos"][modo_id]
            embed = get_name_saved_embed(idioma)
            criando_modo[user_id] = "nome_salvo"
            logger.debug(f"[EDIT] Nome do modo atualizado e salvo no cache.")
        else:
            # -------------------- CRIAÇÃO --------------------
            logger.debug(f"[CREATE] Iniciando criação do modo '{nome_modo}'.")
            modo_id_existente = modo_existe(guild_id, nome_modo)
            if modo_id_existente:
                logger.debug(f"[CONFLICT] Modo '{nome_modo}' já existe (id={modo_id_existente}).")
                embed = get_name_conflict_embed(idioma, nome_modo)
                criando_modo[user_id] = "nome_conflito"
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

                embed = get_name_saved_embed(idioma)
                criando_modo[user_id] = "nome_salvo"
                logger.debug(f"[CREATE] Criação concluída para o modo '{nome_modo}'.")

        # Atualiza histórico e envia embed final
        push_embed(user_id, "get_create_embed")
        logger.debug(f"[UI] Atualizando histórico e enviando embed final para {user_id}.")
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("🔙")
        await msg.add_reaction("✅")
        mensagem_voltar_ids[str(guild_id)] = msg.id
        mensagem_avancar_ids[str(guild_id)] = msg.id
        user_progress.setdefault(guild_id, {})[user_id] = "get_name_saved_embed"
        logger.debug(f"[STATE] user_progress atualizado: user={user_id}, guild={guild_id}, step='get_name_saved_embed'.")
        return
    
    # -------------------- ETAPA CARGO --------------------
    if estado == "selecionando_cargo":
        logger.debug(f"[FLOW] Iniciando etapa de seleção de cargo para user={user_id}, guild={guild_id}.")
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
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "cargo_invalido"
            logger.debug(f"[STATE] usuário {user_id} marcado como 'cargo_invalido'. Embed enviado.")
            return

        try:
            salvar_roles_modo(guild_id, modo_ids[user_id], roles)
            salvar_modos(carregar_modos())
            logger.debug(f"[SAVE] Cargo(s) {[r.name for r in roles]} salvo(s) para o modo {modo_ids[user_id]}.")
        except Exception as e:
            logger.debug(f"[ERROR] salvar_roles_modo falhou: {e}")
            embed = get_invalid_role_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
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
    # -------------------- ETAPA CANAL / ATRIBUIR RECEPÇÃO --------------------
    if estado == "selecionando_canal":
        logger.debug(f"[FLOW] Iniciando etapa de seleção de canal para user={user_id}, guild={guild_id}.")
        channels = list(message.channel_mentions)
        content_lower = message.content.lower()
        logger.debug(f"[INPUT] Canais mencionados: {[ch.name for ch in channels]} | Conteúdo da mensagem: '{message.content}'")

        for ch in message.guild.text_channels + message.guild.voice_channels + message.guild.categories:
            if ch.name.lower() == content_lower:
                channels.append(ch)
                logger.debug(f"[MATCH] Canal encontrado por nome: {ch.name}")

        if not channels:
            logger.debug(f"[VALIDATION] Nenhum canal válido encontrado para '{message.content}'.")
            embed = get_invalid_channel_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "canal_invalido"
            logger.debug(f"[STATE] usuário {user_id} marcado como 'canal_invalido'. Embed enviado.")
            return

        # Validação de canais removidos
        canais_removidos = [str(ch.id) for ch in channels if not message.guild.get_channel(ch.id)]
        if canais_removidos:
            logger.debug(f"[VALIDATION] Canais removidos detectados: {canais_removidos}")
            embed = get_channel_removed_warning_embed(idioma, canais_removidos)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "erro_canal"
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
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "erro_canal"
            return

        # Salva apenas os canais e mantém o modo existente
        salvar_channels_modo(guild_id, modo_ids[user_id], channels)
        modos = carregar_modos()
        MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_ids[user_id]] = modos[str(guild_id)]["modos"][modo_ids[user_id]]
        salvar_modos(modos)
        logger.debug(f"[SAVE] Canais salvos para o modo {modo_ids[user_id]}: {[ch.name for ch in channels]}")

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

    idioma = obter_idioma(ctx.guild.id)
    embed = get_language_embed(idioma, ctx.guild)
    msg = await ctx.send(embed=embed)

    await msg.add_reaction("🇺🇸")
    await msg.add_reaction("🇧🇷")

    mensagem_idioma_id[ctx.guild.id] = msg.id
    resposta_enviada.discard(str(ctx.guild.id))
    logger.debug(f"[IDIOMA] mensagem de idioma enviada no servidor {ctx.guild.id}")

@bot.command(name="limpar", aliases=["Limpar", "LIMPAR", "clean", "Clean", "CLEAN"])
async def limpar(ctx):
    logger.debug(f"[CMD] limpar chamado por {ctx.author} ({ctx.author.id})")
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)

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

    config = carregar_config()
    novo_estado = not config.get("debug_enabled", False)
    config["debug_enabled"] = novo_estado
    salvar_config(config)

    logger = configurar_logger()

    estado = "ativado ✅" if novo_estado else "desativado ❌"
    await ctx.send(f"🔧 Modo de debug {estado}.")
    logger.debug(f"[LOG] debug mode {estado} pelo usuário {ctx.author} ({ctx.author.id})")

# ----------------- RODA O BOT -----------------
bot.run(TOKEN)