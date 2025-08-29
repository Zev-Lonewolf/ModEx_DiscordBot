import re
import discord
from discord.ext import commands
from config import TOKEN, PREFIX, CAMINHO_IDIOMAS
from utils.modos import (
    criar_modo,
    modo_existe,
    salvar_roles_modo,
    carregar_modos,
    salvar_channels_modo,
    salvar_recepcao_modo,
    atribuir_recepcao
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
    get_role_select_embed,
    get_role_saved_embed,
    get_invalid_role_embed,
    get_channel_select_embed,
    get_channel_saved_embed,
    get_invalid_channel_embed,
    get_reception_mode_question_embed,
    get_reception_assigned_embed,
    get_reception_replaced_embed,
    get_reception_error_embed,
    get_name_conflict_embed
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
historico_embeds = {}
resposta_enviada = set()
modo_ids = {}

def push_embed(user_id, estado):
    historico_embeds.setdefault(user_id, []).append(estado)

def pop_embed(user_id):
    if user_id in historico_embeds and historico_embeds[user_id]:
        return historico_embeds[user_id].pop()
    return None

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

async def limpar_mensagens(canal, autor1, autor2, quantidade=50):
    def check(msg):
        return msg.author in [autor1, autor2]
    try:
        await canal.purge(limit=quantidade, check=check)
    except Exception as e:
        print(f"[limpar_mensagens] purge falhou: {e}")
        try:
            async for m in canal.history(limit=20):
                if m.author in [autor1, autor2]:
                    try:
                        await m.delete()
                    except:
                        pass
        except Exception as e2:
            print(f"[limpar_mensagens] fallback falhou: {e2}")

async def safe_delete_message(msg):
    try:
        await msg.delete()
    except Exception as e:
        print(f"[safe_delete_message] não foi possível apagar mensagem: {e}")

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
    user_id = payload.user_id
    idioma = obter_idioma(guild_id)
    estado = criando_modo.get(user_id)

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

        embed = get_greeting_embed(obter_idioma(guild_id))
        try:
            msg = await canal.fetch_message(message_id)
            await msg.delete()
        except:
            pass
        await canal.send(embed=embed)
        resposta_enviada.add(guild_id)
        return

    voltar_msg_id = mensagem_voltar_ids.get(guild_id)
    avancar_msg_id = mensagem_avancar_ids.get(guild_id)

    # Voltar
    if payload.emoji.name == "🔙" and message_id == voltar_msg_id:
        estado_anterior = pop_embed(user_id)
        if estado_anterior == "get_create_embed":
            embed = get_create_embed(canal.guild.roles, idioma)
            criando_modo[user_id] = "esperando_nome"
        elif estado_anterior == "get_initial_create_embed":
            embed = get_initial_create_embed(idioma)
            criando_modo[user_id] = "info_inicial"
        else:
            embed = get_setup_embed(idioma)
            criando_modo.pop(user_id, None)

        await limpar_mensagens(canal, bot.user, bot.user)
        msg = await canal.send(embed=embed)
        await msg.add_reaction("🔙")

        if criando_modo.get(user_id) not in ["info_inicial", "nome_salvo"]:
            await msg.add_reaction("✅")
            mensagem_avancar_ids[guild_id] = msg.id

        mensagem_voltar_ids[guild_id] = msg.id
        return

    # Avançar
    if payload.emoji.name == "✅" and message_id == avancar_msg_id:
        # Etapa: Nome
        if estado == "esperando_nome":
            push_embed(user_id, "get_create_embed")
            embed = get_initial_create_embed(idioma)
            criando_modo[user_id] = "info_inicial"

            await limpar_mensagens(canal, bot.user, bot.user)
            nova_msg = await canal.send(embed=embed)
            await nova_msg.add_reaction("🔙")
            mensagem_voltar_ids[guild_id] = nova_msg.id
            return

        # Etapa: Cargo
        elif estado == "nome_salvo":
            push_embed(user_id, "get_initial_create_embed")
            embed = get_role_select_embed(idioma, canal.guild.roles)
            criando_modo[user_id] = "escolher_cargo"

            await limpar_mensagens(canal, bot.user, bot.user)
            nova_msg = await canal.send(embed=embed)
            await nova_msg.add_reaction("🔙")
            mensagem_voltar_ids[guild_id] = nova_msg.id
            return
        
        # Etapa: Canais
        elif estado == "cargo_salvo":
            push_embed(user_id, "get_role_select_embed")
            embed = get_channel_select_embed(idioma)
            criando_modo[user_id] = "escolher_canal"

            await limpar_mensagens(canal, bot.user, bot.user)
            nova_msg = await canal.send(embed=embed)
            await nova_msg.add_reaction("🔙")
            mensagem_voltar_ids[guild_id] = nova_msg.id
            return

    # Etapa: Pergunta de recepção
    if estado == "canais_salvos":
        push_embed(user_id, "get_channel_select_embed")
        embed = get_reception_mode_question_embed(idioma)
        criando_modo[user_id] = "modo_recepcao"

        await limpar_mensagens(canal, bot.user, bot.user)
        nova_msg = await canal.send(embed=embed)
        await nova_msg.add_reaction("✅")
        await nova_msg.add_reaction("❌")
        mensagem_voltar_ids[guild_id] = nova_msg.id
        mensagem_avancar_ids[guild_id] = nova_msg.id
        return

    if estado == "modo_recepcao" and message_id == avancar_msg_id:
        try:
            dados = carregar_modos()
            server_modos = dados.setdefault(guild_id, {}).setdefault("modos", {})

            if payload.emoji.name == "✅":
                # Atribui recepção e pega o ID do modo anterior, se houver
                recepcao_anterior = atribuir_recepcao(guild_id, modo_ids[user_id])
                await limpar_mensagens(canal, bot.user, bot.user)

                current_role_name = server_modos[modo_ids[user_id]].get("nome", "Unknown")

                if recepcao_anterior:
                    old_role_name = server_modos[recepcao_anterior].get("nome", "Unknown")
                    embed = get_reception_replaced_embed(idioma, old_role_name, current_role_name)
                else:
                    embed = get_reception_assigned_embed(idioma, current_role_name)

                msg = await canal.send(embed=embed)
                await msg.add_reaction("🔙")
                criando_modo[user_id] = "modo_recepcao_salvo"
                return

            elif payload.emoji.name == "❌":
                salvar_recepcao_modo(guild_id, modo_ids[user_id], False)
                await limpar_mensagens(canal, bot.user, bot.user)

                current_role_name = server_modos[modo_ids[user_id]].get("nome", "Unknown")
                embed = get_reception_assigned_embed(idioma, current_role_name, assigned=False)

                msg = await canal.send(embed=embed)
                await msg.add_reaction("🔙")
                criando_modo[user_id] = "modo_recepcao_salvo"
                return

        except Exception:
            await limpar_mensagens(canal, bot.user, bot.user)
            embed = get_reception_error_embed(idioma)
            msg = await canal.send(embed=embed)
            await msg.add_reaction("🔙")
            criando_modo[user_id] = "modo_recepcao_erro"
            return

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    estado = criando_modo.get(user_id)
    idioma = obter_idioma(message.guild.id) if message.guild else "pt"

    if estado == "info_inicial" and message.content.startswith("#"):
        nome_modo = message.content[1:].strip()

        if not 2 <= len(nome_modo) <= 15:
            embed = get_invalid_name_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(message.guild.id)] = msg.id
            criando_modo[user_id] = "erro_nome"
            return

        modo_existente = modo_existe(message.guild.id, nome_modo)
        if modo_existente:
            embed = get_name_conflict_embed(idioma, nome_modo)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            mensagem_voltar_ids[str(message.guild.id)] = msg.id
            criando_modo[user_id] = f"editar_modo_{modo_existente}"
            return

        modo_id = criar_modo(message.guild.id, user_id, nome_modo)
        modo_ids[user_id] = modo_id

        embed = get_name_saved_embed(idioma)
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("🔙")
        await msg.add_reaction("✅")

        mensagem_voltar_ids[str(message.guild.id)] = msg.id
        mensagem_avancar_ids[str(message.guild.id)] = msg.id
        criando_modo[user_id] = "nome_salvo"
        return


    if estado == "escolher_cargo":
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
            mensagem_voltar_ids[str(message.guild.id)] = msg.id
            criando_modo[user_id] = "erro_cargo"
            return

        try:
            salvar_roles_modo(message.guild.id, modo_ids[user_id], roles)
        except Exception as e:
            print(f"[ERROR] salvar_roles_modo falhou: {e}")
            embed = get_invalid_role_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(message.guild.id)] = msg.id
            criando_modo[user_id] = "erro_cargo"
            return

        try:
            await safe_delete_message(message)
        except:
            pass

        role = roles[0]
        embed = get_role_saved_embed(idioma, role.name)
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("🔙")
        await msg.add_reaction("✅")

        mensagem_voltar_ids[str(message.guild.id)] = msg.id
        mensagem_avancar_ids[str(message.guild.id)] = msg.id
        criando_modo[user_id] = "cargo_salvo"

        return
    
    if estado == "escolher_canal":
        channels = []
        for ch in message.channel_mentions:
            channels.append(ch)

        guild = message.guild
        content_lower = message.content.lower()
        for ch in guild.text_channels + guild.voice_channels + guild.categories:
            if ch.name.lower() == content_lower:
                channels.append(ch)

        if not channels:
            embed = get_invalid_channel_embed(idioma)
            await limpar_mensagens(message.channel, bot.user, message.author)
            msg = await message.channel.send(embed=embed)
            await msg.add_reaction("🔙")
            mensagem_voltar_ids[str(message.guild.id)] = msg.id
            return

        salvar_channels_modo(message.guild.id, modo_ids[user_id], channels)

        embed = get_channel_saved_embed(idioma, ", ".join([ch.name for ch in channels]))
        await limpar_mensagens(message.channel, bot.user, message.author)
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction("🔙")
        await msg.add_reaction("✅")

        mensagem_voltar_ids[str(message.guild.id)] = msg.id
        mensagem_avancar_ids[str(message.guild.id)] = msg.id
        criando_modo[user_id] = "canais_salvos"
        return

    await bot.process_commands(message)

