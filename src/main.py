import discord
from discord.ext import commands
from config import TOKEN, PREFIX
from config import CAMINHO_IDIOMAS
from utils.modos import(
    salvar_nome_modo, 
    carregar_modos, 
    salvar_modos, 
    salvar_json
)
import json
from embed import (
    get_language_embed,
    get_greeting_embed,
    get_setup_embed,
    get_about_embed,
    get_functions_embed,
    get_roles_embed,
    get_edit_embed,
    get_create_embed,
    get_initial_create_embed,
    get_name_saved_embed,
    get_invalid_name_embed,
    get_role_requested_embed,
    get_invalid_role_embed,
    get_channels_request_embed,
    get_invalid_channels_embed,
    get_allowed_roles_embed,
    get_invalid_roles_embed,
    get_final_embed
)

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

mensagem_idioma_id = {}
mensagem_voltar_ids = {}
mensagem_avancar_ids = {}
criando_modo = {}
resposta_enviada = set()
caminho_modos = "data/modos.json"

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

@bot.before_invoke
async def preparar_contexto(ctx):
    ctx.language = obter_idioma(ctx.guild.id)

async def limpar_mensagens(canal, autor1, autor2, quantidade=15):
    def check(msg):
        return msg.author == autor1 or msg.author == autor2

    try:
        await canal.purge(limit=quantidade, check=check)
    except Exception as e:
        print(f"Erro ao limpar mensagens: {e}")

@bot.event
async def on_ready():
    print(f"Usuário conectado: {bot.user}!")

