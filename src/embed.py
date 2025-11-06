import discord
from utils.modos import carregar_modos
from idiomas import obter_idioma

def get_language_embed(language, guild):
    if language == "pt":
        embed = discord.Embed(
            title=f"**🌍 Seleção de Idioma | {guild.name}**",
            description=(
                "**Seja bem-vindo(a)!** Vamos configurar o idioma do seu bot. "
                "Para começar, **reaja abaixo** e escolha como o ModEx vai se comunicar com você. "
                "Ah, e relaxa — dá pra mudar quando quiser com o comando `!idioma`."
            ),
            color=discord.Color.blue()
        )
        embed.add_field(
            name="**🌐 Idiomas Disponíveis:**",
            value=(
                "> - *🇺🇸 **English***\n"
                "> - *🇧🇷 **Português (BR)***\n"
                "> - *🚧 **Em breve...***"
            ),
            inline=False
        )
        embed.set_footer(text="⚙️ Ajustando sotaque digital...")
    else:
        embed = discord.Embed(
            title=f"**🌍 Language Selection | {guild.name}**",
            description=(
                "**Welcome!** Let's set up your bot's language. "
                "To begin, **react below** and choose how ModEx will talk to you. "
                "No worries — you can change it anytime with the `!language` command."
            ),
            color=discord.Color.blue()
        )
        embed.add_field(
            name="**🌐 Available Languages:**",
            value=(
                "> - *🇺🇸 **English***\n"
                "> - *🇧🇷 **Português (BR)***\n"
                "> - *🚧 **Coming soon...***"
            ),
            inline=False
        )
        embed.set_footer(text="⚙️ Adjusting digital accent...")
    return embed

