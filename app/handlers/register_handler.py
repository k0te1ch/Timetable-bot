import database.services.faculty
from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import Group, Role
from database.services.course import get_courses_by_faculty_id
from database.services.direction import get_directions_by_course_id
from database.services.group import get_groups_by_profile_id, get_specific_group
from database.services.profile import get_profiles_by_direction_id
from database.services.role import get_role_by_name
from database.services.user import create_user
from filters.dispatcherFilters import IsPrivate
from forms.form_utils import next_step
from forms.register import Register
from loguru import logger

router = Router(name="registerHandler")
router.message.filter(IsPrivate)


# TODO: Добавить логирование
# TODO: Добавить другие роли


# Handle /start command
@router.message(F.text, CommandStart())
async def start(msg: Message, state: FSMContext, username: str, db, existUser: bool) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Called <b>/start</b> command")

    if existUser:
        from handlers.main_handler import menu

        return await menu(msg=msg, username=username, state=state, db=db, existUser=existUser)

    await state.set_state(Register.faculty)

    async with db.session() as session:
        async with session.begin():
            faculties = await database.services.faculty.get_faculties(session)
            faculties = [(i.id, i.name) for i in faculties]

    await state.update_data(faculties=faculties)

    keyboard = InlineKeyboardBuilder()
    for num, key in enumerate(faculties):
        keyboard.row(InlineKeyboardButton(text=key[1], callback_data=f"faculty_{num}"))

    await msg.answer(
        "Регистрация: Выберете ваш факультет",
        reply_markup=keyboard.as_markup(resize_keyboard=True),
    )


# TODO: Сделать
@router.callback_query(F.data == "back", StateFilter(Register))
async def handle_back(callback: CallbackQuery, state: FSMContext) -> None:
    pass


