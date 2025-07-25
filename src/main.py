import discord
from discord.ext import commands
from config import TOKEN, PREFIX
from discord.ui import View, Button
import json
from embed import (
    get_language_embed,
    get_greeting_embed,
    get_setup_embed,
    get_about_embed
)

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

mensagem_idioma_id = {}

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
    if payload.member.bot:
        return

    guild_id = str(payload.guild_id)
    message_id = mensagem_idioma_id.get(guild_id)

    if payload.message_id != message_id:
        return

    if payload.emoji.name == "🇧🇷":
        definir_idioma(guild_id, "pt")
    elif payload.emoji.name == "🇺🇸":
        definir_idioma(guild_id, "en")
    else:
        return

    guild = bot.get_guild(payload.guild_id)
    channel = bot.get_channel(payload.channel_id)
    idioma = obter_idioma(guild_id)
    embed = get_greeting_embed(idioma)
    await channel.send(embed=embed)

@bot.command(name="setup", aliases=["Setup", "SETUP"])
async def setup(ctx):
    idioma = obter_idioma(ctx.guild.id)
    embed = get_setup_embed(idioma)
    await ctx.send(embed=embed)

@bot.command(name="idioma", aliases=["Idioma", "IDIOMA", "language", "Language", "LANGUAGE"])
async def idioma(ctx):
    embed = get_language_embed()
    message = await ctx.send(embed=embed)
    await message.add_reaction("🇺🇸")
    await message.add_reaction("🇧🇷")

    mensagem_idioma_id[str(ctx.guild.id)] = message.id

@bot.command(name="sobre", aliases=["Sobre", "SOBRE", "about", "About", "ABOUT"])
async def sobre(ctx):
    idioma = obter_idioma(ctx.guild.id)
    embed = get_about_embed(idioma)
    await ctx.send(embed=embed)

bot.run(TOKEN)