@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = get_language_embed()
            message = await channel.send(embed=embed)
            await message.add_reaction("🇺🇸")
            await message.add_reaction("🇧🇷")
            mensagem_idioma_id[str(guild.id)] = message.id
            break

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    guild_id = str(payload.guild_id)
    message_id = payload.message_id
    canal = bot.get_channel(payload.channel_id)

    idioma_msg_id = mensagem_idioma_id.get(guild_id)
    if message_id == idioma_msg_id:
        if guild_id in resposta_enviada:
            return

        if payload.emoji.name == "🇧🇷":
            definir_idioma(guild_id, "pt")
        elif payload.emoji.name == "🇺🇸":
            definir_idioma(guild_id, "en")
        else:
            return

        idioma = obter_idioma(guild_id)
        embed = get_greeting_embed(idioma)

        try:
            msg = await canal.fetch_message(message_id)
            await msg.delete()
        except Exception as e:
            print(f"Erro ao apagar mensagem de idioma: {e}")

        await canal.send(embed=embed)
        resposta_enviada.add(guild_id)
        return

    voltar_msg_id = mensagem_voltar_ids.get(guild_id)
    avancar_msg_id = mensagem_avancar_ids.get(guild_id)
    estado = criando_modo.get(payload.user_id)
    idioma = obter_idioma(guild_id)

    if payload.emoji.name == "🔙":
        if estado is None:
            embed = get_allowed_roles_embed(idioma)
            criando_modo[payload.user_id] = "esperando_cargos_adicionais"
            await limpar_mensagens(canal, bot.user, bot.user)
            try:
                msg = await canal.fetch_message(message_id)
                await msg.delete()
            except Exception:
                pass
            await canal.send(embed=embed)
            return
        if message_id == voltar_msg_id:
            if estado == "erro_nome":
                embed = get_initial_create_embed(idioma)
                criando_modo[payload.user_id] = "esperando_nome"
            elif estado == "nome_salvo":
                embed = get_initial_create_embed(idioma)
                criando_modo[payload.user_id] = "esperando_nome"
            elif estado == "info_inicial":
                embed = get_setup_embed(idioma)
            elif estado == "esperando_cargo":
                embed = get_name_saved_embed(idioma)
                criando_modo[payload.user_id] = "nome_salvo"
            else:
                embed = get_setup_embed(idioma)
                criando_modo.pop(payload.user_id, None)

            await limpar_mensagens(canal, bot.user, bot.user)
            try:
                msg = await canal.fetch_message(message_id)
                await msg.delete()
            except Exception:
                pass
            await canal.send(embed=embed)
            return
        
    if payload.emoji.name == "✅":
        if message_id == avancar_msg_id:
            embed = get_initial_create_embed(idioma)
            criando_modo[payload.user_id] = "esperando_nome"
        elif estado == "nome_salvo" and payload.emoji.name == "✅":
            embed = get_role_requested_embed(idioma)
            criando_modo[payload.user_id] = "esperando_cargo"
        elif estado == "erro_nome":
            embed = get_role_requested_embed(idioma)
            criando_modo[payload.user_id] = "esperando_cargo"
        elif estado == "info_inicial":
            embed = get_initial_create_embed(idioma)
            criando_modo[payload.user_id] = "esperando_nome"
        else:
            embed = get_setup_embed(idioma)
            criando_modo.pop(payload.user_id, None)

        await limpar_mensagens(canal, bot.user, bot.user)
        try:
            msg = await canal.fetch_message(message_id)
            await msg.delete()
        except Exception:
            pass
        await canal.send(embed=embed)
        return
    
    if criando_modo.get(payload.user_id) == "nome_salvo":
        if payload.emoji.name == "🔙":
            idioma = obter_idioma(guild_id)
            embed = get_initial_create_embed(idioma)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(payload.guild_id)] = msg.id
            await limpar_mensagens(canal, bot.user, bot.user)
            try:
                msg = await canal.fetch_message(message_id)
                await msg.delete()
            except Exception:
                pass
            await canal.send(embed=embed)
            criando_modo[payload.user_id] = "esperando_nome"
            return

        elif payload.emoji.name == "✅":
            idioma = obter_idioma(guild_id)
            embed = get_role_requested_embed(idioma)
            await limpar_mensagens(canal, bot.user, bot.user)
            try:
                msg = await canal.fetch_message(message_id)
                await msg.delete()
            except Exception:
                pass
            await canal.send(embed=embed)
            criando_modo[payload.user_id] = "esperando_cargo"
            return

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    estado = criando_modo.get(message.author.id)
    idioma = obter_idioma(message.guild.id) if message.guild else "pt"

    if estado == "esperando_nome":
        if message.content.startswith("#"):
            nome_modo = message.content[1:].strip()

            if len(nome_modo) < 2 or len(nome_modo) > 15:
                embed = get_invalid_name_embed(idioma)
                await limpar_mensagens(message.channel, bot.user, message.author)
                msg = await message.channel.send(embed=embed)
                await msg.add_reaction("🔙")
                mensagem_voltar_ids[str(message.guild.id)] = msg.id
                criando_modo[message.author.id] = "erro_nome"
                return

            if message.guild is not None:
                salvar_nome_modo(message.guild.id, message.author.id, nome_modo)
                embed = get_name_saved_embed(idioma)
                await limpar_mensagens(message.channel, bot.user, message.author)
                msg = await message.channel.send(embed=embed)
                await msg.add_reaction("🔙")
                await msg.add_reaction("✅")
                mensagem_voltar_ids[str(message.guild.id)] = msg.id
                criando_modo[message.author.id] = "nome_salvo"
            else:
                await message.channel.send("Este comando só pode ser usado em um servidor.")
        return

    elif estado == "esperando_cargo":
        if message.role_mentions:
            cargo = message.role_mentions[0]
            dados = carregar_modos()
            server_id = str(message.guild.id)
            user_id = str(message.author.id)

            dados.setdefault(server_id, {})
            dados[server_id].setdefault("modos", {})
            dados[server_id]["modos"].setdefault(user_id, {})

            dados[server_id]["modos"][user_id]["cargo_principal"] = cargo.id
            salvar_modos(dados)

            embed = get_channels_request_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(message.guild.id)] = msg.id
            criando_modo[message.author.id] = "esperando_canais"
        else:
            embed = get_invalid_role_embed(idioma)
            await message.channel.send(embed=embed)
        return

    elif estado == "esperando_canais":
        canais_mencionados = message.channel_mentions
        if not canais_mencionados:
            embed = get_invalid_channels_embed(idioma)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(message.guild.id)] = msg.id
            return

        dados = carregar_modos()
        servidor_id = str(message.guild.id)
        usuario_id = str(message.author.id)

        dados.setdefault(servidor_id, {})
        dados[servidor_id].setdefault("modos", {})
        dados[servidor_id]["modos"].setdefault(usuario_id, {})

        canais_ids = [canal.id for canal in canais_mencionados]
        dados[servidor_id]["modos"][usuario_id]["canais"] = canais_ids
        salvar_modos(dados)

        embed = get_allowed_roles_embed(idioma)
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("🔙")
        mensagem_voltar_ids[str(message.guild.id)] = msg.id
        criando_modo[message.author.id] = "esperando_cargos_adicionais"
        return

    elif estado == "esperando_cargos_adicionais":
        servidor_id = str(message.guild.id)
        usuario_id = str(message.author.id)
        language = idioma
        dados = carregar_modos()

        if message.content.lower() in ["pular", "skip"]:
            dados[servidor_id]["modos"][usuario_id]["cargos_permitidos"] = []
            salvar_modos(dados)
            criando_modo.pop(usuario_id, None)

            await limpar_mensagens(message.channel, bot.user, message.author)
            embed = get_final_embed(language)
            await message.channel.send(embed=embed)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(message.guild.id)] = msg.id
            return

        cargos_mencionados = message.role_mentions
        if not cargos_mencionados:
            embed = get_invalid_roles_embed(language)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(message.guild.id)] = msg.id
            return

        cargo_principal_id = dados[servidor_id]["modos"][usuario_id].get("cargo_principal")
        cargos_validos = [cargo.id for cargo in cargos_mencionados]

        if not cargos_validos:
            embed = get_invalid_roles_embed(language)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(message.guild.id)] = msg.id
            return

        dados[servidor_id]["modos"][usuario_id]["cargos_permitidos"] = cargos_validos
        salvar_modos(dados)

        criando_modo.pop(usuario_id, None)

        await limpar_mensagens(message.channel, bot.user, message.author)
        embed = get_final_embed(language)
        await message.channel.send(embed=embed)

        canais_ids = dados[servidor_id]["modos"][usuario_id].get("canais", [])
        cargos_permitidos = dados[servidor_id]["modos"][usuario_id].get("cargos_permitidos", [])
        cargo_principal_id = dados[servidor_id]["modos"][usuario_id].get("cargo_principal")

        if cargo_principal_id and cargo_principal_id not in cargos_permitidos:
            cargos_permitidos.append(cargo_principal_id)

        for canal_id in canais_ids:
            canal = message.guild.get_channel(canal_id)
            if canal:
                overwrites = {
                    message.guild.default_role: discord.PermissionOverwrite(view_channel=False)
                }
                for cargo_id in cargos_permitidos:
                    cargo = message.guild.get_role(cargo_id)
                    if cargo:
                        overwrites[cargo] = discord.PermissionOverwrite(view_channel=True)

                try:
                    await canal.edit(overwrites=overwrites)
                except Exception as e:
                    print(f"Erro ao editar canal {canal.name}: {e}")

    elif estado == "cargos_extras":
        if not message.role_mentions:
            await message.channel.send(embed=get_invalid_roles_embed(language))
            return
        cargos_extras_ids = [role.id for role in message.role_mentions]

        dados[servidor_id]["modos"][usuario_id]["cargos_extras"] = cargos_extras_ids
        salvar_json(caminho_modos, dados)

        await message.channel.send(embed=get_channels_request_embed(language))
        criando_modo[usuario_id]["etapa"] = "canais"


        return
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction("❓")
        criando_modo[ctx.message.author.id] = "esperando_cargo"
    else:
        pass

