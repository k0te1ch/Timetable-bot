# Timetable-bot

[![CC BY-NC-ND 4.0][cc-by-nc-nd-shield]][cc-by-nc-nd]

Timetable-bot is a telegram bot designed to send a schedule. It provides users with up-to-date information about upcoming classes and events related to the learning process. The bot integrates with the schedule of Voronezh State University (VSU), which allows students to receive timely notifications about the schedule, as well as detailed information about each lesson

## 🛠 Getting Started

### Requirements

- Python 3.12
- Poetry 1.8.3 или новее
- Docker

### Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/k0te1ch/Timetable-bot.git
    cd Timetable-bot
    ```

2. Configure the .env file according to your requirements.
3. Run the following commands to set up and start:

    ```bash
    poetry shell
    poetry update
    docker-compose --env-file .env build
    docker-compose up -d --force-recreate
    ```

### First Run

Execute the following commands:

```bash
docker exec -it bot-container bash
python app/bot.py makemigrations -s False
python app/bot.py migrate -s False
exit
```

## 🙋‍♂️ FAQs

- **I encountered an error using Docker, the bot keeps restarting, what should I do?** This option is possible if the settings are incorrect .the env file. In this case, delete the generated volumes and containers in Docker, then recheck the env, run poetry update again in the console and try again.
- **Why is Docker not starting?** - Check whether virtualization mode is enabled in the BIOS; Hyper-V, WSL2 in Windows system components (or look for a specific error on the Internet).
- **How do I create my own bot and get a token?** - Use [BotFather](https://t.me/BotFather)
- **How do I view the chat id for feedback?** - Forward the message from your channel/a feedback bot in [getMyID](https://t.me/getmyid_bot) or use [telegram](https://web.telegram.org/a) in the Web version, the ID will be specified in the link of the channel.
- **How do I run make on windows?** - Download the program [GnuWin](https://sourceforge.net/projects/gnuwin32), then in the root directory, find make.exe add this path to the environment variables in the PATH environment.

## 📚 Usage Examples

Timetable for VSU

- tg: [@TimetableVSU_bot](https://t.me/TimetableVSU_bot)
- vk (not supported): @shedulevsubot

## 👥 Developers

- tg: [@k0te1ch](https://t.me/k0te1ch)
- tg: [@ShyDamn](https://t.me/ShyDamn)

- vk: [@k0te1ch](https://vk.com/k0te1ch)
- vk: [@ShyDamn](https://vk.com/fandomdan)

## 📃 License

This work is licensed under a
[Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International License][cc-by-nc-nd].

See LICENSE file for more details.

[cc-by-nc-nd]: http://creativecommons.org/licenses/by-nc-nd/4.0/
[cc-by-nc-nd-shield]: https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg
