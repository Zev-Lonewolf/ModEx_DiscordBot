import discord
from discord.ext import commands
from config import TOKEN, PREFIX
import json
from embed import (
    get_language_embed,
    get_greeting_embed,
    get_setup_embed,
    get_about_embed,
    get_functions_embed,
    get_roles_embed,
    get_edit_embed
)

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

mensagem_idioma_id = {}
mensagem_voltar_ids = {}
resposta_enviada = set()

def carregar_idiomas():
    try:
        with open("idiomas.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def salvar_idiomas(dados):
    with open("idiomas.json", "w", encoding="utf-8") as f:
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
    if message_id == voltar_msg_id and payload.emoji.name == "🔙":
        idioma = obter_idioma(guild_id)
        embed = get_setup_embed(idioma)

        await limpar_mensagens(canal, bot.user, bot.user)
        try:
            msg = await canal.fetch_message(message_id)
            await msg.delete()
        except Exception as e:
            print(f"Erro ao apagar mensagem de voltar: {e}")

        await canal.send(embed=embed)
        return

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

bot.run(TOKEN)