@bot.command(name="limpar", aliases=["Limpar", "LIMPAR", "clean", "Clean", "CLEAN"])
async def limpar(ctx):
    await limpar_mensagens(ctx.channel, ctx.author, ctx.bot.user)

@bot.command(name="setup", aliases=["Setup", "SETUP"])
async def setup(ctx):
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, ctx.bot.user)

    idioma = obter_idioma(ctx.guild.id)
    embed = get_setup_embed(idioma)
    await ctx.send(embed=embed)

@bot.command(name="idioma", aliases=["Idioma", "IDIOMA", "language", "Language", "LANGUAGE"])
async def idioma(ctx):
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, ctx.bot.user)

    embed = get_language_embed()
    message = await ctx.send(embed=embed)
    await message.add_reaction("🇺🇸")
    await message.add_reaction("🇧🇷")
    mensagem_idioma_id[str(ctx.guild.id)] = message.id
    resposta_enviada.discard(str(ctx.guild.id))

@bot.command(name="sobre", aliases=["Sobre", "SOBRE", "about", "About", "ABOUT"])
async def sobre(ctx):
    await ctx.message.delete()
    idioma = obter_idioma(ctx.guild.id)
    embed = get_about_embed(idioma)
    await limpar_mensagens(ctx.channel, ctx.author, ctx.bot.user)
    message = await ctx.send(embed=embed)
    await message.add_reaction("🔙")
    mensagem_voltar_ids[str(ctx.guild.id)] = message.id