@router.callback_query(F.data.contains("faculty_"), Register.faculty)
async def get_faculty(callback: CallbackQuery, state: FSMContext, username: str, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Selected faculty")

    await next_step(Register, state)

    faculty_id, selected_value = (await state.get_data())["faculties"][int(callback.data.split("_")[-1])]

    async with db.session() as session:
        async with session.begin():
            courses = await get_courses_by_faculty_id(session, faculty_id)
            courses = [(i.id, i.name) for i in courses]

    await state.update_data(courses=courses, faculty=(faculty_id, selected_value))

    keyboard = InlineKeyboardBuilder()
    for num, key in enumerate(courses):
        keyboard.row(InlineKeyboardButton(text=key[1], callback_data=f"course_{num}"))

    await callback.answer(f'Вы выбрали "{selected_value}"')

    await callback.message.edit_text(
        "Регистрация: Выберете ваш курс", reply_markup=keyboard.as_markup(resize_keyboard=True)
    )


@router.callback_query(F.data.contains("course_"), Register.course)
async def get_course(callback: CallbackQuery, state: FSMContext, username: str, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Selected course")

    await next_step(Register, state)

    course_id, selected_value = (await state.get_data())["courses"][int(callback.data.split("_")[-1])]

    async with db.session() as session:
        async with session.begin():
            directions = await get_directions_by_course_id(session, course_id)
            directions = [(i.id, i.name) for i in directions]

    await state.update_data(directions=directions, course=(course_id, selected_value))

    keyboard = InlineKeyboardBuilder()
    for num, key in enumerate(directions):
        keyboard.row(InlineKeyboardButton(text=key[1], callback_data=f"direction_{num}"))

    await callback.answer(f'Вы выбрали "{selected_value}"')

    await callback.message.edit_text(
        "Регистрация: Выберете ваше направление", reply_markup=keyboard.as_markup(resize_keyboard=True)
    )


@router.callback_query(F.data.contains("direction_"), Register.direction)
async def get_direction(callback: CallbackQuery, state: FSMContext, username: str, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Selected direction")

    await next_step(Register, state)

    direction_id, selected_value = (await state.get_data())["directions"][int(callback.data.split("_")[-1])]

    async with db.session() as session:
        async with session.begin():
            profiles = await get_profiles_by_direction_id(session, direction_id)
            profiles = [(i.id, i.name) for i in profiles]

    await state.update_data(profiles=profiles, direction=(direction_id, selected_value))

    keyboard = InlineKeyboardBuilder()
    for num, key in enumerate(profiles):
        keyboard.row(InlineKeyboardButton(text=key[1], callback_data=f"profile_{num}"))

    await callback.answer(f'Вы выбрали "{selected_value}"')

    await callback.message.edit_text(
        "Регистрация: Выберете ваш профиль", reply_markup=keyboard.as_markup(resize_keyboard=True)
    )


@router.callback_query(F.data.contains("profile_"), Register.profile)
async def get_profile(callback: CallbackQuery, state: FSMContext, username: str, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Selected profile")

    await next_step(Register, state)

    profile_id, selected_value = (await state.get_data())["profiles"][int(callback.data.split("_")[-1])]

    async with db.session() as session:
        async with session.begin():
            groups = await get_groups_by_profile_id(session, profile_id)
            groups = [(i.id, i.name) for i in groups]

    await state.update_data(groups=groups, profile=(profile_id, selected_value))

    keyboard = InlineKeyboardBuilder()
    for num, key in enumerate(groups):
        keyboard.row(InlineKeyboardButton(text=key[1], callback_data=f"group_{num}"))

    await callback.answer(f'Вы выбрали "{selected_value}"')

    await callback.message.edit_text(
        "Регистрация: Выберете вашу группу", reply_markup=keyboard.as_markup(resize_keyboard=True)
    )


@router.callback_query(F.data.contains("group_"), Register.group)
async def get_group(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Selected group")

    await next_step(Register, state)

    group_id, selected_value = (await state.get_data())["groups"][int(callback.data[len("group_") :])]

    await state.update_data(group=(group_id, selected_value))

    await callback.answer(f'Вы выбрали "{selected_value}"')

    await callback.message.edit_text("Регистрация: Напишите ваше имя")


@router.message(F.text, Register.first_name)
async def get_first_name(message: Message, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get first name")

    await next_step(Register, state)

    await state.update_data(first_name=message.text.strip())

    await message.answer("Регистрация: Напишите ваше отчество")


@router.message(F.text, Register.middle_name)
async def get_middle_name(message: Message, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get middle name")

    await next_step(Register, state)

    await state.update_data(middle_name=message.text.strip())

    await message.answer("Регистрация: Напишите вашу фамилию")


@router.message(F.text, Register.last_name)
async def get_last_name(message: Message, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get last name")

    await next_step(Register, state)

    await state.update_data(last_name=message.text.strip())

    # TODO: сюда всю инфу

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Всё правильно", callback_data="ok"))
    # keyboard.row(InlineKeyboardButton(text="Изменить", callback_data=f"no")) # TODO: Сделать систему верификации
    await message.answer("Регистрация: Удостоверьтесь в правильности данных", reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "ok", Register.verify)
async def get_verify_ok(callback: CallbackQuery, state: FSMContext, username: str, db) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get verify and its ok")

    state_data = await state.get_data()

    async with db.session() as session:
        async with session.begin():
            group: Group = await get_specific_group(
                session=session,
                faculty=state_data["faculty"][1],
                direction=state_data["direction"][1],
                profile=state_data["profile"][1],
                group=state_data["group"][1],
                course=state_data["course"][1],
            )
        async with session.begin():
            role: Role = await get_role_by_name(session, "Бакалавр")
        async with session.begin():
            result: bool = await create_user(
                session=session,
                telegram_id=callback.from_user.id,
                vk_id=None,
                first_name=state_data["first_name"],
                middle_name=state_data["middle_name"],
                last_name=state_data["last_name"],
                role=role,
                group=group,
            )
    await next_step(Register, state)
    if result:
        await callback.answer("Вы успешно зарегистрированы!")
        from handlers.main_handler import menuCallback

        return await menuCallback(callback=callback, username=username, state=state, db=db, existUser=True)

    await callback.answer("Вы уже зарегистрированы!")


@router.callback_query(F.data == "no", Register.verify)
async def get_verify_no(callback: CallbackQuery, state: FSMContext, username: str) -> None:
    logger.opt(colors=True).debug(f"[<y>{username}</y>]: Get verify and its no")
    # TODO: Придумать как это реализовать
