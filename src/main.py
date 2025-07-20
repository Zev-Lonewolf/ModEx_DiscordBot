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
    print(f"ModEx está online como: {bot.user}!")

@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(
                title="🌎 Select your language | Selecione seu idioma",
                description="React with your language below:\n\n🇧🇷 **Português**\n🇺🇸 **English**",
                color=discord.Color.blue()
            )
            embed.set_footer(text="ModEx - Language Setup / Setup de Idioma")

            message = await channel.send(embed=embed)
            await message.add_reaction("🇧🇷")
            await message.add_reaction("🇺🇸")
            break
            

bot.run(TOKEN)