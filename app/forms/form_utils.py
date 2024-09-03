# TODO: Перенести сюда создание форм сюда
from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# TODO: add annotation
# TODO: need refactoring


async def form_step(
    callback: CallbackQuery,
    state: FSMContext,
    stateCls: StatesGroup,
    obj: str,
    obj_glob: str,
    step_texts: list,
    step_text1: str,
    name: str,
) -> None:

    steps: tuple[str] = stateCls.__state_names__
    current_state: str = await state.get_state()
    indexStep: int = steps.index(current_state)
    state_data: dict[str, Any] = await state.get_data()
    tableObj: dict[str, Any] = state_data[obj]

    if callback.data == "back":

        await state.clear()
        indexStep -= 1
        current_state = steps[indexStep]
        state_data.pop(current_state.split(":")[-1])
        tableObj = state_data[obj_glob]
        for key in stateCls.__states__:
            if key._state in state_data:
                tableObj = tableObj[state_data[key._state]]

        state_data[obj] = tableObj
        await state.set_state(current_state)

        await state.update_data(state_data)
        callback_text = f"Вы вернулись на предыдущий этап {name}"
        while len(tableObj) == 1 and indexStep != 0:
            # Автоматически выбираем единственный вариант
            await state.clear()
            indexStep -= 1
            current_state = steps[indexStep]
            state_data.pop(current_state.split(":")[-1])
            tableObj = state_data[obj_glob]
            for key in obj_glob.__states__:
                if key._state in state_data:
                    tableObj = tableObj[state_data[key._state]]

            state_data[obj] = tableObj
            await state.set_state(current_state)
            await state.update_data(state_data)

    elif callback.data.startswith(f"{current_state.split(':')[-1]}_"):
        selected_value = list(tableObj.keys())[int(callback.data.split("_")[-1])]
        tableObj = tableObj[selected_value]
        await state.update_data({current_state.split(":")[-1]: selected_value, obj: tableObj})
        indexStep += 1
        current_state = steps[indexStep]
        await state.set_state(current_state)
        callback_text = f'Вы выбрали "{selected_value}"'

        while len(tableObj) == 1 and indexStep != 3:
            # Автоматически выбираем единственный вариант
            next_selected_value = list(tableObj.keys())[0]
            tableObj = tableObj[next_selected_value]
            await state.update_data({current_state.split(":")[-1]: next_selected_value, obj: tableObj})
            indexStep += 1
            current_state = steps[indexStep]
            await state.set_state(current_state)
    else:
        return

    keyboard = InlineKeyboardBuilder()
    for num, key in enumerate(tableObj.keys()):
        keyboard.row(InlineKeyboardButton(text=key, callback_data=f"{current_state.split(':')[-1]}_{num}"))

    if indexStep != 0:
        keyboard.row(InlineKeyboardButton(text="Назад", callback_data="back"))

    step_text = step_text1 + step_texts[indexStep]
    await callback.message.edit_text(step_text, reply_markup=keyboard.as_markup(resize_keyboard=True))
    await callback.answer(callback_text)


async def next_step(state_cls: StatesGroup, state: FSMContext) -> None:
    steps: tuple[str] = state_cls.__state_names__
    current_state: str = await state.get_state()
    index_state: int = steps.index(current_state) + 1
    if index_state >= len(steps):
        return await state.clear()

    return await state.set_state(steps[index_state])
