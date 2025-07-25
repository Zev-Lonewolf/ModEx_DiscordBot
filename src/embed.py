import discord

def get_language_embed():
    embed = discord.Embed(
        title="**🌎 Choose your language | Escolha seu idioma**",
        description="React with the 🇺🇸 emoji for **English** or/ou reaja com o emoji 🇧🇷 para **Português (BR)**",
        color=discord.Color.greyple()
    )
    embed.set_footer(text="🔍 Detecting roles automatically... / Detectando cargos automaticamente...")
    return embed

def get_greeting_embed(language):
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
            color=discord.Color.green()
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
            color=discord.Color.green()
        )
        embed.set_footer(text="🔍 Confirming roles to avoid setup issues...")
    return embed

def get_setup_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="**📘 Painel de Configuração**",
            description=(
                "Bem-vindo ao **modo de configuração** do **ModEx**. Estou aqui para te ajudar a **gerenciar modos personalizados** no seu servidor! Abaixo estão os comandos principais que você pode usar:\n\n"
                "**Comandos Principais:**\n"
                "`!Criar` → Inicia a criação de um novo modo personalizado\n"
                "`!Editar` → Inicia a edição de um modo existente\n"
                "`!Verificar` → Verificar cargos detectados e os modos já criados\n"
                "`!Funções` → Lista e explica todas as funções disponíveis\n"
                "`!Sobre` → Saiba mais sobre o ModEx e seu desenvolvedor\n\n"
                "Use `!Idioma` para trocar o idioma."
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="🗑️ Apagando mensagens anteriores para manter o canal limpo...")
    else:
        embed = discord.Embed(
            title="**📘 Setup Panel**",
            description=(
                "Welcome to the **ModEx configuration mode**. I'm here to help you **manage custom modes** on your server! Below are the main commands you can use:\n\n"
                "**Main Commands:**\n"
                "`!Create` → Starts the creation of a new custom mode\n"
                "`!Edit` → Starts editing an existing mode\n"
                "`!Check` → Check detected roles and created modes\n"
                "`!Functions` → Lists and explains all available functions\n"
                "`!About` → Learn more about ModEx and its developer\n\n"
                "Use `!Language` to change the language."
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="🗑️ Deleting previous messages to keep the channel clean...")
    return embed

def get_about_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="**🤖 Sobre o ModEx**",
            description=(
                "O **ModEx** começou como um projeto simples de **aprendizado em Python**, criado por **Gleidson Gonzaga**, mais conhecido como **Zev Lonewolf**, com o objetivo de tornar seu servidor de RPG **mais versátil** — alternando facilmente entre um ambiente imersivo e outro mais casual.\n\n"
                "Na sua primeira versão, o bot já era capaz de **alternar entre dois modos** distintos, mas de forma **bastante limitada**. Desde então, Zev tem trabalhado com carinho para transformar o ModEx em algo **flexível e útil para qualquer servidor**.\n\n"
                "**🌟 Se quiser apoiar, siga o desenvolvedor ou dê uma estrela no projeto!**\n"
                "- [GitHub de Zev Lonewolf](https://github.com/Zev-Lonewolf)\n"
                "- [Repositório do ModEx](https://github.com/Zev-Lonewolf/ModEx_DiscordBot)"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="🔐 Psiu... já ouviu falar no comando !Dev?")
    else:
        embed = discord.Embed(
            title="**🤖 About ModEx**",
            description=(
                "**ModEx** started as a simple **Python learning project**, created by **Gleidson Gonzaga**, also known as **Zev Lonewolf**. It was designed to make his RPG server **more versatile** — allowing quick switches between an immersive setting and a more casual one.\n\n"
                "In its first version, the bot could already **toggle between two distinct modes**, but in a **very limited way**. Since then, Zev has been carefully evolving ModEx into something **flexible and useful for any server**.\n\n"
                "**🌟 If you'd like to support, follow the developer or star the project!**\n"
                "- [Zev Lonewolf’s GitHub](https://github.com/Zev-Lonewolf)\n"
                "- [ModEx GitHub Repository](https://github.com/Zev-Lonewolf/ModEx_DiscordBot)"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="🔐 Psst... have you tried the !Dev command?")
    return embed

def get_functions_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="⛔ Em Desenvolvimento!",
            description=(
                "Recurso em fase de criação. Como o projeto está sempre em expansão, "
                "a lista final de comandos para os usuários será listada em breve..."
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="💡 Outra alternativa é utilizar o `!help` nativo dos bots...")
    else:
        embed = discord.Embed(
            title="⛔ Under Development!",
            description=(
                "This feature is still being built. Since the project is always expanding, "
                "the final list of user commands will be listed soon..."
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="💡 You can also use the native `!help` command of bots...")
    return embed