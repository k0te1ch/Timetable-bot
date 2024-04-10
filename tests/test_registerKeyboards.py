import pytest
from keyboards.registerHandler import ru, en
from utils.context import context

@pytest.fixture
def ru_keyboard():
    return ru()

@pytest.fixture
def en_keyboard():
    return en()

# Тест для проверки создания кнопок отмены на русском языке
def test_ru_cancel_button(ru_keyboard):
    keyboard = ru_keyboard.cancel

    assert len(keyboard.keyboard) == 1
    assert keyboard.keyboard[0][0].text == context["ru"].cancel

# Тест для проверки создания кнопок типа эпизода на английском языке
def test_en_type_episode_buttons(en_keyboard):
    keyboard = en_keyboard.typeEpisode

    assert len(keyboard.keyboard) == 1
    assert keyboard.keyboard[0][0].text == context["en"].main_episode
    assert keyboard.keyboard[0][1].text == context["en"].episode_aftershow
