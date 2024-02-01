# EraNodes Manager

## Overview

This project is a manager bot for the [EraNodes Discord](https://discord.gg/9u6dJueQQ4) server.

## Installation
1. Clone the repository (`git clone https://github.com/Eranodes/Manager-Bot.git`)
2. Install the dependencies (`pip install -r requirements.txt`)
3. Create a `config.py` file and update with following:
```py
# Replace 123 wih discord snowflake IDs

DISCORD_TOKEN = "" # Your bot token

MAIN_GUILD = 123

INVITE_TRACKING_CHANNEL = 123

OWNER_IDS = [123,]

SUPPORT_ROLES = [123,]
SUPPORT_FORUM = 123
SOLVED_TAG = 123

SUGGESTIONS_FORUM = 123
ACCEPTED_TAG = 123
DENIED_TAG = 123
```

## License
This project is licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.en.html)
See the [LICENSE](LICENSE) file for more information.

## Maintainers
- Ritam Das [(@nxrmqlly)](https://github.com/nxrmqlly)