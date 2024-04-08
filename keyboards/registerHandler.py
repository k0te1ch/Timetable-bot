# TODO ПЕРЕДЕЛАТЬ ВСЁ ТУТ
from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from utils.context import context

# TODO переписать кнопки для других целей


class ru:
    lang = "ru"

    #TODO PREBUILD BUTTONS
    cancel = ReplyKeyboardBuilder()
    courses = ReplyKeyboardBuilder()

    cancel.add(KeyboardButton(text = context[lang].cancel))
    cancel = cancel.as_markup(resize_keyboard=True)


class en:
    lang = "en"

    cancel = ReplyKeyboardBuilder()
    typeEpisode = ReplyKeyboardBuilder()

    cancel.add(KeyboardButton(text = context[lang].cancel))
    cancel = cancel.as_markup(resize_keyboard=True)

    typeEpisode.row(KeyboardButton(text = context[lang].main_episode), KeyboardButton(text = context[lang].episode_aftershow))
    typeEpisode = typeEpisode.as_markup(resize_keyboard=True)