@bot.command(name="funções", aliases=["Funções", "FUNÇÕES", "functions", "Functions", "FUNCTIONS"])
async def funções(ctx):
    await ctx.message.delete()
    idioma = obter_idioma(ctx.guild.id)
    embed = get_functions_embed(idioma)
    await limpar_mensagens(ctx.channel, ctx.author, ctx.bot.user)
    message = await ctx.send(embed=embed)
    await message.add_reaction("🔙")
    mensagem_voltar_ids[str(ctx.guild.id)] = message.id

@bot.command(name="verificar", aliases=["Verificar", "VERIFICAR", "check", "Check", "CHECK"])
async def verificar(ctx):
    await ctx.message.delete()
    idioma = obter_idioma(ctx.guild.id)
    embed = get_roles_embed(ctx.guild.roles, idioma)
    await limpar_mensagens(ctx.channel, ctx.author, ctx.bot.user)
    message = await ctx.send(embed=embed)
    await message.add_reaction("🔙")
    mensagem_voltar_ids[str(ctx.guild.id)] = message.id

@bot.command(name="editar", aliases=["Editar", "EDITAR", "edit", "Edit", "EDIT"])
async def editar(ctx):
    await ctx.message.delete()
    idioma = obter_idioma(ctx.guild.id)
    embed = get_edit_embed(idioma)
    await limpar_mensagens(ctx.channel, ctx.author, ctx.bot.user)
    message = await ctx.send(embed=embed)
    await message.add_reaction("🔙")
    mensagem_voltar_ids[str(ctx.guild.id)] = message.id

@bot.command(name="criar", aliases=["Criar", "CRIAR", "create", "Create", "CREATE"])
async def criar(ctx):
    await ctx.message.delete()
    idioma = obter_idioma(ctx.guild.id)
    embed = get_create_embed(ctx.guild.roles, idioma)
    await limpar_mensagens(ctx.channel, ctx.author, ctx.bot.user)
    message = await ctx.send(embed=embed)
    await message.add_reaction("🔙")
    mensagem_voltar_ids[str(ctx.guild.id)] = message.id
    await message.add_reaction("✅")
    mensagem_avancar_ids[str(ctx.guild.id)]= message.id
    criando_modo[ctx.author.id] = "esperando_nome"

bot.run(TOKEN)