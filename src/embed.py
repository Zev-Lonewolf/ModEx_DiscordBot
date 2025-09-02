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
                "**🌟 Se quiser apoiar, siga o desenvolvedor e dê uma estrela no projeto!**\n"
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
                "**🌟 If you'd like to support, follow the developer and star the project!**\n"
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
            title="**⛔ Em Desenvolvimento!**",
            description=(
                "Recurso em fase de criação. Como o projeto está sempre em expansão, "
                "a lista final de comandos para os usuários será listada em breve..."
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="💡 Outra alternativa é utilizar o !help nativo dos bots...")
    else:
        embed = discord.Embed(
            title="**⛔ Under Development!**",
            description=(
                "This feature is still being built. Since the project is always expanding, "
                "the final list of user commands will be listed soon..."
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="💡 You can also use the native !help command of bots...")
    return embed

def get_roles_embed(roles, language):
    filtered_roles = [role for role in roles if role.name != "@everyone"]

    if language == "pt":
        if filtered_roles:
            cargos_texto = "\n".join([f"- **{role.name}**: ({role.id})" for role in filtered_roles])
        else:
            cargos_texto = "❌ Nenhum cargo encontrado. Utilize o comando `!Manual` para adicionar manualmente."

        modos_texto = "🚧 O sistema de modos ainda está em desenvolvimento. Em breve será possível criá-los com o comando !Criar."

        embed = discord.Embed(
            title="📌 Cargos e modos do servidor",
            color=discord.Color.blurple()
        )
        embed.add_field(name="**Cargos encontrados:**", value=cargos_texto, inline=False)
        embed.add_field(name="**Modos encontrados:**", value=modos_texto, inline=False)
        embed.set_footer(text="📇 Organize seus cargos e modos com clareza para uma melhor gestão.")

    else:
        if filtered_roles:
            roles_text = "\n".join([f"- **{role.name}**: ({role.id})" for role in filtered_roles])
        else:
            roles_text = "❌ No roles found. Use the `!Manual` command to add them manually."

        modes_text = "🚧 Mode system is under development. Soon you'll be able to create them using the !Create command."

        embed = discord.Embed(
            title="📌 Server Roles and Modes",
            color=discord.Color.blurple()
        )
        embed.add_field(name="**Roles found:**", value=roles_text, inline=False)
        embed.add_field(name="**Modes found:**", value=modes_text, inline=False)
        embed.set_footer(text="📇 Keep your roles and modes organized for better server management.")
    return embed

def get_edit_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="**⛔ Em Desenvolvimento!**",
            description=(
                "Este recurso ainda está sendo desenvolvido. Aguarde a finalização da etapa de criação."
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="✨ Ajude o dev com uma estrela no GitHub! Confere lá em !Sobre")
    else:
        embed = discord.Embed(
            title="**⛔ Under Development!**",
            description=(
                "Still cooking! We’re finishing the creation part first"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="✨ Support the dev with a GitHub star! Check it out in !About")
    return embed

def get_create_embed(roles, language):
    filtered_roles = [role for role in roles if role.name != "@everyone"]

    if language == "pt":
        titulo = "**ℹ️ Informações Iniciais**"
        descricao = (
            "Olá! Seja bem-vindo(a) ao modo de criação. Se este for seu **primeiro modo**, recomendamos seguir os passos abaixo com atenção:\n\n"
            "**1.** Crie ao menos um **modo de 'recepção'**. Ele será atribuído automaticamente a quem entrar no servidor, evitando o trabalho manual.\n"
            "**2.** Certifique-se de que o bot tenha as **permissões necessárias** para funcionar corretamente. Não se preocupe, não coletamos dados dos usuários. Em caso de dúvidas, use o comando `!sobre` para acessar o repositório do projeto.\n"
            "**3.** Verifique se os cargos abaixo foram reconhecidos corretamente. Caso contrário, utilize o comando `!manual` e siga o passo a passo.\n"
            "**4.** O funcionamento do bot é simples: ele **altera os cargos dos membros** para exibir os canais privados correspondentes ao modo ativo.\n"
            "**5.** Após configurar tudo, teste criando um modo temporário e veja se o sistema aplica corretamente os cargos ao reagir.\n\n"
            "⚙️ *Lembre-se: os modos podem ser editados ou removidos a qualquer momento usando os comandos disponíveis.*"
        )
        rodape = "🗃️ ModEx - Seu servidor, seus modos!"

        if filtered_roles:
            cargos_texto = "\n".join([f"- **{role.name}**" for role in filtered_roles])
        else:
            cargos_texto = "❌ Nenhum cargo encontrado. Utilize o comando `!manual` para adicionar manualmente."

    else:
        titulo = "**ℹ️ Initial Info**"
        descricao = (
            "Hi there! Welcome to Creation Mode. If this is your **first time setting things up**, we strongly recommend following these steps carefully:\n\n"
            "**1.** Create at least one **'welcome mode'**. This mode will be automatically assigned to new members, saving you manual work.\n"
            "**2.** Make sure the bot has all the **required permissions** to function properly. Don’t worry, we don’t collect any user data. If in doubt, use the `!about` command to view the project repository.\n"
            "**3.** Check if the roles below were detected correctly. If not, run the `!manual` command and follow the step-by-step guide.\n"
            "**4.** The bot works in a simple way: it **switches roles for members** to show private channels linked to that mode.\n"
            "**5.** Once setup is done, test it by creating a temporary mode and see if it applies the roles correctly when reacting.\n\n"
            "⚙️ *Reminder: you can edit or remove modes at any time using the available commands.*"
        )
        rodape = "🗃️ ModEx - Your server, your modes!"

        if filtered_roles:
            cargos_texto = "\n".join([f"- **{role.name}**" for role in filtered_roles])
        else:
            cargos_texto = "❌ No roles found. Use the `!manual` command to add them manually."

    embed = discord.Embed(title=titulo, description=descricao, color=discord.Color.yellow())
    embed.add_field(name="**Cargos encontrados:**", value=cargos_texto, inline=False)
    embed.set_footer(text=rodape)
    return embed

def get_initial_create_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="🚧 Criação de Modo (etapa 1 de 5)",
            description=(
                "Qual será o nome do seu modo?\n\n"
                "📌 _Exemplos: Eventos, Staff, AcessoVIP..._\n"
                "✍️ _Responda com:_ `#NomeDoModo`\n\n"
                "⚠️ Evite nomes muito longos ou com símbolos estranhos."
            ),
            color=discord.Color.teal()
        )
        embed.set_footer(text="Use # antes do nome para confirmar. Ex: #Eventos")
    else:
        embed = discord.Embed(
            title="🚧 Mode Creation (step 1 of 5)",
            description=(
                "What will be the name of your mode?\n\n"
                "📌 _Examples: Events, Staff, VIPAccess..._\n"
                "✍️ _Reply with:_ `#ModeName`\n\n"
                "⚠️ Avoid very long names or strange symbols."
            ),
            color=discord.Color.teal()
        )
        embed.set_footer(text="Use # before the name to confirm. Ex: #Events")
    return embed

def get_name_saved_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="**✅ Nome salvo com sucesso!**",
            description=(
                "O nome do modo foi registrado.\n"
                "Agora, siga para a próxima etapa da criação."
            ),
            color=discord.Color.dark_green()
        )
        embed.set_footer(text="Continue seguindo as instruções para configurar seu modo.")
    else:
        embed = discord.Embed(
            title="**✅ Name saved successfully!**",
            description=(
                "The mode name has been registered.\n"
                "Now, proceed to the next creation step."
            ),
            color=discord.Color.dark_green()
        )
        embed.set_footer(text="Keep following the instructions to set up your mode.")
    return embed

