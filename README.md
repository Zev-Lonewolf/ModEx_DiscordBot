<!-- LOGO -->
<p align="center">
  <img src="https://i.imgur.com/YZEbeyq.png" width="200px" alt="ModEx Logo"/>
</p>

<!-- MINI RESUMO - Resumo curto inicial -->
<p align="center">
  <em>
    MoDex (Mode Executor) is a Discord bot that reorganizes large servers into thematic sections by adjusting roles and channel visibility for each group.  
    It lets you activate complete sets of channels — like RPG, anime, movies, games, or casual areas — showing only what matters for each moment.
  </em>
</p>

<!-- BADGES PRINCIPAIS - Licença, tipo e status -->
<p align="center">
  <img src="https://img.shields.io/badge/License-GNU%20GPL%20v3-E92063?style=flat-square&logo=opensourceinitiative&logoColor=white"/>
  <img src="https://img.shields.io/badge/Discord-Bot-E92063?style=flat-square&logo=discord&logoColor=white"/>
  <img src="https://img.shields.io/badge/Current%20State-Release-E92063?style=flat-square"/>
</p>

<!-- TÍTULO DA SEÇÃO DAS TECNOLOGIAS -->
<p align="center"><em>Built with:</em></p>

<!-- BADGES TECNOLOGIAS - Ferramentas usadas no projeto -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.14-E92063?style=flat-square&logo=Python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Discord.py-2.0+-E92063?style=flat-square&logo=discord&logoColor=white"/>
  <img src="https://img.shields.io/badge/JSON-Data-E92063?style=flat-square&logo=json&logoColor=white"/>
  <img src="https://img.shields.io/badge/Git-F05032?style=flat-square&logo=Git&logoColor=white"/>
  <img src="https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=GitHub&logoColor=white"/>
  <img src="https://img.shields.io/badge/VS%20Code-E92063?style=flat-square&logo=visualstudiocode&logoColor=white"/>
</p>

---

