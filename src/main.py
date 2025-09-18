import re
import json
import discord
from discord.ext import commands
from config import TOKEN, PREFIX, CAMINHO_IDIOMAS
from utils.modos import (
    criar_modo,
    modo_existe,
    salvar_modos,
    salvar_roles_modo,
    carregar_modos,
    salvar_channels_modo,
    atribuir_recepcao,
    reset_edicao
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
    get_channel_reset_warning_embed
)

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
            "get_channel_reset_warning_embed"
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
    "get_channel_reset_warning_embed": {
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
    "get_reception_mode_question_embed": get_reception_mode_question_embed,
    "get_reception_assigned_embed": get_reception_assigned_embed,
    "get_reception_replaced_embed": get_reception_replaced_embed,
    "get_reception_skipped_embed": get_reception_skipped_embed,
    "get_finish_mode_embed": get_finish_mode_embed,
    "get_channel_reset_warning_embed": get_channel_reset_warning_embed
}

# ----------------- FUNÇÕES AUXILIARES -----------------
def carregar_idiomas():
    try:
        with open(CAMINHO_IDIOMAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def salvar_idiomas(dados):
    with open(CAMINHO_IDIOMAS, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4)

idiomas = carregar_idiomas()

def obter_idioma(guild_id):
    guild_id = str(guild_id)
    if guild_id not in idiomas:
        idiomas[guild_id] = "en"
        salvar_idiomas(idiomas)
    return idiomas[guild_id]

def definir_idioma(guild_id, idioma):
    idiomas[str(guild_id)] = idioma
    salvar_idiomas(idiomas)

def push_embed(user_id, estado, *args):
    historico_embeds.setdefault(user_id, []).append((estado, args))

def pop_embed(user_id):
    if historico_embeds.get(user_id):
        return historico_embeds[user_id].pop()
    return None, ()

async def limpar_mensagens(canal, autor1, autor2, quantidade=50):
    def check(msg):
        return msg.author in [autor1, autor2]
    try:
        await canal.purge(limit=quantidade, check=check)
    except:
        async for m in canal.history(limit=50):
            if m.author in [autor1, autor2]:
                try: await m.delete()
                except: pass

async def enviar_embed(canal, user_id, embed):
    try:
        await canal.send(embed=embed)
    except Exception as e:
        print(f"Erro ao enviar embed: {e}")

async def go_next(canal, user_id, guild_id, resultado=None):
    current = user_progress.get(guild_id, {}).get(user_id)
    if not current:
        return

    idioma = obter_idioma(guild_id)
    extra_args = () 

    # ---------- SE RESULTADO FOR TUPLA (EX: assigned/skipped) ----------
    if isinstance(resultado, tuple):
        func_name, *extra_args = resultado
        embed_func = EMBEDS.get(func_name) or globals().get(func_name)
        if not embed_func:
            print(f"[ERROR] Embed {func_name} não encontrado")
            return
        try:
            embed = embed_func(idioma, *extra_args)
        except Exception as e:
            print(f"[ERROR] ao gerar embed {func_name}: {e}")
            return
        membro = canal.guild.get_member(user_id)
        await limpar_mensagens(canal, membro, bot.user)
        msg = await canal.send(embed=embed)
        if flow.get(func_name, {}).get("back"):
            await msg.add_reaction("🔙")
        if flow.get(func_name, {}).get("next"):
            await msg.add_reaction("✅")
        mensagem_voltar_ids[str(guild_id)] = msg.id
        mensagem_avancar_ids[str(guild_id)] = msg.id
        user_progress.setdefault(guild_id, {})[user_id] = func_name
        return

    # ---------- LÓGICA NORMAL ----------
    next_step = flow[current].get("next")

    if isinstance(next_step, list):
        if resultado and resultado in next_step:
            next_embed_name = resultado
        else:
            next_embed_name = next_step[0]
    else:
        next_embed_name = next_step

    if not next_embed_name:
        return

    embed_func = EMBEDS.get(next_embed_name)
    if not embed_func:
        print(f"[ERROR] Embed {next_embed_name} não encontrado")
        return

    embed = None
    try:
        if next_embed_name in ("get_roles_embed", "get_create_embed", "get_role_select_embed"):
            roles = [role for role in canal.guild.roles if not role.is_default()]
            try:
                embed = embed_func(roles, idioma)
            except TypeError:
                try:
                    embed = embed_func(roles, idioma)
                except TypeError:
                    embed = embed_func(idioma)
        elif next_embed_name in ("get_channel_select_embed",):
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
    except Exception as e:
        print(f"[ERROR] ao gerar embed {next_embed_name}: {e}")
        return

    push_embed(user_id, next_embed_name, *extra_args, current)

    membro = canal.guild.get_member(user_id)
    await limpar_mensagens(canal, membro, bot.user)
    msg = await canal.send(embed=embed)

    if flow[next_embed_name].get("back"):
        await msg.add_reaction("🔙")
    if flow[next_embed_name].get("next"):
        await msg.add_reaction("✅")

    if next_embed_name == "get_reception_mode_question_embed":
        try:
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
        except Exception as e:
            print(f"[WARN] Não foi possível adicionar reações de recepção: {e}")

    if current == "get_name_saved_embed":
        next_embed_name = "get_role_select_embed"
        criando_modo[user_id] = "selecionando_cargo"
    elif current == "get_role_saved_embed":
        next_embed_name = "get_channel_select_embed"
        criando_modo[user_id] = "selecionando_canal"
    elif next_embed_name == "get_name_saved_embed":
        criando_modo[user_id] = "nome_salvo"
    elif next_embed_name == "get_finish_mode_embed":
        criando_modo[user_id] = "finalizado"
    elif next_embed_name == "get_role_select_embed":
        criando_modo[user_id] = "selecionando_cargo"
    elif next_embed_name == "get_channel_select_embed":
        criando_modo[user_id] = "selecionando_canal"

    user_progress.setdefault(guild_id, {})[user_id] = next_embed_name

async def go_back(canal, user_id, guild_id):
    current = user_progress.get(guild_id, {}).get(user_id)
    idioma = obter_idioma(guild_id)

    if current == "get_finish_mode_embed":
        back_embed = flow[current].get("back")
        if not back_embed:
            return

        embed_func = EMBEDS.get(back_embed)
        if not embed_func:
            print(f"[ERROR] Embed {back_embed} não encontrado")
            return

        try:
            embed = embed_func(idioma)
        except Exception as e:
            print(f"[ERROR] ao gerar embed {back_embed}: {e}")
            return

        membro = canal.guild.get_member(user_id)
        await limpar_mensagens(canal, membro, bot.user)
        msg = await canal.send(embed=embed)

        if flow[back_embed].get("back"):
            await msg.add_reaction("🔙")
        if flow[back_embed].get("next"):
            await msg.add_reaction("✅")

        user_progress.setdefault(guild_id, {})[user_id] = back_embed
        return

    # ----------------- Lógica normal (com histórico) -----------------
    if not historico_embeds.get(user_id):
        return

    while historico_embeds[user_id] and historico_embeds[user_id][-1][0] == current:
        historico_embeds[user_id].pop()

    last_embed, args = pop_embed(user_id)
    if not last_embed:
        return

    # Se for voltar para setup, desativa a edição automaticamente
    if last_embed == "get_setup_embed":
        reset_edicao(guild_id, user_id)
        em_edicao[user_id] = False
        modo_atual[user_id] = None
        modo_ids.pop(user_id, None)
        criando_modo[user_id] = None

    embed_func = EMBEDS.get(last_embed)
    if not embed_func:
        print(f"[ERROR] Embed {last_embed} não encontrado")
        return

    embed = None
    try:
        import inspect
        sig = inspect.signature(embed_func)
        num_params = len(sig.parameters)

        if last_embed in ("get_roles_embed", "get_create_embed"):
            roles = [role for role in canal.guild.roles if not role.is_default()]
            embed = embed_func(roles, idioma) if num_params > 1 else embed_func(idioma)
        elif last_embed == "get_channel_select_embed":
            channels = canal.guild.channels
            embed = embed_func(idioma, channels) if num_params > 1 else embed_func(idioma)
        else:
            embed = embed_func(idioma) if num_params == 1 else embed_func(idioma, *args)
    except Exception as e:
        print(f"[ERROR] ao gerar embed {last_embed}: {e}")
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
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = get_language_embed()
            msg = await channel.send(embed=embed)
            await msg.add_reaction("🇺🇸")
            await msg.add_reaction("🇧🇷")
            mensagem_idioma_id[str(guild.id)] = msg.id
            break

@bot.event
async def on_member_join(member):
    guild_id = str(member.guild.id)
    server_modos = carregar_modos().get(guild_id, {}).get("modos", {})
    modo_recepcao = next((m for m in server_modos.values() if m.get("recepcao")), None)
    if not modo_recepcao: return
    roles = modo_recepcao.get("roles", [])
    if not roles: return
    role = member.guild.get_role(int(roles[0]))
    if not role: return
    try:
        await member.add_roles(role)
        print(f"[INFO] Cargo de recepção '{role.name}' atribuído a {member.name}")
    except Exception as e:
        print(f"[ERROR] Falha ao atribuir cargo de recepção: {e}")

@bot.event
async def on_raw_reaction_add(payload):
    # Ignorar reações do próprio bot
    if payload.user_id == bot.user.id:
        return

    # Tentativa de blindagem caso guild ou canal não existam
    guild = bot.get_guild(payload.guild_id)
    canal = bot.get_channel(payload.channel_id)
    if not guild or not canal:
        return

    user_id = payload.user_id
    guild_id = payload.guild_id
    current = user_progress.get(guild_id, {}).get(user_id)

    # -------------------- VOLTAR --------------------
    if payload.emoji.name == "🔙":
        await go_back(canal, user_id, guild_id)
        
    # -------------------- AVANÇAR --------------------
    elif payload.emoji.name == "✅":
        if current == "get_mode_selected_embed":
            criando_modo[user_id] = "esperando_nome"
            await go_next(canal, user_id, guild_id)
            return

        elif current == "get_reception_mode_question_embed":
            modo_id = modo_ids.get(user_id)
            if not modo_id:
                return

            modos = carregar_modos()
            modo = modos.get(str(guild_id), {}).get("modos", {}).get(modo_id)
            if not modo:
                return

            cargo_id = int(modo["roles"][0]) if modo.get("roles") else None
            canais_ids = modo.get("channels", [])
            role = guild.get_role(cargo_id) if cargo_id else None

            if role:
                for cid in canais_ids:
                    ch = guild.get_channel(int(cid))
                    if ch:
                        try:
                            overwrites = ch.overwrites.copy()
                            overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=False)
                            overwrites[role] = discord.PermissionOverwrite(view_channel=True)
                            await ch.edit(overwrites=overwrites)
                        except Exception as e:
                            print(f"[ERROR] Falha ao atualizar permissões de {ch}: {e}")

            recepcao_anterior = atribuir_recepcao(guild_id, modo_id)

            if recepcao_anterior:
                old_role_id = modos.get(str(guild_id), {}).get("modos", {}).get(recepcao_anterior, {}).get("roles", [None])[0]
                old_role = guild.get_role(int(old_role_id)) if old_role_id else None
                old_name = old_role.name if old_role else "N/A"
                await go_next(canal, user_id, guild_id, resultado=("get_reception_replaced_embed", old_name, role.name))
            else:
                await go_next(canal, user_id, guild_id, resultado=("get_reception_assigned_embed", role.name))

            # Resetar flag ao finalizar edição
            dados = carregar_modos()
            if str(guild_id) in dados and "modos" in dados[str(guild_id)] and modo_id in dados[str(guild_id)]["modos"]:
                dados[str(guild_id)]["modos"][modo_id]["em_edicao"] = False
                salvar_modos(dados)
                MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = dados[str(guild_id)]["modos"][modo_id]

        else:
            await go_next(canal, user_id, guild_id)

    # -------------------- PULAR --------------------
    elif payload.emoji.name == "❌":
        if current == "get_reception_mode_question_embed":
            modo_id = modo_ids.get(user_id)
            if not modo_id:
                return

            modos = carregar_modos()
            modo = modos.get(str(guild_id), {}).get("modos", {}).get(modo_id)

            cargo_id = int(modo["roles"][0]) if modo and modo.get("roles") else None
            canais_ids = modo.get("channels", []) if modo else []
            role = guild.get_role(cargo_id) if cargo_id else None

            if role:
                for cid in canais_ids:
                    ch = guild.get_channel(int(cid))
                    if ch:
                        try:
                            overwrites = ch.overwrites.copy()
                            overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=False)
                            overwrites[role] = discord.PermissionOverwrite(view_channel=True)
                            await ch.edit(overwrites=overwrites)
                        except Exception as e:
                            print(f"[ERROR] Falha ao atualizar permissões de {ch} (skip): {e}")

            role_name = role.name if role else "N/A"
            await go_next(canal, user_id, guild_id, resultado=("get_reception_skipped_embed", role_name))

            # Resetar flag ao finalizar edição (skip)
            dados = carregar_modos()
            if str(guild_id) in dados and "modos" in dados[str(guild_id)] and modo_id in dados[str(guild_id)]["modos"]:
                dados[str(guild_id)]["modos"][modo_id]["em_edicao"] = False
                salvar_modos(dados)
                MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = dados[str(guild_id)]["modos"][modo_id]

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    guild_id = message.guild.id if message.guild else None
    idioma = obter_idioma(guild_id) if guild_id else "pt"
    estado = criando_modo.get(user_id)
    current = user_progress.get(guild_id, {}).get(user_id)

    dados = carregar_modos()
    # Garantir estrutura do guild
    if guild_id and str(guild_id) not in dados:
        dados[str(guild_id)] = {"modos": {}}

    # -------------------- ETAPA EDIÇÃO (get_edit_embed) --------------------
    current = user_progress.get(guild_id, {}).get(user_id)
    if current == "get_edit_embed" and message.content.startswith("#"):
        nome_modo = message.content[1:].strip()
        modo_id = modo_existe(guild_id, nome_modo)

        if not modo_id:
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

        if modo_id not in dados[str(guild_id)]["modos"]:
            dados[str(guild_id)]["modos"][modo_id] = {}

        dados[str(guild_id)]["modos"][modo_id]["em_edicao"] = True

        salvar_modos(dados)
        MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = dados[str(guild_id)]["modos"][modo_id]

        em_edicao[user_id] = True
        modo_atual[user_id] = modo_id
        modo_ids[user_id] = modo_id

        embed = get_mode_selected_embed(nome_modo, idioma)
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("🔙")
        await msg.add_reaction("✅")
        mensagem_voltar_ids[str(guild_id)] = msg.id
        mensagem_avancar_ids[str(guild_id)] = msg.id
        user_progress[guild_id][user_id] = "get_mode_selected_embed"
        criando_modo[user_id] = "iniciando_edicao"
        return

    # -------------------- ETAPA NOME (criação ou edição) --------------------
    if message.content.startswith("#"):
        nome_modo = message.content[1:].strip()

        # Validação de tamanho
        if not 2 <= len(nome_modo) <= 15:
            embed = get_invalid_name_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "nome_invalido"
            push_embed(user_id, "get_create_embed")
            return

        modo_id = modo_ids.get(user_id)
        esta_editando = (
            modo_id and dados.get(str(guild_id), {}).get("modos", {}).get(modo_id, {}).get("em_edicao", False)
        )

        if esta_editando:
            # -------------------- EDIÇÃO --------------------
            dados[str(guild_id)]["modos"][modo_id]["nome"] = nome_modo
            salvar_modos(dados)
            MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = dados[str(guild_id)]["modos"][modo_id]
            embed = get_name_saved_embed(idioma)
            criando_modo[user_id] = "nome_salvo"
        else:
            # -------------------- CRIAÇÃO --------------------
            modo_id_existente = modo_existe(guild_id, nome_modo)
            if modo_id_existente:
                embed = get_name_conflict_embed(idioma)
                criando_modo[user_id] = "nome_conflito"
            else:
                modo_id = criar_modo(guild_id, user_id, nome_modo)
                modo_ids[user_id] = modo_id

                # Recarrega dados e garante estrutura
                dados = carregar_modos()
                dados.setdefault(str(guild_id), {}).setdefault("modos", {}).setdefault(modo_id, {})
                dados[str(guild_id)]["modos"][modo_id]["em_edicao"] = True
                salvar_modos(dados)

                # Atualiza cache
                MODOS_CACHE.setdefault(str(guild_id), {}).setdefault("modos", {})[modo_id] = dados[str(guild_id)]["modos"][modo_id]

                embed = get_name_saved_embed(idioma)
                criando_modo[user_id] = "nome_salvo"

        # Atualiza histórico e envia embed final
        push_embed(user_id, "get_create_embed")
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("🔙")
        await msg.add_reaction("✅")
        mensagem_voltar_ids[str(guild_id)] = msg.id
        mensagem_avancar_ids[str(guild_id)] = msg.id
        user_progress.setdefault(guild_id, {})[user_id] = "get_name_saved_embed"
        return

    # -------------------- ETAPA CARGO --------------------
    if estado == "selecionando_cargo":
        roles = []

        if message.role_mentions:
            roles = message.role_mentions
        else:
            m = re.search(r"<@&(\d+)>", message.content)
            if m:
                rid = int(m.group(1))
                role = message.guild.get_role(rid)
                if role:
                    roles = [role]
            else:
                nome = message.content.strip()
                if nome:
                    role = discord.utils.get(message.guild.roles, name=nome)
                    if role:
                        roles = [role]

        if not roles:
            embed = get_invalid_role_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "cargo_invalido"
            return

        try:
            salvar_roles_modo(guild_id, modo_ids[user_id], roles)
            salvar_modos(carregar_modos())
        except Exception as e:
            print(f"[ERROR] salvar_roles_modo falhou: {e}")
            embed = get_invalid_role_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "cargo_invalido"
            return

        try:
            await message.delete()
        except:
            pass

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
        return

    # -------------------- ETAPA CANAL / ATRIBUIR RECEPÇÃO --------------------
    if estado == "selecionando_canal":
        channels = list(message.channel_mentions)
        content_lower = message.content.lower()

        for ch in message.guild.text_channels + message.guild.voice_channels + message.guild.categories:
            if ch.name.lower() == content_lower:
                channels.append(ch)

        if not channels:
            embed = get_invalid_channel_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "canal_invalido"
            return

        canais_invalidos = [ch.name for ch in channels if ch.overwrites]
        if canais_invalidos:
            embed = get_channel_reset_warning_embed(idioma, canais_invalidos)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(guild_id)] = msg.id
            criando_modo[user_id] = "erro_canal"
            return

        # Salvar canais no modo
        salvar_channels_modo(guild_id, modo_ids[user_id], channels)
        salvar_modos(carregar_modos())

        # -------------------- ATRIBUIR RECEPÇÃO --------------------
        try:
            atribuir_recepcao(guild_id, modo_ids[user_id], channels)
        except Exception as e:
            print(f"[ERROR] atribuir_recepcao falhou: {e}")

        embed = get_channel_saved_embed(idioma, ", ".join([ch.name for ch in channels]))
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("🔙")
        await msg.add_reaction("✅")
        user_progress.setdefault(guild_id, {})[user_id] = "get_channel_saved_embed"
        criando_modo[user_id] = "canal_salvo"
        mensagem_voltar_ids[str(guild_id)] = msg.id
        mensagem_avancar_ids[str(guild_id)] = msg.id
        return

    # ----------------- CHAMADA DOS COMANDOS -----------------
    await bot.process_commands(message)