def get_invalid_name_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="**❌ Nome inválido!**",
            description=(
                "O nome do modo deve ter entre **2 e 15 caracteres**.\n"
                "Por favor, escolha um nome mais curto e tente novamente."
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="Use # antes do nome para confirmar. Ex: #Eventos")
    else:
        embed = discord.Embed(
            title="**❌ Invalid name!**",
            description=(
                "The mode name must be between **2 and 15 characters**.\n"
                "Please choose a shorter name and try again."
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="Use # before the name to confirm. Ex: #Events")
    return embed

def get_name_conflict_embed(language, nome_modo):
    if language == "pt":
        embed = discord.Embed(
            title="⚠️ Conflito de nome",
            description=(
                f"Já existe um modo chamado **{nome_modo}**.\n\n"
                "✅ Clique para **editar** esse modo.\n"
                "❌ Clique para **cancelar** e escolher outro nome."
            ),
            color=discord.Color.orange()
        )
    else:
        embed = discord.Embed(
            title="⚠️ Name conflict",
            description=(
                f"A mode named **{nome_modo}** already exists.\n\n"
                "✅ Click to **edit** this mode.\n"
                "❌ Click to **cancel** and choose another name."
            ),
            color=discord.Color.orange()
        )
    return embed

def get_role_select_embed(language, roles):
    if language == "pt":
        embed = discord.Embed(
            title="🚧 Criação de Modo (etapa 2 de 5)",
            description=(
                "Escolha qual cargo será atribuído a este modo.\n\n"
                "📌 _Mencione o cargo ou digite o nome exato do cargo._\n"
                "⚠️ Você precisa ter permissão para gerenciar cargos."
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="Mencione o cargo ou digite o nome. Ex: @Staff")
    else:
        embed = discord.Embed(
            title="🚧 Mode Creation (step 2 of 5)",
            description=(
                "Choose which role will be assigned to this mode.\n\n"
                "📌 _Mention the role or type the exact role name._\n"
                "⚠️ You need permission to manage roles."
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="Mention the role or type its name. Ex: @Staff")

    role_list = "\n".join([f"- {role.name}" for role in roles])
    embed.add_field(name="Available roles:" if language != "pt" else "Cargos disponíveis:", 
                    value=role_list or ("Nenhum cargo encontrado." if language == "pt" else "No roles found."), 
                    inline=False)
    return embed

def get_role_saved_embed(language, role_name):
    if language == "pt":
        embed = discord.Embed(
            title="✅ Cargo selecionado!",
            description=f"O cargo **{role_name}** foi atribuído ao modo com sucesso.",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="✅ Role selected!",
            description=f"The role **{role_name}** was successfully assigned to the mode.",
            color=discord.Color.green()
        )
    return embed

def get_invalid_role_embed(language):
    if language == "pt":
        embed = discord.Embed(
            title="❌ Cargo inválido",
            description="Cargo não encontrado. Por favor, mencione o cargo ou digite o nome correto.",
            color=discord.Color.red()
        )
    else:
        embed = discord.Embed(
            title="❌ Invalid role",
            description="Role not found. Please mention the role or type the correct name.",
            color=discord.Color.red()
        )
    return embed

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

def get_channel_reset_warning_embed(language, canais_invalidos):
    canais_str = ", ".join(canais_invalidos)
    if language == "pt":
        embed = discord.Embed(
            title="⚠️ Canais inválidos",
            description=(
                f"Os seguintes canais são inválidos ou não podem ser usados:\n"
                f"**{canais_str}**\n\n"
                "O modo será reiniciado para corrigir os canais."
            ),
            color=discord.Color.orange()
        )
    else:
        embed = discord.Embed(
            title="⚠️ Invalid channels",
            description=(
                f"The following channels are invalid or cannot be used:\n"
                f"**{canais_str}**\n\n"
                "The mode will be reset to fix the channels."
            ),
            color=discord.Color.orange()
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
