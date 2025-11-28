<!-- LOGO -->
<p align="center">
  <img src="https://i.imgur.com/YZEbeyq.png" width="200px" alt="ModEx Logo"/>
</p>

<!-- MINI RESUMO - Resumo curto inicial -->
<p align="center">
  <em>
    ModEx (Mode Executor) is a Discord bot that reorganizes large servers into thematic sections by adjusting roles and channel visibility for each group.  
    It lets you activate complete sets of channels — Whether for movies, music, sweepstakes, events, casual activities, or any other topic that requires automated organization.
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

<!-- Collapsible Table of Contents Section -->
<details><summary><b>📋 Table of Contents</b></summary>

- [🧭 Overview](#overview)
  - [Why ModEx?](#ㅤ---)
- [⚙️ Features](#features)
- [📁 Project Structure](#project-structure) 
- [🗂️ Project Index](#project-index)
- [🧩 Get Started](#get-started)
  - [🚀 Invite or Installation](#invite)
  - [🧠 Usage](#usage)
    - [🤖 Using the Official Bot](#official-usage)
    - [🧭 Mode Creation Flow](#mode-flow)
    - [🔄 Navigation](#navigation)
    - [🧩 Running Locally](#running-the-bot)
    - [🧪 Testing](#tests)
- [🌈 Roadmap](#roadmap)
- [🤝 Contributing](#contributing)
- [✨ Acknowledgments](#acknowledgments)
- [💖 Support the developers](#support-the-developers)
- [License](#license)

</details>

<!-- OVERVIEW - Visão Geral do Projeto -->
<a id="overview"></a>
## 🧭 Overview

**ModEx Discord Bot** is a structured, multilingual system built to create, edit, manage, and seamlessly switch between fully customized server *modes*. A **mode** represents a complete configuration of roles and channels that determines what each member can see or access, allowing large or multi-theme servers to reorganize themselves instantly and efficiently.

The system was originally inspired by the challenge of maintaining different “sections” within a shared community — such as RPG areas, casual spaces, or thematic categories like movies or music. Instead of manually toggling permissions or updating roles for dozens of users, ModEx automates the entire workflow:

- When a mode is activated, all members below the bot's hierarchy receive the corresponding role.  
- Only the channels assigned to that mode remain visible to regular members.  
- All other channels are hidden automatically.  
- Server owners and roles above the bot always retain full visibility.

This approach allows administrators to manage multiple server layouts effortlessly, such as:
- **Work/Team Mode:** Project channels, task boards, reporting areas, meeting logs, documentation hubs.
- **Event Mode:** Registration channels, ticket check-in, announcements, schedule boards, voice stages, staff-only areas.
- **Study Mode:** Subject channels, resource libraries, group rooms, Q&A spaces, notebook uploads.
- **Creative Mode:** Art dumps, music sharing, writing corners, critique rooms, project showcases.
- **Marketplace Mode:** Buyer/seller listings, feedback threads, price checks, trade channels.
- **Clan/Guild Mode:** Raid planning, ranking boards, team coordination, strategy rooms, voice hubs.
- **Education/Workshop Mode:** Sessions, modules, exercises, instructor-only channels, resource repositories.
- **And More!**

A mode can also be designated as a **reception mode**, automatically assigning a specific role to every new member who joins the server, similar to welcome or visitor roles, but without custom greetings. This ensures consistent onboarding and default visibility for newcomers.

<!-- SUBSEÇÃO RECOLHÍVEL - "Why ModEx?" -->
### ㅤ---
<details><summary><b>Why ModEx?</b></summary>

ModEx provides a powerful, scalable solution for administrators who need:

- 🔁 Admins no longer need to reconfigure permissions every time the server shifts focus.
- 🧩 Community sections can be swapped in or out without rebuilding the server from scratch.
- 🎯 Layouts stay consistent across updates, role changes, and new members joining.
- 🏗️ Large servers with multiple themes or activities can stay organized without fragmenting into separate servers.
</details>

---

<!-- FEATURES - Base section for any project -->
<a id="features"></a>
## ⚙️ Features

|      | Category         | Description |
| :--- | :--------------- | :----------- |
| 🎯 | **Mode System** | Create, edit and switch between complete server configurations (roles + channels). Includes reception modes for automatic onboarding. |
| 🛠️ | **Smart Automation** | Automatic visibility control, conflict detection, role synchronization, and per-mode validation. |
| 📚 | **Multilingual Support** | Full support for Portuguese and English with per-server language profiles. |
| 🔍 | **Logging & Debugging** | Centralized logging with detailed debug insights for easier troubleshooting. |
| 🧩 | **Modular Design** | Separated modules for logic, embeds, language handling, and logging. Easy to extend and maintain. |
| 🛡️ | **Permission Safety** | Server ownership checks, bot hierarchy validation, and protected modification rules. |
| ⚡ | **Optimized Workflow** | Cached modes, efficient IO, and responsive reaction-based navigation. |

---

<!-- Project Structure -->
<a id="project-structure"></a>
## 📁 Project Structure

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

<a id="project-index"></a>
### 🗂️ Project Index

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
</details>
          
---

<a id="get-started"></a>
## 🧩 Get Started

ModEx offers two distinct setup paths designed for both everyday users and developers who want full control.

<a id="invite"></a>
#### 🚀 Option A — Invite the Official Bot (recommended for most users)

If your goal is simply **use ModEx immediately** on your Discord server, this is the fast lane.
No install. No setup. No dependencies. No technical hurdles.
Just invite and you're ready to go:

> 🎉 **[Add ModEx to Your Discord Server](https://discord.com/oauth2/authorize?client_id=1396498715803385970)**
> *(Instant access, works right away)*

#### 🛠️ Option B — Build From Source (for developers & modders)

If you want to **customize**, **understand the internals**, **debug**, or **contribute** to the project, you can install ModEx locally and run your own bot instance.
<details>

<summary><b>Show full installation steps</b></summary>

#### **1. Clone the repository**

```sh
git clone https://github.com/Zev-Lonewolf/ModEx_DiscordBot.git
cd ModEx_DiscordBot
```

#### **2. Install dependencies**
**Using pip**

```sh
pip install -U discord.py>=2.0.0 python-dotenv
```

**Using uv (recommended for speed)**

```sh
uv pip install -U discord.py>=2.0.0 python-dotenv
```

#### **3. Configure environment variables**
Create a `.env` file inside the `src/` folder:

```env
TOKEN=your_discord_token_here
PREFIX=!
LANGUAGE_PATH=./languages.json
DEBUG_ENABLED=false
```

#### **4. Set up permissions for your custom bot**
Inside the Discord Developer Portal:

* Enable the **bot** scope
* Grant the required permissions:

  * Manage Roles
  * Manage Channels
  * Send Messages
  * Manage Messages
  * Add Reactions
  * Read Messages/View Channels

---

<a id="usage"></a>
### 🧠 Usage

This section is divided into two paths:

> * **Using the official bot** (recommended for regular users)
> * **Running a local instance** (intended for developers)

<a id="official-usage"></a>
#### 🤖 Using the Official Bot:

<!-- Esta parte é para usuários comuns que apenas querem usar o bot, sem rodar nada localmente. -->
Once the bot is invited to your server, all interactions are performed using text commands.

#### **Available Commands**

| Command      | Aliases                  | Description               | Permission   |
| ------------ | ------------------------ | ------------------------- | ------------ |
| `!setup`     | `Setup`, `SETUP`         | Set server language       | manage_guild |
| `!create`    | `Create`, `CREATE`       | Create new mode           | manage_guild |
| `!edit`      | `Edit`, `EDIT`           | Edit existing mode        | manage_guild |
| `!delete`    | `Delete`, `DELETE`       | Delete a mode             | manage_guild |
| `!switch`    | `Switch`, `SWITCH`       | Switch to another mode    | manage_guild |
| `!log`       | `Log`, `LOG`             | Enable/disable debug mode | manage_guild |
| `!clean`     | `Clean`, `CLEAN`         | Clear bot messages        | manage_guild |
| `!about`     | `About`, `ABOUT`         | Information about the bot | none         |
| `!functions` | `Functions`, `FUNCTIONS` | List of functions         | none         |

<a id="mode-flow"></a>
#### 🧭 Mode Creation Flow

<!-- Aviso claro: usuários comuns devem pular a parte de "Running Locally" e vir direto para cá. -->
> **Regular users:**
> If you are using the official bot, skip the “Running Locally” section and start here.

1. Type `!create`
2. Enter the mode name (validated automatically)
3. Select a server role (confirm with ✅)
4. Select visible channels (confirm with ✅)
5. Configure reception mode if desired (confirm with ✅ or ❌)
6. Finalize creation (confirm with ✅)

<a id="navigation"></a>
#### 🔄 Navigation

* **✅ Next:** Proceed to the next step
* **❌ Cancel:** Abort the current action
* **🔙 Back:** Return to the previous step

<a id="running-the-bot"></a>
#### 🧩 Running Locally (Developers Only)

<!-- Aviso claro de que esta parte NÃO é necessária para usuários comuns. -->
> **Note:**
> This section is intended for developers.
> Regular users do **not** need to run the bot locally.

Run the bot using:

**Using pip:**

```sh
python src/main.py
```

**Using uv:**

```sh
uv run src/main.py
```

---

<!-- TESTS - Generic Testing Section -->
<a id="tests"></a>
### 🧪 Testing

The project includes automatic validations and error handling. To test:

1. **Mode creation test:**
    - Follow the creation flow
  
  ```sh
  !create
  ```

2. **Validation test:**
   - Try to create a mode with a duplicate name
   - Try to reference deleted channels
   - Check for role conflict detection

3. **Permissions test:**
   - Try to execute commands without manage_guild permission
   - Check denied access logs

4. **Multilingual test:**
    - Select a different language

  ```sh
  !Language
  ```

</details>

---

<!-- ROADMAP - Future Plans / Milestones -->
<a id="roadmap"></a>
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

<a id="contributing"></a>
## 🤝 Contributing

- **💬 [Open Discussions](https://github.com/Zev-Lonewolf/ModEx_DiscordBot/discussions):** Share insights, provide feedback, or ask questions
- **🐛 [Report Issues](https://github.com/Zev-Lonewolf/ModEx_DiscordBot/issues):** Submit bugs you find or request new features
- **💡 [Send Pull Requests](https://github.com/Zev-Lonewolf/ModEx_DiscordBot/pulls):** Review open PRs and send your contributions

<details closed>
<summary>Contribution Guidelines</summary>

1. **Fork the Repository:** Start by forking the repository to your GitHub account
2. **Clone Locally:** Clone the forked repository using a git client
```sh
   git clone https://github.com/Zev-Lonewolf/ModEx_DiscordBot
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

<a id="acknowledgments"></a>
## ✨ Acknowledgments

* **discord.py** — For providing the core library that powers the project  
* **Discord Developers Community** — For guidance, documentation, and shared knowledge  
* **Contributors** — For code improvements, fixes, and enhancements  
* **All users** — For feedback, testing, and helping the project evolve  
* **Special thanks to all supporting tools and technologies** — Editors, platforms, libraries, and ecosystems that made development smoother and more reliable

---

<a id="support-the-developers"></a>
## 💖 Support the developers

If this project helped you, inspired you, or saved you a few hours of work, consider giving it a ⭐ on GitHub, it truly makes a difference.
You can also follow the people behind the project to stay updated on new releases, improvements, and related work. Every star, follow, and piece of feedback helps keep the project growing. Thanks for the support!

* **Gleidson Gonzaga (“Zev”) — Project Owner & Lead Developer**  
📎 https://github.com/Zev-Lonewolf  
* **Noara Inazawa (“Noa”) — Technical Assistant & Co-Developer**  
📎 No contact link currently available

---

## 📜 License
ModEx Discord Bot is protected under the [MIT License](LICENSE). For more details, see the [LICENSE](LICENSE) file.

---

<div align="left"><a href="#top">⬆ Back to Top</a></div>
