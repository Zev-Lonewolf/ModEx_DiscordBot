import discord
from discord.ext import commands
from config import TOKEN, PREFIX

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

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
            embed.set_footer(text="🔍 Auto-detecting roles on this server | Detectando cargos automaticamente")

            message = await channel.send(embed=embed)
            await message.add_reaction("🇺🇸")
            await message.add_reaction("🇧🇷")
            break
            

bot.run(TOKEN)