# ----------------- COMANDOS -----------------
@bot.command(name="setup", aliases=["Setup", "SETUP"])
async def setup(ctx):
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    idioma = obter_idioma(ctx.guild.id)
    embed = get_setup_embed(idioma)
    await enviar_embed(ctx.channel, ctx.author.id, embed)

@bot.command(name="criar", aliases=["Criar", "CRIAR", "create", "Create", "CREATE"])
async def criar(ctx):
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)

    user_id = ctx.author.id
    guild_id = ctx.guild.id

    if em_edicao.get(user_id):
        em_edicao[user_id] = False
        modo_atual[user_id] = None

    modo_ids.pop(user_id, None)
    criando_modo[user_id] = None
    if guild_id in user_progress:
        user_progress[guild_id].pop(user_id, None)

    dados = carregar_modos()
    if str(guild_id) in dados:
        for mid, m in dados[str(guild_id)].get("modos", {}).items():
            if m.get("em_edicao") and m.get("criador") == str(user_id):
                m["em_edicao"] = False
    salvar_modos(dados)

    idioma = obter_idioma(guild_id)
    embed = get_create_embed(ctx.guild.roles, idioma)
    msg = await ctx.channel.send(embed=embed)

    if flow["get_create_embed"].get("back"):
        await msg.add_reaction("🔙")
    if flow["get_create_embed"].get("next"):
        await msg.add_reaction("✅")
        user_progress.setdefault(guild_id, {})[user_id] = "get_create_embed"

    criando_modo[user_id] = "esperando_nome"
    push_embed(user_id, "get_setup_embed")

