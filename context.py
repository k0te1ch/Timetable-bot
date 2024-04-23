# TODO welcome
# TODO I18n


class ru:
    # Global
    cancel: str = "Отмена"
    back: str = "Назад"
    error_occurred: str = "Произошла ошибка! Пожалуйста, попробуйте снова"
    invalid_input: str = "Ошибка при вводе!"

    # Start handler
    canceled: str = "Отменено"
    feedback: str = "Отправлено"

    # Admin panel
    admin_panel_open: str = "Админ панель"
    admin_panel_close: str = "Админ панель закрыта"
    admin_panel_main: list = [("Бот", "bot")]
    bot_commands: list = [
        ("Выключить бота", "restart_bot"),
        ("Прислать лог-файлы", "send_logs"),
    ]


class en:
    # Global
    cancel: str = "Cancel"
    back: str = "Back"
    error_occurred: str = "An error occurred! please try again"
    invalid_input: str = "Invalid input!"

    # Start handler
    canceled: str = "Canceled"
    feedback: str = "Sending"

    # Admin panel
    admin_panel_open: str = "Admin panel"
    admin_panel_close: str = "Admin panel closed"
    admin_panel_main: list = [("Bot", "bot")]
    bot_commands: list = [("Turn off the bot", "restart_bot"), ("Send log-files", "send_logs")]
