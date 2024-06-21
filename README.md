# Timetable-bot

## Установка

Для установки необходим python 3.10, poetry старше 1.8
Клонировать данный репозиторий

<<<<<<< HEAD
```console
poetry init
=======
```bash
python -m venv .venv
// в .venv переходим в Scripts, запускаем activate.ps1 в консоли
poetry update
docker-compose --env-file .env build
docker-compose up -d --force-recreate
// При первом запуске:
docker exec -it bot-container bash
// Далее в #app прописываем:
python bot.py makemigrations -s False
python bot.py migrate -s False
exit
```

## Alternative Start 2

Для установки необходим python 3.10, poetry старше 1.8
Клонировать данный репозиторий
Настроить .env

```bash
poetry shell
poetry update
make docker-up
```

При повторном использовании 
```bash
poetry shell
poetry update
make docker-run
```

## Alternative Start 3 (Not Supported)

Для установки необходим python 3.10, poetry старше 1.8
Клонировать данный репозиторий
Настроить .env

```bash
poetry shell
>>>>>>> 8eef424 (Update README.md)
poetry update
python bot.py makemigrations
python bot.py migrate
python bot.py run
```

## Примеры использования

Timetable for VSU

- tg: @TimetableVSU_bot
- vk: @shedulevsubot
