<div align="center">
  <img src="https://i.imgur.com/6B3dzwe.png" alt="Bot Preview" width="300" />
</div>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue" alt="Python" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License" />
  <img src="https://img.shields.io/badge/Discord-Bot-5865F2?logo=discord" alt="Discord" />
  <img src="https://img.shields.io/badge/JSON-Data-5E5C5C?logo=json&logoColor=white" alt="JSON" />
  <img src="https://img.shields.io/badge/Current%20State-In%20Development-orange" alt="Current State" />
</p>

<p align="center"><strong>Python Discord bot that manages multiple server modes by automatically toggling member roles. Supports multilingual servers and streamlines permission management based on the active mode.</strong></p>


---

### 📚 About

ModEx is a Python Discord bot designed to manage multiple server "modes" by dynamically toggling member roles and controlling access to private channels. Each mode corresponds to a set of designated channels—only users with the associated role can view and interact with them.

Created to support multilingual servers, ModEx simplifies organizational flow by automatically enforcing permissions per mode. Ideal for managing gaming lobbies, study groups, event areas, and more.

Perfect for server administrators or developers looking for structured role and access management driven by active modes.

![Discord](https://img.shields.io/badge/Discord-Bot-5865F2?logo=discord)  ![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)  ![VS Code](https://img.shields.io/badge/VSCode-Editor-007ACC?logo=visual-studio-code&logoColor=white) ![JSON](https://img.shields.io/badge/JSON-Data-5E5C5C?logo=json&logoColor=white")

### 🚀 How to Use

1. **Invite the bot to your Discord server:**  
   Click [here](https://discord.com/oauth2/authorize?client_id=1396498715803385970&permissions=8&integration_type=0&scope=bot+applications.commands) to add ModEx with the necessary permissions.

2. **Set the bot language:**  
   React to the language selection message with 🇺🇸 for English or 🇧🇷 for Portuguese.

3. **Start managing your server modes:**  
   Use the bot commands to create, edit, and switch modes that control roles and channel access dynamically.

4. **Explore useful commands:**  
   - `!criar` / `!create` — Create a new mode.  
   - `!editar` / `!edit` — Edit an existing mode.  
   - `!verificar` / `!check` — View current modes and roles.  
   - `!funções` / `!functions` — List available bot functions.  
   - `!sobre` / `!about` — Learn more about the bot.  
   - `!limpar` / `!clean` — Clear recent bot messages for a tidy channel.

> ✅ The bot automatically manages permissions and roles based on the active mode, making server organization seamless.


## 🛠️ Technical Details & Techniques Used

ModEx is a Discord bot written in Python using the `discord.py` library. It provides dynamic management of server modes by toggling roles and permissions automatically based on the active mode.

The bot is structured primarily around a single main script (`main.py`) supported by utility modules for handling data persistence (`utils/modos.py`) and configuration (`config.py`). Data is stored in JSON files (`modos.json` and `idiomas.json`) for modes and language settings, ensuring easy scalability and straightforward management.

Key features include:  
- Dynamic creation, editing, and deletion of server modes linked to specific roles and channels.  
- Automatic permission overwrites on Discord channels to reflect the selected mode's visibility rules.  
- Multilingual support with English and Portuguese handled via reaction-based language selection.  
- Command-based interaction with users to setup modes, configure roles, and manage permissions.  
- Clean asynchronous event handling for message commands and reaction responses.

### Techniques Used  
- Discord API via `discord.py` for real-time bot interactions.  
- JSON-based persistent storage for modes and language configurations.  
- Rol## 🎲 Example of Use — Practical Scenarios

### 1. Setting the Bot Language  
After adding the bot to your server, you want to set it to communicate in Portuguese:  
- **Command:** `!language`  
- **Bot Response:** Sends an embed prompting you to choose between 🇧🇷 and 🇺🇸 reactions.  
- *Upon reacting with 🇧🇷, the bot confirms the language change and sends a welcome message in Portuguese.*

---

### 2. Creating a New Server Mode  
You intend to organize specific channels for a gaming community within your server:  
- **Command:** `!create`  
- **Bot Response:** Requests the mode name (e.g., `#rpg`).  
- *After providing the name `#rpg`, the bot asks to mention the primary role associated with this mode.*  
- *You mention the role “Player”.*  
- **Bot Response:** Prompts to specify the channels that will become private under this mode.  
- *You mention the relevant channels.*  
- **Bot Response:** Asks if additional roles should be added (optional).  
- *You respond with “skip” to bypass this step.*  
- **Bot Response:** Confirms that the mode has been created and applies the necessary channel permission changes automatically.

---

### 3. Reviewing Existing Modes  
You want to review the modes currently configured on your server:  
- **Command:** `!check`  
- **Bot Response:** Displays an embed listing all created modes along with their associated roles.

---

### 4. Editing an Existing Mode  
You need to modify the roles or channels linked to a previously created mode:  
- **Command:** `!edit`  
- **Bot Response:** Guides you through selecting the mode to edit and updating its parameters step-by-step.

---

### 5. Viewing Bot Functions and Help  
You require information about available commands and bot features:  
- **Command:** `!functions`  
- **Bot Response:** Sends an embed outlining all commands and their purposes.

---

### 6. Accessing Bot Information  
You want to know more about the bot itself, its purpose, and its development:  
- **Command:** `!about`  
- **Bot Response:** Provides an embed with detailed information about the bot.

---

### 7. Cleaning Bot Messages  
You prefer to clear the bot’s messages from a channel for tidiness:  
- **Command:** `!clean`  
- **Bot Response:** Deletes recent bot messages within the channel.

---

This set of practical examples demonstrates the core functionalities of the bot and guides server administrators through typical usage scenarios.
e and channel permission management with Discord permission overwrites.  
- State management for multi-step user interactions using dictionaries keyed by user IDs.  
- Embed messages to provide structured and user-friendly interfaces.

Planned improvements include enhanced error handling, support for more languages, and optional web dashboard integration for easier mode management.

### 🙏 Credits and Acknowledgments

This Discord Bot project is the original idea of Zev Lonewolf (Gleidson Gonzaga), with collaboration and technical support from the assistant Noa.

We sincerely thank the tools that made this development possible, including Visual Studio Code, the Discord.py library, the Python programming language—created by Guido van Rossum and his remarkable community—and the JSON library, whose simplicity and efficiency are often underestimated but essential to the project’s functionality.

Furthermore, we recognize the value of developer communities and enthusiasts who constantly share knowledge and support, fostering innovation and continuous learning.

Finally, this project is dedicated to everyone who, directly or indirectly, contributes to turning ideas into reality and continues to believe in the power of technology to connect people.

### 🙌 Help the Developer

If this project helped you or caught your interest, a ⭐ star on GitHub would mean a lot!

Feel free to follow me for more projects, updates, and all things nerdy.

Every star and follower keeps the creative engine running — thanks for the support!

---

## 📝 License

Copyright (C) 2025 Zev Lonewolf

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

You are free to use, modify, and distribute this software under the terms of the GPL v3, which ensures that all derivative works also remain open source and respect user freedoms.

For the full license text, see the [LICENSE](LICENSE) file in this repository or visit the [GNU GPL v3 official page](https://www.gnu.org/licenses/gpl-3.0.en.html).