@bot.command(name="limpar", aliases=["Limpar", "LIMPAR", "clean", "Clean", "CLEAN"])
async def limpar(ctx):
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)

@bot.command(name="setup", aliases=["Setup", "SETUP"])
async def setup(ctx):
    await ctx.message.delete()
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    idioma = obter_idioma(ctx.guild.id)
    embed = get_setup_embed(idioma)
    await ctx.send(embed=embed)

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

@bot.command(name="sobre", aliases=["Sobre", "SOBRE", "about", "About", "ABOUT"])
async def sobre(ctx):
    await ctx.message.delete()
    idioma = obter_idioma(ctx.guild.id)
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    embed = get_about_embed(idioma)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🔙")
    mensagem_voltar_ids[str(ctx.guild.id)] = msg.id

@bot.command(name="funções", aliases=["Funções", "FUNÇÕES", "functions", "Functions", "FUNCTIONS"])
async def funções(ctx):
    await ctx.message.delete()
    idioma = obter_idioma(ctx.guild.id)
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    embed = get_functions_embed(idioma)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🔙")
    mensagem_voltar_ids[str(ctx.guild.id)] = msg.id

@bot.command(name="verificar", aliases=["Verificar", "VERIFICAR", "check", "Check", "CHECK"])
async def verificar(ctx):
    await ctx.message.delete()
    idioma = obter_idioma(ctx.guild.id)
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    embed = get_roles_embed(ctx.guild.roles, idioma)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🔙")
    mensagem_voltar_ids[str(ctx.guild.id)] = msg.id

@bot.command(name="editar", aliases=["Editar", "EDITAR", "edit", "Edit", "EDIT"])
async def editar(ctx):
    await ctx.message.delete()
    idioma = obter_idioma(ctx.guild.id)
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    embed = get_edit_embed(idioma)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🔙")
    mensagem_voltar_ids[str(ctx.guild.id)] = msg.id

@bot.command(name="criar", aliases=["Criar", "CRIAR", "create", "Create", "CREATE"])
async def criar(ctx):
    await ctx.message.delete()
    idioma = obter_idioma(ctx.guild.id)
    embed = get_create_embed(ctx.guild.roles, idioma)
    await limpar_mensagens(ctx.channel, ctx.author, bot.user)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🔙")
    await msg.add_reaction("✅")
    mensagem_voltar_ids[str(ctx.guild.id)] = msg.id
    mensagem_avancar_ids[str(ctx.guild.id)] = msg.id
    criando_modo[ctx.author.id] = "esperando_nome"

bot.run(TOKEN)