@bot.command(name="editar", aliases=["Editar", "EDITAR", "edit", "Edit", "EDIT"])
async def editar(ctx):
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)

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

@bot.command(name="verificar", aliases=["Verificar", "VERIFICAR", "check", "Check", "CHECK"])
async def verificar(ctx):
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)

    idioma = obter_idioma(ctx.guild.id)
    embed = get_roles_embed(ctx.guild.roles, idioma)

    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🔙")

    mensagem_voltar_ids[str(ctx.guild.id)] = msg.id
    user_progress.setdefault(ctx.guild.id, {})[ctx.author.id] = "get_roles_embed"
    push_embed(ctx.author.id, "get_setup_embed")

@bot.command(name="funções", aliases=["Funções", "FUNÇÕES", "functions", "Functions", "FUNCTIONS"])
async def funcoes(ctx):
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)

    idioma = obter_idioma(ctx.guild.id)
    embed = get_functions_embed(idioma)

    msg = await ctx.channel.send(embed=embed)

    if flow["get_functions_embed"].get("back"):
        await msg.add_reaction("🔙")
    if flow["get_functions_embed"].get("next"):
        await msg.add_reaction("✅")
        user_progress.setdefault(ctx.guild.id, {})[ctx.author.id] = "get_functions_embed"

    user_progress.setdefault(ctx.guild.id, {})[ctx.author.id] = "get_functions_embed"
    push_embed(ctx.author.id, "get_setup_embed")

@bot.command(name="sobre", aliases=["Sobre", "SOBRE", "about", "About", "ABOUT"])
async def sobre(ctx):
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)

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

@bot.command(name="idioma", aliases=["Idioma", "IDIOMA", "language", "Language", "LANGUAGE"])
async def idioma(ctx):
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)

    embed = get_language_embed()
    msg = await ctx.send(embed=embed)

    await msg.add_reaction("🇺🇸")
    await msg.add_reaction("🇧🇷")

    mensagem_idioma_id[str(ctx.guild.id)] = msg.id
    resposta_enviada.discard(str(ctx.guild.id))

@bot.command(name="limpar", aliases=["Limpar", "LIMPAR", "clean", "Clean", "CLEAN"])
async def limpar(ctx):
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)

# ----------------- RODA O BOT -----------------
bot.run(TOKEN)