<details><summary><b>📋 Table of Contents</b></summary>

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Project Index](#project-index)
- [How to Use](#how-to-use)
  - [Installation](#installation)
  - [Running the Bot](#running-the-bot)
  - [Tests](#tests)
- [Technical Details](#technical-details)
- [Roadmap](#roadmap)
- [How to Contribute](#how-to-contribute)
- [Acknowledgments](#acknowledgments)
- [Support the Developer](#support-the-developer)
- [Contact](#contact)
- [License](#license)

</details>

## Overview

**ModEx Discord Bot** is a robust, multilingual system designed for complete mode management in Discord servers. It enables creating, editing, and switching between role and channel configurations with advanced validation, detailed logging, and an interactive reaction-based interface.

**Why ModEx?**

This project provides a full-featured solution for server administrators who need:

- **🎯 Mode Management:** Create and switch between predefined role and channel configurations
- **🔐 Strong Validation:** Automatic detection of conflicts, invalid channels, and permission issues
- **🌍 Multilingual Support:** Fully available in Portuguese and English
- **📊 Advanced Logging System:** Debug mode with detailed operation tracking
- **🎨 Intuitive Interface:** Reaction-based navigation with interactive embeds
- **👥 Reception Management:** Automatic role assignment with conflict detection

---

## 🟡 Features

|      | Component        | Details                              |
| :--- | :-------------- | :----------------------------------- |
| ⚙️  | **Architecture**  | <ul><li>Discord bot built on discord.py 2.0+</li><li>Modular system with clear responsibility separation</li><li>Data persistence using JSON</li><li>Per-server multilingual state management</li></ul> |
| 🔩 | **Code Quality**  | <ul><li>Full logging system with multiple levels</li><li>Robust exception handling</li><li>Permission validation in all commands</li><li>Smart mode caching</li></ul> |
| 📄 | **Documentation** | <ul><li>Detailed README.md</li><li>Inline code comments</li><li>Contextual error messages</li><li>Integrated help system</li></ul> |
| 🔌 | **Integrations**  | <ul><li>Full Discord API support (reactions, embeds, components)</li><li>Role and channel management</li><li>Granular permission system</li><li>Server state validation</li></ul> |
| 🧩 | **Modularity**    | <ul><li>`utils/modos.py` module for business logic</li><li>`embed.py` module for interface generation</li><li>`idiomas.py` module for multilingual features</li><li>`logger_manager.py` module for centralized logging</li></ul> |
| 🧪 | **Robustness**       | <ul><li>Validation of existing channels</li><li>Role conflict detection</li><li>Automatic cleanup of invalid states</li><li>Mode recovery for ongoing edits</li><li>Timeout and network error handling</li></ul> |
| ⚡️  | **Performance**   | <ul><li>In-memory mode caching</li><li>Asynchronous reaction processing</li><li>Efficient cleanup of old messages</li><li>Optimized JSON operations</li></ul> |
| 🛡️ | **Security**      | <ul><li>Mandatory `manage_guild` permission checks</li><li>Server ownership validation</li><li>Protection against unauthorized modifications</li><li>Per-server data isolation</li></ul> |
| 📦 | **Dependencies**  | <ul><li>`discord.py>=2.0.0` for Discord integration</li><li>`python-dotenv` for environment variables</li><li>Python standard libraries (json, logging, datetime)</li></ul> |

---
## 🟠 Project Structure

The project follows a clean and modular architecture, ensuring easy maintenance, scalability, and clear separation of responsibilities.

```sh
ModEx_DiscordBot/
├── src/
│   ├── main.py                 # Core bot file (commands, events, startup)
│   ├── config.py               # Configuration handler and environment loader
│   ├── embed.py                # Centralized embed builder
│   ├── idiomas.py              # Multilingual handler (PT/EN)
│   ├── .env                    # Environment variables (never commit)
│   └── utils/
│       ├── __init__.py
│       ├── logger_manager.py   # Unified logging system
│       ├── modos.py            # Mode management logic (roles/channels)
│       └── __pycache__/
├── data/
│   ├── modos.json              # Server-specific mode storage
│   └── config.json             # Global configuration file
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore patterns
└── requirements.txt            # Python dependencies
```

### 🔴 Project Index

<details open>
    <summary><b><code>ModEx_DiscordBot/</code></b></summary>
    <!-- __root__ Submodule -->
<details>
    <summary><b>src (Main)</b></summary>
    <blockquote>
        <div class='directory-path' style='padding: 8px 0; color: #666;'>
            <code><b>⦿ src</b></code>
        <table style='width: 100%; border-collapse: collapse;'>
        <thead>
            <tr style='background-color: #f8f9fa;'>
                <th style='width: 30%; text-align: left; padding: 8px;'>File</th>
                <th style='text-align: left; padding: 8px;'>Description</th>
            </tr>
        </thead>
            <tr style='border-bottom: 1px solid #eee;'>
                <td style='padding: 8px;'><b><a href='./src/main.py'>main.py</a></b></td>
                <td style='padding: 8px;'>- Main bot file with command definitions<br>- Event handling (reactions, messages)<br>- Implementation of interactive embed flow<br>- Navigation system using reactions (✅, ❌, 🔙)<br>- Bot initialization and intents configuration</td>
            </tr>
            <tr style='border-bottom: 1px solid #eee;'>
                <td style='padding: 8px;'><b><a href='./src/config.py'>config.py</a></b></td>
                <td style='padding: 8px;'>- Loading environment variables (.env)<br>- Definition of project constants<br>- Discord token and prefix configuration<br>- Path to language and data files</td>
            </tr>
            <tr style='border-bottom: 1px solid #eee;'>
                <td style='padding: 8px;'><b><a href='./src/embed.py'>embed.py</a></b></td>
                <td style='padding: 8px;'>- Centralized generation of all Discord embeds<br>- Function for each step of the creation/edit flow<br>- Multilingual support with fallback to Portuguese<br>- Standardized visual formatting with themed colors<br>- Error, confirmation, information and success embeds</td>
            </tr>
            <tr style='border-bottom: 1px solid #eee;'>
                <td style='padding: 8px;'><b><a href='./src/idiomas.py'>idiomas.py</a></b></td>
                <td style='padding: 8px;'>- Language management per server<br>- Loading multilingual dictionary<br>- Functions to get and set server language<br>- Support for multiple languages (Português, English)<br>- Centralized translation of all messages</td>
            </tr>
            <tr style='border-bottom: 1px solid #eee;'>
                <td style='padding: 8px;'><b><a href='./src/.env'>.env</a></b></td>
                <td style='padding: 8px;'>- TOKEN: Bot Discord token<br>- PREFIX: Command prefix (default: !)<br>- LANG_PATH: Path to language file<br>- DEBUG_ENABLED: Debug mode (true/false)</td>
            </tr>
        </table>
    </blockquote>
</details>

<details>
    <summary><b>utils (Utilities)</b></summary>
    <blockquote>
        <div class='directory-path' style='padding: 8px 0; color: #666;'>
            <code><b>⦿ utils</b></code>
        <table style='width: 100%; border-collapse: collapse;'>
        <thead>
            <tr style='background-color: #f8f9fa;'>
                <th style='width: 30%; text-align: left; padding: 8px;'>File</th>
                <th style='text-align: left; padding: 8px;'>Description</th>
            </tr>
        </thead>
            <tr style='border-bottom: 1px solid #eee;'>
                <td style='padding: 8px;'><b><a href='./src/utils/logger_manager.py'>logger_manager.py</a></b></td>
                <td style='padding: 8px;'>- Centralized logging system with multiple levels<br>- Handler configuration for console and file<br>- Functions to load and save JSON configuration<br>- Detailed tracking of bot operations<br>- Debug mode with expanded logging</td>
            </tr>
            <tr style='border-bottom: 1px solid #eee;'>
                <td style='padding: 8px;'><b><a href='./src/utils/modos.py'>modos.py</a></b></td>
                <td style='padding: 8px;'>- Core logic for mode management<br>- Functions to create, edit, delete and apply modes<br>- Channel validation and conflict detection<br>- Management of welcome roles<br>- JSON data persistence<br>- Cleanup of incomplete and editing states</td>
            </tr>
        </table>
    </blockquote>
</details>

---


### 🟤 Installation

Build the ModEx Discord Bot from source and install dependencies:

1. **Clone the repository:**

```sh
    ❯ git clone https://github.com/seu-usuario/ModEx_DiscordBot.git
    ❯ cd ModEx_DiscordBot
    ```

2. **Install dependencies:**

**Using pip:**

```sh
❯ pip install -U discord.py>=2.0.0 python-dotenv
```

**Using uv (faster):**

    ```sh
    ❯ uv pip install -U discord.py>=2.0.0 python-dotenv
    ```

3. **Configure the environment variables:**

Create a `.env` file in the `src/` folder with:

```env
    TOKEN=your_discord_token_here
    PREFIX=!
    LANGUAGE_PATH=./languages.json
    DEBUG_ENABLED=false
```

**How to obtain the token:**
- Access the [Discord Developer Portal](https://discord.com/developers/applications)
    - Create a new Application
- Go to “Bot” and click “Add Bot”
- Copy the token in “TOKEN”

4. **Configure bot permissions:**

- In “Bot,” look for “SCOPES” and enable: `bot`
    - Under “PERMISSIONS,” enable:
      - Manage Roles
      - Manage Channels
      - Send Messages
      - Manage Messages
      - Add Reactions
      - Read Messages/View Channels



Translated with DeepL.com (free version)

### ⚫ Usage

Run the bot with:

**Using pip:**
```sh
❯ python src/main.py
```

**Using uv:**
```sh
❯ uv run src/main.py
```

### Available Commands

| Command | Aliases | Description | Permission |
|---------|---------|-----------|-----------|
| `!setup` | `Setup`, `SETUP` | Set server language | manage_guild |
| `!create` | `Create`, `CREATE` | Create new mode | manage_guild |
| `!edit` | `Edit`, `EDIT` | Edit existing mode | manage_guild |
| `!delete` | `Delete`, `DELETE` | Delete a mode | manage_guild |
| `!switch` | `Switch`, `SWITCH` | Switch to another mode | manage_guild |
| `!log` | `Log`, `LOG` | Enable/disable debug mode | manage_guild |
| `!clean` | `Clean`, `CLEAN` | Clear bot messages | manage_guild |
| `!about` | `About`, `ABOUT` | Information about the bot | none |
| `!functions` | `Functions`, `FUNCTIONS` | List of functions | none |

### Mode Creation Flow

1. Type `!create`
2. Enter the mode name (will be validated)
3. Select a server role (✅ to confirm)
4. Select associated channels (✅ to confirm)
5. Configure reception if desired (✅/❌)
6. Finalize creation (✅)

### Navigation

- **✅ (Next):** Advances to the next step
- **❌ (Cancel):** Cancels/denies the operation
- **🔙 (Back):** Returns to the previous step

### ⚪ Testing

The project includes automatic validations and error handling. To test:

1. **Mode creation test:**
```sh
!create
# Follow the creation flow
```

2. **Validation test:**
   - Try to create a mode with a duplicate name
   - Try to reference deleted channels
   - Check for role conflict detection

3. **Permissions test:**
   - Try to execute commands without manage_guild permission
   - Check denied access logs

4. **Multilingual test:**
   ```sh
   !setup
   # Select a different language
   ```

---

## 🌈 Roadmap

- [X] **Mode System:** Create, edit, delete, and switch between modes
- [X] **Role Management:** Assign roles to modes
- [X] **Channel Management:** Configure channels by mode
- [X] **Reception System:** Assign reception positions
- [X] **Multilingual:** Support for Portuguese and English
- [X] **Logs System:** Debug mode with tracking
- [ ] **Web Dashboard:** Web interface for remote management
- [ ] **Automatic Backup:** Configuration backup system
- [ ] **Scheduling:** Modes with specific times
- [ ] **Database Integration:** Migration from JSON to dedicated database

---

## 🤝 Contributing

- **💬 [Open Discussions](https://github.com/seu-usuario/ModEx_DiscordBot/discussions):** Share insights, provide feedback, or ask questions
- **🐛 [Report Issues](https://github.com/seu-usuario/ModEx_DiscordBot/issues):** Submit bugs you find or request new features
- **💡 [Send Pull Requests](https://github.com/seu-usuario/ModEx_DiscordBot/pulls):** Review open PRs and send your contributions

<details closed>
<summary>Contribution Guidelines</summary>

1. **Fork the Repository:** Start by forking the repository to your GitHub account
2. **Clone Locally:** Clone the forked repository using a git client
```sh
   git clone https://github.com/seu-usuario/ModEx_DiscordBot
   ```
3. **Create a New Branch:** Always work on a new branch with a descriptive name
```sh
   git checkout -b feature/new-feature
   ```
4. **Make Your Changes:** Develop and test your changes locally
5. **Commit Your Changes:** Commit with a clear message describing the updates
```sh
   git commit -m ‘Implemented new feature X’
   ```
6. **Push to GitHub:** Send the changes to the forked repository
```sh
   git push origin feature/new-feature
   ```
7. **Send a Pull Request:** Create a PR against the original repository, clearly describing the changes
8. **Review:** After review and approval, your PR will be merged into the main branch. Congratulations on your contribution!

</details>

---

## 📜 License

ModEx Discord Bot is protected under the [MIT License](LICENSE). For more details, see the [LICENSE](LICENSE) file.

---

## ✨ Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py) - Excellent Python library for Discord
- [Discord Developers Community](https://discord.gg/discord-developers) - Support and resources
- All contributors and users of the project

<div align="left"><a href="#top">⬆ Back to Top</a></div>

---
