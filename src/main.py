import discord
from discord.ext import commands
from config import TOKEN, PREFIX
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

LANGUAGE_FILE = "language_data.json"

if os.path.exists(LANGUAGE_FILE):
    with open(LANGUAGE_FILE, "r") as f:
        language_data = json.load(f)
else:
    language_data = {}

def get_language(guild_id):
    return language_data.get(str(guild_id), "en")

def set_language(guild_id, language):
    language_data[str(guild_id)] = language
    with open(LANGUAGE_FILE, "w") as f:
        json.dump(language_data, f, indent=4)

@bot.before_invoke
async def preparar_contexto(ctx):
    guild_id = ctx.guild.id
    language = get_language(guild_id)
    ctx.language = language

@bot.event
async def on_ready():
    print(f"Usuário conectado: {bot.user}!")

@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(
                title="**🌎 Choose your language | Escolha seu idioma**",
                description="React with the 🇺🇸 emoji for **English** or/ou reaja com o emoji 🇧🇷 para **Português (BR)**",
                color=discord.Color.greyple()
            )
            embed.set_footer(text="🔍 Detecting roles automatically... / Detectando cargos automaticamente...")

            message = await channel.send(embed=embed)
            await message.add_reaction("🇺🇸")
            await message.add_reaction("🇧🇷")
            break

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return
    
    guild_id = payload.guild_id
    emoji = str(payload.emoji)

    if str(guild_id) in language_data:
        return
    
    if emoji not in ["🇺🇸", "🇧🇷"]:
        return

    if emoji == "🇺🇸":
        set_language(guild_id, "en")
        language = "English"
    elif emoji == "🇧🇷":
        set_language(guild_id, "pt")
        language = "Português (BR)"
    else:
        return

    channel = bot.get_channel(payload.channel_id)
    if channel:
        language = get_language(guild_id)

        if language == "pt":
            embed = discord.Embed(
                title="**👋 Hey! Eu sou o ModEx!**",
                description=(
                    "Sou um bot feito para **organizar e gerenciar modos personalizados** no seu servidor! E aí, qual desses comandos você precisa agora?\n\n"
                    "**Comandos Disponíveis:**\n"
                    "`!Setup` → Abre o painel inicial do ModEx\n"
                    "`!Idioma` → Reabre a seleção de idioma\n\n"
                    "**🌐 Site:** Em breve...\n"
                ),
                color=discord.Color.blue()
            )
            embed.set_footer(text="🔍 Confirmando cargos para evitar erros...")
        else:
            embed = discord.Embed(
                title="**👋 Hey! I'm ModEx!**",
                description=(
                    "I'm a bot built to help you **organize and manage custom modes** in your server! So, which of these commands do you need right now?\n\n"
                    "**Available commands:**\n"
                    "`!Setup` → Opens ModEx’s initial panel\n"
                    "`!Language` → Reopens the language selection\n\n"
                    "**🌐 Website:** Coming soon...\n"
                ),
                color=discord.Color.blue()
            )
            embed.set_footer(text="🔍 Confirming roles to avoid setup issues...")
        await channel.send(embed=embed)

@bot.command(name="idioma", aliases= ["Idioma", "IDIOMA", "language", "Language", "LANGUAGE"])
async def language_command(ctx):
    guild = ctx.guild

    if not ctx.channel.permissions_for(guild.me).send_messages:
        return
    
    embed = discord.Embed(
        title="**🌎 Choose your language | Escolha seu idioma**",
        description="React with the 🇺🇸 emoji for **English** or/ou reaja com o emoji 🇧🇷 para **Português (BR)**",
        color=discord.Color.greyple()
    )
    embed.set_footer(text="🔍 Detecting roles automatically... / Detectando cargos automaticamente...")

    message = await ctx.send(embed=embed)
    await message.add_reaction("🇺🇸")
    await message.add_reaction("🇧🇷")

    if str(guild.id) in language_data:
        del language_data[str(guild.id)]
        with open(LANGUAGE_FILE, "w") as f:
            json.dump(language_data, f, indent=4)

@bot.command(name="setup", aliases=["Setup", "SETUP"])
async def setup_command(ctx):
    language = ctx.language

    if not ctx.channel.permissions_for(ctx.guild.me).send_messages:
        return

    if language == "pt":
        embed = discord.Embed(
            title="**📘 Painel de Configuração**",
            description="Bem-vindo ao **modo de configuração** do **ModEx**. Estou aqui para te ajudar a **gerenciar modos personalizados** no seu servidor! Abaixo estão os comandos principais que você pode usar:\n\n"
            "**Comandos Principais:**\n"
            "`!Criar` → Inicia a criação de um novo modo personalizado\n"
            "`!Editar` → Inicia a edição de um modo existente\n"
            "`!Verificar` → Verifica os cargos detectados e os modos já criados no servidor\n"
            "`!Funções` → Lista e explica todas as funções disponíveis\n"
            "`!Sobre` → Saiba mais sobre o ModEx e seu desenvolvedor\n\n"
            "Use !Idioma para trocar o idioma."
        )
        embed.set_footer(text="🗑️ Apagando mensagens anteriores para manter o canal limpo...")
    
    else:
        embed = discord.Embed(
            title="**📘 Setup Panel**",
            description="Welcome to the **ModEx configuration mode**. I'm here to help you **manage custom modes** on your server! Below are the main commands you can use:\n\n"
            "**Main Commands:**\n"
            "`!Create` → Starts the creation of a new custom mode\n"
            "`!Edit` → Starts editing an existing mode\n"
            "`!Check` → Checks detected roles and the modes already created on the server\n"
            "`!Functions` → Lists and explains all available functions\n"
            "`!About` → Learn more about ModEx and its developer\n\n"
            "Use !Language to change the language."
        )
        embed.set_footer(text="🗑️ Deleting previous messages to keep the channel clean...")

    await ctx.send(embed=embed)

bot.run(TOKEN)