def get_greeting_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="**👋 Hey! Eu sou o ModEx!**",
            description=(
                "Prazer em te conhecer! Sou o **ModEx** (Modes Executer - ou Executador de Modos em Pt-BR), seu assistente pra **organizar e gerenciar seus modos personalizados** no servidor. "
                "Posso deixar tudo nos trinques — é só escolher por onde quer começar.\n\n"
                "🛠️ **Comandos Disponíveis:**\n"
                "> `!Setup` → Abre o painel inicial do ModEx\n"
                "> `!Idioma` → Reabre a seleção de idioma\n\n"
                "🌐 **Links Úteis:**\n"
                "> [📁 Repositório](https://github.com/Zev-Lonewolf/ModEx_DiscordBot)\n"
                "> [👤 GitHub do Criador](https://github.com/Zev-Lonewolf)\n"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="📦 Bibliotecas... ok | 🎭 Piadas ruins... confirmadas | 🔒 Dados... em segurança ✅")
    else:
        embed = discord.Embed(
            title="**👋 Hey! I'm ModEx!**",
            description=(
                "Nice to meet you! I'm **ModEx** (Execute Modes), your assistant for **organizing and managing your custom modes** on the server. "
                "I can keep everything neat and ready — just choose where you’d like to start.\n\n"
                "🛠️ **Available Commands:**\n"
                "> `!Setup` → Opens the ModEx main panel\n"
                "> `!Language` → Reopens the language selection\n\n"
                "🌐 **Useful Links:**\n"
                "> [📁 Repository](https://github.com/Zev-Lonewolf/ModEx_DiscordBot)\n"
                "> [👤 Creator’s GitHub](https://github.com/Zev-Lonewolf)\n"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="📦 Libraries... okay | 🎭 Bad jokes... confirmed | 🔒 Data... secure ✅")
    return embed

def get_setup_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="📘 **Painel de Configuração**",
            description=(
                "Bem-vindo ao **modo de configuração do ModEx!** "
                "Aqui você pode **criar, editar e organizar seus modos personalizados** com praticidade. "
                "Quer se aprofundar mais? Dê uma olhada nas funções disponíveis ou explore o bot através de seu repositório no GitHub!\n\n"
                "**Comandos Principais:**\n"
                "> `!Criar` → *Começa a criação de um novo modo personalizado.*\n"
                "> `!Editar` → *Abre a edição de um modo existente.*\n"
                "> `!Verificar` → *Mostra os cargos detectados e modos criados.*\n"
                "> `!Funções` → *Lista e explica todas as funções disponíveis.*\n"
                "> `!Sobre` → *Saiba mais sobre o ModEx e seu criador.*\n\n"
                "Use `!Idioma` para trocar o idioma a qualquer momento."
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="💡 Curiosidade: Apenas o dono e gerentes têm acesso completo aos canais!")
    else:
        embed = discord.Embed(
            title="📘 **Setup Panel**",
            description=(
                "Welcome to **ModEx setup mode!** "
                "Here you can **create, edit, and organize your custom modes** with ease. "
                "Want to dig deeper? Take a look at the available functions or explore the bot through its GitHub repository!\n\n"
                "**Main Commands:**\n"
                "> `!Create` → *Starts creating a new custom mode.*\n"
                "> `!Edit` → *Opens editing for an existing mode.*\n"
                "> `!Check` → *Shows detected roles and created modes.*\n"
                "> `!Functions` → *Lists and explains all available functions.*\n"
                "> `!About` → *Learn more about ModEx and its creator.*\n\n"
                "Use `!Language` to switch languages anytime."
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="💡 Fun fact: Only the owner and managers have full access to all channels!")
    return embed

def get_about_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="**🤖 Sobre o ModEx:**",
            description=(
                "_O projeto **ModEx** (codinome: Execute Modes) teve sua iniciativa durante a abertura do primeiro semestre de **Sistemas de Informação na UFMT**. Seu criador, **Gleidson G. Silva** — mais conhecido como **Zev** — percebeu que diversos servidores acumulavam muitos canais para milhares de funções diferentes._\n\n"
                "_A ideia inicial era usar **cargos** e **canais privados** para controlar o fluxo e a visualização dos temas/momentos do servidor. Entretanto, como nenhum outro bot fazia esse trabalho — ou apenas de forma manual — **Zev decidiu criar o ModEx** para **criar, editar, alternar e sair de diversos 'modos'** de maneira automática._\n\n"
                "_Hoje, o projeto conta com a ajuda de **Noa** para **melhorias, expansão e correções** nas linhas de código, garantindo que o ModEx continue **funcionando e evoluindo constantemente**._\n\n"
                "**🌟 Se quiser apoiar, siga o desenvolvedor e dê uma estrela no projeto!**\n"
                "- [GitHub de Zev Lonewolf](https://github.com/Zev-Lonewolf)\n"
                "- [Repositório do ModEx](https://github.com/Zev-Lonewolf/ModEx_DiscordBot)"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="🔐 Sabia que o ModEx começou em um i3 de 2ª e 4GB de RAM?")
    else:
        embed = discord.Embed(
            title="**🤖 About ModEx:**",
            description=(
                "_The **ModEx** project (codename: Execute Modes) started during the first semester of **Information Systems at UFMT**. Its creator, **Gleidson G. Silva**, better known as **Zev**, noticed that many servers were cluttered with channels for countless different functions._\n\n"
                "_The initial idea was to use **roles** and **private channels** to control the flow and visibility of server themes/moments. However, since no other bot did this — or only did it manually — **Zev decided to create ModEx** to **create, edit, switch, and exit various 'modes'** automatically with just a few clicks._\n\n"
                "_Today, the project counts on the help of **Noa** for **improvements, expansions, and code fixes**, ensuring that ModEx keeps **running smoothly and evolving continuously**._\n\n"
                "**🌟 If you'd like to support, follow the developer and star the project!**\n"
                "- [Zev Lonewolf’s GitHub](https://github.com/Zev-Lonewolf)\n"
                "- [ModEx GitHub Repository](https://github.com/Zev-Lonewolf/ModEx_DiscordBot)"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="🔐 Did you know ModEx started on a 2nd gen i3 with 4GB of RAM?")
    return embed

def get_functions_embed(language, guild):
    if language == "pt":
        embed = discord.Embed(
            title="🧭 Lista de Comandos do ModEx",
            description=(
                "Aqui está um resumo dos comandos disponíveis. O ModEx está sempre recebendo novidades, então fique de olho para futuras atualizações! ✨\n\n"
                f"**🗃️ Servidor:** {guild.name}\n"
                "> Criar      → Inicia a criação de um novo modo\n"
                "> Editar      → Edita um modo existente\n"
                "> Funções     → Exibe esta lista de comandos\n"
                "> Help        → Mostra a ajuda nativa do Discord\n"
                "> Idioma      → Reabre a seleção de idioma\n"
                "> Limpar      → Limpa mensagens do bot e do usuário\n"
                "> Log         → Mostra o status dos logs\n"
                "> Setup       → Abre o painel inicial do ModEx\n"
                "> Sobre       → Mostra informações sobre o bot\n"
                "> Verificar   → Lista cargos e modos do servidor\n\n"
                "💡 Dica: Use `!help comando` para saber mais sobre um comando específico."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="📘 O ModEx está em constante evolução — mais funções virão em breve!")
    else:
        embed = discord.Embed(
            title="🧭 ModEx Command List",
            description=(
                "Here’s a quick overview of the available commands. ModEx is constantly evolving, so stay tuned for new features! ✨\n\n"
                f"**🗃️ Servidor:** {guild.name}\n"
                "> Create       → Starts creating a new mode\n"
                "> Edit      → Edits an existing mode\n"
                "> Functions     → Displays this command list\n"
                "> Help        → Shows Discord’s native help message\n"
                "> Language      → Reopens the language selection\n"
                "> Clean      → Clears bot and user messages\n"
                "> Log         → Shows log status\n"
                "> Setup       → Opens the ModEx main panel\n"
                "> About       → Shows information about the bot\n"
                "> Check   → Lists server roles and modes\n\n"
                "💡 Tip: Use `!help command` for more info on a specific command."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="📘 ModEx keeps evolving — new features coming soon!")
    return embed

def get_roles_embed(roles, language, guild):
    dados_modos = carregar_modos()
    guild_id = str(guild.id)
    guild_name = str(guild.name)
    modos_servidor = dados_modos.get(guild_id, {}).get("modos", {})
    filtered_roles = []
    for role in roles:
        if isinstance(role, discord.Role) and role.name != "@everyone":
            filtered_roles.append(role)
        elif isinstance(role, (str, int)):
            filtered_roles.append(str(role))

    if language == "pt":
        cargos_texto = (
            "\n".join([
                f"> - **{getattr(role, 'name', str(role))}** (`{getattr(role, 'id', 'N/A')}`)"
                for role in filtered_roles
            ])
            if filtered_roles else "> *🔍 Nenhum cargo encontrado. Crie um cargo para começar a atribuí-lo aos modos.*"
        )
        modos_texto = (
            "\n".join([
                f"> - **{modo['nome']}**"
                for modo in modos_servidor.values()
            ])
            if modos_servidor else "> *💡 Nenhum modo criado ainda. Use o comando !Criar para começar.*"
        )
        embed = discord.Embed(
            title="📌 Cargos e Modos do Servidor",
            description=f"**Servidor:** {guild_name} (`{guild_id}`)\n",
            color=discord.Color.blurple()
        )
        embed.add_field(name="💼 **Cargos encontrados:**", value=cargos_texto, inline=False)
        embed.add_field(name="🧩 **Modos disponíveis:**", value=modos_texto, inline=False)
        embed.set_footer(text="📇 Organização é poder — e o ModEx entende disso!")
    else:
        roles_text = (
            "\n".join([
                f"> - **{getattr(role, 'name', str(role))}** (`{getattr(role, 'id', 'N/A')}`)"
                for role in filtered_roles
            ])
            if filtered_roles else "> *🔍 No roles found. Create a role to start assigning it to modes.*"
        )
        modes_text = (
            "\n".join([
                f"> - **{modo['nome']}**"
                for modo in modos_servidor.values()
            ])
            if modos_servidor else "> *💡 No modes created yet. Use the !Create command to start.*"
        )
        embed = discord.Embed(
            title="📌 Server Roles and Modes",
            description=f"**Server:** {guild_name} (`{guild_id}`)\n",
            color=discord.Color.blurple()
        )
        embed.add_field(name="💼 **Roles found:**", value=roles_text, inline=False)
        embed.add_field(name="🧩 **Available Modes:**", value=modes_text, inline=False)
        embed.set_footer(text="📇 Organization is power — and ModEx knows that!")
    return embed

def get_edit_embed(server_id, language):
    dados = carregar_modos()
    server_id = str(server_id)
    modos = dados.get(server_id, {}).get("modos", {})

    if language == "pt":
        titulo = "📝 **Editar Modos Existentes**"
        descricao = (
            "➡️ Aqui estão os modos já criados no seu servidor. Para editar um modo, digite o **nome** dele usando `#nomedomodo`.\n\n"
            "⚙️ **Aviso importante:** ao iniciar a edição, o modo é **redefinido do zero**, "
            "como se estivesse sendo criado novamente. "
            "Se o processo for interrompido, o **modo de segurança entra em ação**, "
            "definindo os parâmetros `em_edicao` e `finalizado` como **False** — "
            "fazendo com que o modo seja **apagado automaticamente do banco de dados**.\n\n"
            "Caso não veja o modo desejado, certifique-se de que ele foi criado corretamente com `!Criar`."
        )
        rodape = "🗃️ Dica: evite encerrar a edição antes de finalizá-la!"
    else:
        titulo = "📝 **Edit Existing Modes**"
        descricao = (
            "➡️ Here are the modes already created on your server. To edit a mode, type its **name** using `#modename`.\n\n"
            "⚙️ **Important note:** when editing begins, the mode is **reset from scratch**, "
            "as if it were being created again. "
            "If the process is interrupted, the **safety system kicks in**, "
            "setting both `in_edit` and `finished` to **False** — "
            "which makes the mode **automatically deleted from the database**.\n\n"
            "If you don’t see the desired mode, make sure it was properly created using `!Create`."
        )
        rodape = "🗃️ Tip: avoid closing the editing process before finishing it!"

    if modos:
        lista_modos = "\n".join(
            [f"> - **{modo['nome']}**" for modo in modos.values() if "nome" in modo]
        )
    else:
        lista_modos = (
            "> ❌ Nenhum modo encontrado." if language == "pt"
            else "> ❌ No modes found."
        )

    embed = discord.Embed(title=titulo, description=descricao, color=discord.Color.orange())
    embed.add_field(
        name="**🧩 Modos disponíveis:**" if language == "pt" else "**🧩 Available modes:**",
        value=lista_modos,
        inline=False,
    )
    embed.set_footer(text=rodape)
    return embed

def get_invalid_mode_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="❌ Modo não encontrado",
            description=(
                "O nome informado **não corresponde a nenhum modo existente**. "
                "Confira **a lista no embed anterior** e tente novamente usando `#nomedomodo`.\n\n"
                "_Dica: modos cancelados são removidos automaticamente do banco de dados._"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="Curiosidade: o primeiro bug foi um inseto real preso num computador 🪲")
    else:
        embed = discord.Embed(
            title="❌ Mode not found",
            description=(
                "The name provided **doesn’t match any existing mode**. "
                "Check **the list in the previous embed** and try again using `#modename`.\n\n"
                "_Tip: canceled modes are automatically removed from the database._"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="Fun fact: the first bug was a real insect stuck in a computer 🪲")
    return embed

def get_mode_selected_embed(mode_name, language):
    if language == "pt":
        embed = discord.Embed(
            title="✅ Modo selecionado!",
            description=(
                f"O modo **{mode_name}** foi encontrado e **aberto para edição**. "
                "Ao clicar em ✅ o modo será **reiniciado**, e a edição começará do zero — "
                "a partir desse ponto, **evite sair antes de finalizar** para não perder os dados.\n\n"
                "➡️ Continue seguindo as etapas normalmente para **atualizar suas configurações**."
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="💾 Curiosidade: o primeiro HD da IBM pesava mais de uma tonelada!")
    else:
        embed = discord.Embed(
            title="✅ Mode selected!",
            description=(
                f"The mode **{mode_name}** was found and **opened for editing**. "
                "When you click ✅, the mode will be **reset**, starting fresh — "
                "from that point, **avoid leaving before finishing** to prevent data loss.\n\n"
                "➡️ Continue following the steps to **update its settings**."
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="💾 Fun fact: IBM’s first hard drive weighed over a ton!")
    return embed

def get_create_embed(guild):
    language = obter_idioma(guild.id)
    roles = [r for r in guild.roles if not r.is_default() and r.name != "@everyone"]

    if language == "pt":
        titulo = "**ℹ️ Informações Iniciais**"
        descricao = (
            "Olá! Seja bem-vindo(a) ao **modo de criação**. Se este for seu **primeiro modo**, "
            "recomendamos seguir os passos abaixo com atenção:\n\n"
            "**1.** Crie ao menos um **modo de recepção** — ele é o cargo atribuído automaticamente "
            "a todos os novos membros do servidor. É possível ter **apenas um modo de recepção ativo** por vez.\n"
            "**2.** O bot, por padrão, é convidado como **administrador**. Caso não esteja, conceda a ele o cargo adequado "
            "para evitar erros de permissão.\n"
            "**3.** Os dados coletados são apenas **informações internas** como IDs, nomes e configurações de modos. "
            "Nenhum dado pessoal é armazenado. Em caso de dúvida, consulte o repositório através do comando `!sobre`.\n"
            "**4.** O funcionamento é simples: o ModEx **alterna cargos** dos membros para exibir os canais "
            "privados correspondentes ao modo ativo.\n"
            "**5.** Após configurar tudo, teste criando um modo temporário e veja se o sistema aplica os cargos corretamente ao reagir.\n"
            "**6.** Se algo não estiver funcionando corretamente, use o comando `!log` para verificar detalhes — "
            "no menu principal há mais informações sobre ele.\n\n"
            "⚙️ *Lembre-se: os modos podem ser editados ou removidos a qualquer momento usando os comandos disponíveis.*"
        )
        rodape = "💡 Curiosidade: o primeiro emoji foi criado em 1999, no Japão!"
        cargos_texto = "\n".join([f"- **{role.name}**" for role in roles]) if roles else \
            "❌ Nenhum cargo encontrado. Crie um cargo para começar a atribuí-lo aos modos."
    else:
        titulo = "**ℹ️ Initial Info**"
        descricao = (
            "Hi there! Welcome to **Creation Mode**. If this is your **first time**, "
            "we recommend following these steps carefully:\n\n"
            "**1.** Create at least one **welcome mode** — this role is automatically assigned "
            "to everyone who joins the server. You can have **only one active welcome mode** at a time.\n"
            "**2.** The bot is usually invited as an **administrator**. If it isn’t, make sure it has the proper role "
            "to prevent permission issues.\n"
            "**3.** The collected data is limited to **internal information** such as IDs, mode names, and settings. "
            "No personal data is stored. If in doubt, check the repository through the `!about` command.\n"
            "**4.** The system works simply: ModEx **switches member roles** to display private channels "
            "linked to the active mode.\n"
            "**5.** Once setup is done, test it by creating a temporary mode and verifying that roles are applied correctly when reacting.\n"
            "**6.** If something isn’t working properly, use the `!log` command to check for details — "
            "you’ll find more info about it in the main menu.\n\n"
            "⚙️ *Remember: modes can be edited or deleted at any time using the available commands.*"
        )
        rodape = "💡 Fun fact: the first emoji was created in 1999, in Japan!"
        cargos_texto = "\n".join([f"- **{role.name}**" for role in roles]) if roles else \
            "❌ No roles found. Create a role to start assigning it to modes."

    embed = discord.Embed(title=titulo, description=descricao, color=discord.Color.yellow())
    embed.add_field(
        name="**Cargos encontrados:**" if language == "pt" else "**Detected Roles:**",
        value=cargos_texto,
        inline=False
    )
    embed.set_footer(text=rodape)
    return embed

def get_initial_create_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="🚧 Criação de Modo (etapa 1 de 5)",
            description=(
                "Vamos começar do zero! Qual será o **nome** do seu modo? Esse nome será usado para identificar o modo nas próximas etapas.\n\n"
                "📌 _Exemplos:_ **Eventos**, **Staff**, **AcessoVIP**...\n"
                "✍️ _Responda com:_ `#NomeDoModo`\n\n"
                "⚠️ Evite nomes longos ou cheios de símbolos — quanto mais simples, melhor!"
            ),
            color=discord.Color.teal()
        )
        embed.set_footer(text="Curiosidade: o primeiro computador pessoal custava mais que um carro novo! 🚗")
    else:
        embed = discord.Embed(
            title="🚧 Mode Creation (step 1 of 5)",
            description=(
                "Let's start from scratch! What will be the **name** of your mode? This name will be used to identify it in the next steps.\n\n"
                "📌 _Examples:_ **Events**, **Staff**, **VIPAccess**...\n"
                "✍️ _Reply with:_ `#ModeName`\n\n"
                "⚠️ Avoid long names or strange symbols — the simpler, the better!"
            ),
            color=discord.Color.teal()
        )
        embed.set_footer(text="Fun fact: the first personal computer cost more than a brand-new car! 🚗")
    return embed

def get_name_saved_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="✅ Nome salvo com sucesso!",
            description=(
                "🎉 Perfeito! O nome do modo foi **registrado com sucesso**. "
                "Agora siga para a **próxima etapa** e continue a configuração."
            ),
            color=discord.Color.dark_green()
        )
        embed.set_footer(text="Dica: nomes simples facilitam identificar os modos depois. 😉")
    else:
        embed = discord.Embed(
            title="✅ Name saved successfully!",
            description=(
                "🎉 Great! The mode name has been **successfully registered**. "
                "Now move on to the **next step** and keep setting things up."
            ),
            color=discord.Color.dark_green()
        )
        embed.set_footer(text="Tip: simple names make it easier to find modes later. 😉")
    return embed

def get_invalid_name_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="❌ Nome inválido!",
            description=(
                "⚠️ O nome do modo deve ter entre **2 e 15 caracteres**. "
                "Escolha um nome mais curto e tente novamente!"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="Curiosidade: o primeiro domínio registrado na internet foi symbolics.com 💻")
    else:
        embed = discord.Embed(
            title="❌ Invalid name!",
            description=(
                "⚠️ The mode name must be between **2 and 15 characters**. "
                "Pick a shorter one and try again!"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="Fun fact: the first domain ever registered was symbolics.com 💻")
    return embed

def get_name_conflict_embed(language, nome_modo):
    if language == "pt":
        embed = discord.Embed(
            title="⚠️ Conflito de nome",
            description=(
                f"🚧 Já existe um modo chamado **{nome_modo}**. Volte e escolha um **nome diferente** ou **edite o outro modo** para liberar este nome."
            ),
            color=discord.Color.orange()
        )
        embed.set_footer(text="Curiosidade: o primeiro computador portátil pesava mais de 10 kg! 💼")
    else:
        embed = discord.Embed(
            title="⚠️ Name conflict",
            description=(
                f"🚧 A mode named **{nome_modo}** already exists. Go back and choose a **different name** or **edit the other mode** to free it up."
            ),
            color=discord.Color.orange()
        )
        embed.set_footer(text="Fun fact: the first portable computer weighed over 10 kg! 💼")
    return embed

def get_role_select_embed(language, roles):
    filtered_roles = [role for role in roles if role.name != "@everyone"]

    if language == "pt":
        titulo = "**🚧 Criação de Modo (etapa 2 de 5)**"
        descricao = (
            "📌 Mencione **um ou mais cargos** ou digite o nome exato deles. "
            "Esses serão os cargos atribuídos ao modo.\n"
            "Ex: `@Staff`, `@Vips`, `@Adms`..."
        )
        rodape = "💡 Curiosidade: o primeiro sistema de permissões em computadores surgiu nos anos 60!"
        cargos_texto = "\n".join([f"- **{role.name}**" for role in filtered_roles]) if filtered_roles else "> ❌ Nenhum cargo encontrado. Crie um cargo para continuar."
    else:
        titulo = "**🚧 Mode Creation (step 2 of 5)**"
        descricao = (
            "📌 Mention **one or more roles** or type their exact names. "
            "These will be the roles assigned to the mode.\n"
            "Ex: `@Staff`, `@Vips`, `@Admins`..."
        )
        rodape = "💡 Fun fact: the first computer permissions system appeared in the 1960s!"
        cargos_texto = "\n".join([f"- **{role.name}**" for role in filtered_roles]) if filtered_roles else "> ❌ No roles found. Create a role to continue."

    embed = discord.Embed(title=titulo, description=descricao, color=discord.Color.green())
    embed.add_field(
        name="**Cargos disponíveis:**" if language == "pt" else "**Available roles:**",
        value=cargos_texto,
        inline=False
    )
    embed.set_footer(text=rodape)
    return embed

def get_role_saved_embed(language, role_name):
    if language == "pt":
        embed = discord.Embed(
            title="✅ Cargo selecionado!",
            description=(
                f"🎉 O cargo **{role_name}** foi atribuído ao modo com sucesso. "
                "Agora siga para a próxima etapa e continue configurando o modo."
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="💡 Dica: você pode atribuir mais de um cargo a um modo se necessário.")
    else:
        embed = discord.Embed(
            title="✅ Role selected!",
            description=(
                f"🎉 The role **{role_name}** was successfully assigned to the mode. "
                "Now move on to the next step to keep setting up the mode."
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="💡 Tip: you can assign more than one role to a mode if needed.")
    return embed

def get_invalid_role_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="❌ Cargo inválido",
            description="⚠️ Cargo não encontrado. Por favor, retorne e mencione o cargo corretamente.",
            color=discord.Color.red()
        )
        embed.set_footer(text="💡 Curiosidade: o teclado QWERTY foi feito para evitar travamentos!")
    else:
        embed = discord.Embed(
            title="❌ Invalid role",
            description="⚠️ Role not found. Please go back and enter the position correctly.",
            color=discord.Color.red()
        )
        embed.set_footer(text="💡 Fun fact: the QWERTY keyboard was made to prevent jams!")
    return embed

#PAREI AQUI, CONTINUAREI AMANHÃ
def get_channel_select_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="🚧 Criação de Modo (etapa 3 de 5)",
            description=(
                "Agora escolha quais **canais de texto, voz ou categorias** ficarão **privados** "
                "para este cargo/modo.\n\n"
                "📌 _Mencione o canal/categoria ou digite o nome exato._\n"
                "⚠️ Você precisa ter permissão para gerenciar canais."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Mencione ou digite o nome do canal/categoria.")
    else:
        embed = discord.Embed(
            title="🚧 Mode Creation (step 3 of 5)",
            description=(
                "Now choose which **text channels, voice channels, or categories** will be **private** "
                "for this role/mode.\n\n"
                "📌 _Mention the channel/category or type the exact name._\n"
                "⚠️ You need permission to manage channels."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Mention or type the name of the channel/category.")
    return embed

def get_channel_saved_embed(language, channel_name):
    if language == "pt":
        embed = discord.Embed(
            title="✅ Canal/Categoria selecionado!",
            description=f"O canal/categoria **{channel_name}** foi atribuído ao modo com sucesso.",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="✅ Channel/Category selected!",
            description=f"The channel/category **{channel_name}** was successfully assigned to the mode.",
            color=discord.Color.green()
        )
    return embed

def get_invalid_channel_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="❌ Canal/Categoria inválido",
            description="Canal ou categoria não encontrado(a). "
                        "Por favor, mencione corretamente ou digite o nome exato.",
            color=discord.Color.red()
        )
    else:
        embed = discord.Embed(
            title="❌ Invalid Channel/Category",
            description="Channel or category not found. "
                        "Please mention it correctly or type the exact name.",
            color=discord.Color.red()
        )
    return embed

def get_channel_conflict_warning_embed(language, conflict_channels, modo_origem=""):
    canais_str = ", ".join([f"<#{cid}>" for cid in conflict_channels])

    if language == "pt":
        embed = discord.Embed(
            title="⚠️ Conflito de Canais Detectado",
            description=(
                f"Os seguintes canais já estão associados a **outro modo**: {canais_str}.\n\n"
                "👉 Para continuar, você deve **escolher outros canais** ou **removê-los do modo atual** antes de prosseguir.\n"
                + (f"\n🔗 Atualmente pertencem ao modo: **{modo_origem}**" if modo_origem else "")
            ),
            color=discord.Color.orange()
        )
        embed.set_footer(text="🚫 Um canal só pode pertencer a um modo por vez.")
    else:
        embed = discord.Embed(
            title="⚠️ Channel Conflict Detected",
            description=(
                f"The following channels are already associated with **another mode**: {canais_str}.\n\n"
                "👉 To proceed, you must **choose different channels** or **remove them from the current mode** first.\n"
                + (f"\n🔗 Currently assigned to mode: **{modo_origem}**" if modo_origem else "")
            ),
            color=discord.Color.orange()
        )
        embed.set_footer(text="🚫 A channel can only belong to one mode at a time.")
    return embed

def get_channel_removed_warning_embed(language, removed_channels):
    canais_str = ", ".join([f"<#{cid}>" for cid in removed_channels])

    if language == "pt":
        embed = discord.Embed(
            title="❌ Canais Removidos Detectados",
            description=(
                f"Os seguintes canais não existem mais no servidor: {canais_str}.\n\n"
                "👉 Para continuar, você deve **atualizar o modo** e remover os canais que foram apagados."
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="⚠️ Canais apagados precisam ser substituídos para evitar erros.")
    else:
        embed = discord.Embed(
            title="❌ Removed Channels Detected",
            description=(
                f"The following channels no longer exist in the server: {canais_str}.\n\n"
                "👉 To continue, you must **update the mode** and remove the deleted channels."
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="⚠️ Deleted channels must be replaced to avoid errors.")
    return embed


def get_reception_mode_question_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="🚧 Criação de Modo (etapa 4 de 5)",
            description=(
                "Deseja atribuir este cargo como **modo de recepção**?\n\n"
                "📌 Apenas **um modo** pode estar configurado como recepção por vez.\n\n"
                "✅ Clique em **Sim** para atribuir.\n"
                "❌ Clique em **Não** para pular."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Um servidor só pode ter um modo de recepção ativo.")
    else:
        embed = discord.Embed(
            title="🚧 Mode Creation (step 4 of 5)",
            description=(
                "Do you want to assign this role as the **reception mode**?\n\n"
                "📌 Only **one mode** can be configured as reception at a time.\n\n"
                "✅ Click **Yes** to assign.\n"
                "❌ Click **No** to skip."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="A server can only have one reception mode active.")
    return embed

def get_reception_assigned_embed(language, role_name):
    if language == "pt":
        embed = discord.Embed(
            title="✅ Modo de recepção atribuído",
            description=f"O cargo **{role_name}** agora é o modo de recepção do servidor.",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="✅ Reception mode assigned",
            description=f"The role **{role_name}** is now the reception mode of the server.",
            color=discord.Color.green()
        )
    return embed

def get_reception_replaced_embed(language, old_role, new_role):
    if language == "pt":
        embed = discord.Embed(
            title="⚠️ Modo de recepção atualizado!",
            description=(
                f"O cargo **{old_role}** não é mais o modo de recepção.\n"
                f"O cargo **{new_role}** foi atribuído no lugar dele."
            ),
            color=discord.Color.orange()
        )
    else:
        embed = discord.Embed(
            title="⚠️ Reception mode updated!",
            description=(
                f"The role **{old_role}** is no longer the reception mode.\n"
                f"The role **{new_role}** has been assigned instead."
            ),
            color=discord.Color.orange()
        )
    return embed

def get_reception_error_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="❌ Erro ao atribuir modo de recepção",
            description=(
                "Ocorreu um erro ao tentar configurar este cargo como modo de recepção.\n"
                "👉 Verifique se o bot tem permissões suficientes (gerenciar canais/cargos)."
            ),
            color=discord.Color.red()
        )
    else:
        embed = discord.Embed(
            title="❌ Error assigning reception mode",
            description=(
                "An error occurred while trying to set this role as the reception mode.\n"
                "👉 Make sure the bot has sufficient permissions (manage channels/roles)."
            ),
            color=discord.Color.red()
        )
    return embed

def get_reception_skipped_embed(language, role_name):
    if language == "pt":
        embed = discord.Embed(
            title="ℹ️ Cargo não definido como recepção",
            description=f"O cargo **{role_name}** foi configurado, mas não será usado como recepção.",
            color=discord.Color.blue()
        )
    else:
        embed = discord.Embed(
            title="ℹ️ Role not set as reception",
            description=f"The role **{role_name}** has been configured, but will not be used as reception.",
            color=discord.Color.blue()
        )
    return embed

def get_finish_mode_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="✅ Criação de Modo finalizada",
            description="O modo foi configurado com sucesso! 🎉",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="✅ Mode creation finished",
            description="The mode has been successfully configured! 🎉",
            color=discord.Color.green()
        )
    return embed

def get_log_info_embed(language):
    if language == "pt":
        titulo = "**ℹ️ Aviso sobre o Modo Log**"
        descricao = (
            "Olá! Antes de avançar e ativar o modo log, queremos garantir que você compreenda de forma clara como ele funciona, "
            "quais são suas finalidades e as responsabilidades envolvidas.\n\n"
            "O modo log foi desenvolvido para registrar eventos importantes do bot, como comandos executados, reações, mensagens enviadas pelo bot, "
            "e alterações de estado dos modos. Estes registros são armazenados de forma segura e estruturada, usando formatos como `[DEBUG]` e `[INFO]`, "
            "permitindo identificar, monitorar e corrigir eventuais problemas no funcionamento do sistema.\n\n"
            "🔒 **Privacidade e acesso:**\n"
            "- Atualmente, apenas o criador do bot tem acesso aos logs.\n"
            "- No futuro, planejamos permitir que o dono ou gerente do servidor visualize os registros e possa reportar informações ao criador. "
            "Cada registro será separado por servidor, facilitando a identificação de bugs e contribuições para melhorias.\n"
            "- As mensagens apagadas registradas **não são de usuários**, mas sim ações do bot. "
            "Não coletamos nenhum dado ou mensagem pessoal dos membros, apenas entradas de nomes, cargos e IDs necessários para criação e gerenciamento dos modos.\n\n"
            "🛠️ **Finalidade dos registros:**\n"
            "- Os logs servem para **melhorar a confiabilidade do bot**, **identificar e corrigir bugs**, e **monitorar o desempenho dos modos**.\n"
            "- O monitoramento dos modos é feito através de registros em JSON que armazenam informações sobre cada modo. "
            "Não coletamos dados sensíveis ou pessoais.\n"
            "- A coleta de logs **só é ativada em momentos cruciais**, quando erros ou falhas ocorrem. Ela **não é ativada por padrão**, nem recomendamos que seja, para não sobrecarregar os arquivos.\n\n"
            "⚖️ **Responsabilidade do usuário e do criador:**\n"
            "Ao prosseguir e ativar o modo log, você concorda com a coleta e uso destes registros conforme explicado acima. "
            "O criador do bot assume total responsabilidade sobre o sistema de logs, garantindo que ele será utilizado exclusivamente para fins técnicos, administrativos e de manutenção do bot. "
            "Isso inclui responder por problemas decorrentes de uso indevido, armazenamento seguro dos dados e transparência sobre o que é registrado. "
            "O usuário concorda em utilizar o modo log de acordo com estas condições, entendendo os limites e a finalidade da coleta.\n\n"
            "❓ Para dúvidas ou mais informações sobre os registros, funcionalidades do bot ou políticas de privacidade, utilize `!Sobre` ou `!About` "
            "e consulte o repositório ou perfil do criador."
        )
        rodape = "🗃️ ModEx - Seus modos, sua segurança!"
    else:
        titulo = "**ℹ️ Log Mode Notice**"
        descricao = (
            "Hello! Before proceeding and activating log mode, we want to ensure you clearly understand how it works, its purposes, and the responsibilities involved.\n\n"
            "The log mode records important bot events, such as executed commands, reactions, messages sent by the bot, and mode state changes. "
            "These logs are securely stored and structured using formats like `[DEBUG]` and `[INFO]`, allowing us to identify, monitor, and efficiently fix any issues.\n\n"
            "🔒 **Privacy and access:**\n"
            "- Currently, only the bot creator has access to the logs.\n"
            "- In the future, we plan to allow server owners or managers to view the logs and report information to the creator. "
            "Logs will be separated by server to facilitate bug identification and future improvements.\n"
            "- Deleted messages recorded are **bot actions only**, not user messages. "
            "We do not collect any personal or user messages, only names, roles, and IDs necessary for mode creation and management.\n\n"
            "🛠️ **Purpose of logs:**\n"
            "- Logs are used to **improve bot reliability**, **identify and fix bugs**, and **monitor mode performance**.\n"
            "- Mode monitoring is done via JSON records storing information about each mode. No sensitive or personal data is collected.\n"
            "- Log collection is **activated only in crucial moments** when errors occur. It is **not enabled by default**, nor recommended to be, to avoid file overload.\n\n"
            "⚖️ **User and creator responsibility:**\n"
            "By proceeding and activating log mode, you agree with the collection and use of these logs as described above. "
            "The bot creator assumes full responsibility for the logging system, ensuring it is used exclusively for technical, administrative, and maintenance purposes. "
            "This includes accountability for improper use, secure data storage, and transparency regarding what is logged. "
            "Users agree to use log mode under these conditions, understanding the scope and purpose of the data collection.\n\n"
            "❓ For questions or more information about logs, bot functionality, or privacy policies, use `!About` and check the creator's repository/profile."
        )
        rodape = "🗃️ ModEx - Your modes, your security!"

    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=discord.Color.orange()
    )
    embed.set_footer(text=rodape)
    return embed

def get_log_confirm_embed(language, debug_logs):

    status_text_pt = "Ativado ✅" if debug_logs else "Desativado ❌"
    status_text_en = "Activated ✅" if debug_logs else "Deactivated ❌"

    if language == "pt":
        titulo = "**❓ Confirmação de Modo Log**"
        descricao = (
            f"O modo Log do servidor está atualmente **{status_text_pt}**.\n\n"
            "💡 *Aviso importante:* O modo Log **não deve ser ativado o tempo todo**. "
            "Ele serve como uma ferramenta de suporte para momentos críticos, quando o bot apresentar algum bug, travamento ou comportamento inesperado "
            "que impeça seu funcionamento correto. Ativando o log nesses momentos, você ajuda o criador a identificar o problema de forma mais rápida e precisa.\n\n"
            "⚙️ *Recomendações de uso:*\n"
            "1️⃣ Ative o modo Log ✅ somente quando necessário.\n"
            "2️⃣ Reproduza os passos que causaram o bug ou erro, para que o sistema registre tudo corretamente.\n"
            "3️⃣ Após reproduzir o problema, **desative o modo Log** ❌ para evitar sobrecarga de arquivos e registros desnecessários.\n"
            "4️⃣ Caso o bot trave ou impeça de usar os botões de navegação até chegar no menu de desativação do Log, utilize o comando `!log`. "
            "Isso vai levá-lo direto para a tela de configuração do modo Log, permitindo desativar os registros com segurança.\n\n"
            "Deseja alterar o estado do modo Log?\n"
            "Reaja com:\n"
            "✅ para **ativar** o modo Log\n"
            "❌ para **desativar** o modo Log"
        )
        rodape = "🗃️ ModEx - Seus modos, sua segurança!"
    else:
        titulo = "**❓ Log Mode Confirmation**"
        descricao = (
            f"The server's Log Mode is currently **{status_text_en}**.\n\n"
            "💡 *Important notice:* Log Mode **should not be enabled all the time**. "
            "It is a support tool for critical moments, when the bot encounters a bug, freeze, or unexpected behavior "
            "that prevents it from functioning correctly. Activating logs in these situations helps the creator identify the problem faster and more accurately.\n\n"
            "⚙️ *Recommended procedure:*\n"
            "1️⃣ Activate Log Mode ✅ only when necessary.\n"
            "2️⃣ Reproduce the steps that caused the bug or error, so the system can record all events properly.\n"
            "3️⃣ After reproducing the issue, **deactivate Log Mode** ❌ to avoid file overload and unnecessary records.\n"
            "4️⃣ If the bot freezes or prevents you from using navigation buttons to reach the Log deactivation menu, use the `!log` command. "
            "This will take you directly to the Log configuration screen, allowing you to safely disable logging.\n\n"
            "Do you want to change the Log Mode status?\n"
            "React with:\n"
            "✅ to **activate** Log Mode\n"
            "❌ to **deactivate** Log Mode"
        )
        rodape = "🗃️ ModEx - Your modes, your security!"

    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=discord.Color.blue()
    )
    embed.set_footer(text=rodape)
    return embed

def get_log_activated_embed(language):

    repo_link = "https://github.com/Zev-Lonewolf/ModEx_DiscordBot"
    
    if language == "pt":
        titulo = "**✅ Modo Log Ativado**"
        descricao = (
            "O modo Log foi ativado! 🫂\n\n"
            "Obrigado por ajudar e contribuir para a identificação e correção de possíveis bugs ou erros do bot. "
            "Em breve o problema será analisado e corrigido, então tenha paciência, uma hora o dev vai perceber o erro 😉.\n\n"
            "P.S.: Se o bug estiver demorando e você suspeitar que o dev ainda não viu o erro, vá ao repositório [clicando aqui](" + repo_link + ") e abra um issue relatando-o! "
            "Se preferir, você também pode criar um pull request e ajudar diretamente com a correção. Toda ajuda é muito bem-vinda! 😄"
        )
        rodape = "Dica: Lembre-se de desativar o modo Log após reproduzir o bug usando o comando !log."
    else:
        titulo = "**✅ Log Mode Activated**"
        descricao = (
            "Log Mode has been activated! 🫂\n\n"
            "Thank you for helping and contributing to identifying and fixing possible bugs or errors in the bot. "
            "Soon the issue will be reviewed and fixed, so be patient — the dev will eventually spot it 😉.\n\n"
            "P.S.: If the bug seems to be taking too long and you suspect the dev hasn’t seen it yet, check the repository [here](" + repo_link + ") and open an issue! "
            "Alternatively, you can create a pull request to help fix it directly. Any contribution is very welcome! 😄"
        )
        rodape = "Tip: Remember to deactivate Log Mode after reproducing the bug using the !log command."

    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=discord.Color.green()
    )
    embed.set_footer(text=rodape)
    return embed

def get_log_deactivated_embed(language):

    if language == "pt":
        titulo = "**❌ Modo Log Desativado**"
        descricao = (
            "O modo Log do servidor foi **desativado com sucesso**! 🎊\n\n"
            "Muito obrigado por contribuir para a identificação de possíveis bugs ou problemas. 🙏💻\n"
            "Os registros agora foram pausados, e o bot continuará funcionando normalmente.\n\n"
            "💡 *Dica:* Se você quiser colaborar ainda mais, pode abrir um **issue** ou criar um **pull request** no repositório [clicando aqui](https://github.com/Zev-Lonewolf/ModEx_DiscordBot) para reportar ou ajudar a corrigir o erro. Toda ajuda é super bem-vinda! 🌟"
        )
        rodape = "🗃️ ModEx - Agradecemos sua colaboração e paciência!"
    else:
        titulo = "**❌ Log Mode Deactivated**"
        descricao = (
            "Log Mode has been **successfully deactivated**! 🎊\n\n"
            "Thank you so much for helping identify possible bugs or issues. 🙏💻\n"
            "Logs are now paused, and the bot will continue operating normally.\n\n"
            "💡 *Tip:* If you want to contribute further, you can open an **issue** or create a **pull request** on the repository [here](https://github.com/Zev-Lonewolf/ModEx_DiscordBot) to report or help fix the error. Any contribution is highly appreciated! 🌟"
        )
        rodape = "🗃️ ModEx - Thanks for your collaboration and patience!"

    embed = discord.Embed(
        title=titulo,
        description=descricao,
        color=discord.Color.red()
    )
    embed.set_footer(text=rodape)
    return embed
