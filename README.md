# Timetable-bot

## 👥 Developers

- tg: [@k0te1ch](https://t.me/k0te1ch)
- vk: [@k0te1ch](https://vk.com/k0te1ch)
- tg: [@ShyDamn](https://t.me/ShyDamn)
- vk: [@ShyDamn](https://vk.com/fandomdan)

## 🛠 Getting Started

Для установки необходим python 3.10, poetry старше 1.8
Клонировать данный репозиторий
Настроить .env

```bash
poetry shell
poetry update
docker-compose --env-file .env build
docker-compose up -d --force-recreate
```

При первом запуске:

```bash
docker exec -it bot-container bash
python app/bot.py makemigrations -s False
python app/bot.py migrate -s False
exit
```

## 🙋‍♂️ FAQs

- **У меня возникла ошибка при использовании Docker, бот постоянно перезагружается, что делать?** Данный вариант возможен при использовании альтернативного запуска бота либо при неправильной настройки .env файла. В таком случае удалите сгенерированные volumes и containers в Docker, затем перепроверьте env, вноваь выполните poetry update в консоли и пробуйте заново.
- **Как мне запуститься через Docker?** Скачайте [Docker Installer](https://www.docker.com/products/docker-desktop/) по ссылке, установите и запустите Docker
- **Почему не запускается Docker?** - Проверьте, включён ли режим виртуализации в BIOS (либо смотрите по конкретной ошибке в интернете).
- **Как создать своего бота?** - Используйте [BotFather](https://t.me/BotFather)
- **Как посмотреть id чата для обратной связи?** - Перешлите сообщение из своего канала/бота для обратной связи в [getMyID](https://t.me/getmyid_bot) либо используйте [telegram](https://web.telegram.org/a) в Web версии, ID будет указан в ссылке канала.
- **Как запустить make?** - Скачайте программу [gnuWin](https://sourceforge.net/projects/gnuwin32/files/make/3.81/make-3.81.exe/download?use_mirror=deac-riga&download=), следом в корневой директории найдите make.exe, этот путь добавьте в переменные среды, в окружение PATH.

## 📚 Usage Examples

Timetable for VSU

- tg: @TimetableVSU_bot
- vk: @shedulevsubot (not supported)

## License

[APACHE LICENSE, VERSION 2.0](https://www.apache.org/licenses/LICENSE-2.0)\
See LICENSE.txt file for more details.
