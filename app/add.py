from aiogram import types, Router

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.shared import user_data


router = Router()


# Define states for adding a habit
class AddHabit(StatesGroup):
    name = State()
    schedule = State()
    date = State()
    day_of_week = State()
    day_of_month = State()
    time = State()


# Handler to capture habit name
@router.message(AddHabit.name)
async def get_habit_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    habit_name = message.text
    await state.update_data(name=habit_name)
    await state.set_state(AddHabit.schedule)

    # Create inline keyboard for repeat schedule options
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Once", callback_data="schedule_once")
    keyboard_builder.button(text="Every day", callback_data="schedule_every_day")
    keyboard_builder.button(
        text="Specific day of the week", callback_data="schedule_weekly"
    )
    keyboard_builder.button(
        text="Specific day of the month", callback_data="schedule_monthly"
    )
    keyboard_builder.adjust(1)
    keyboard = keyboard_builder.as_markup()

    await message.answer("Choose a repeat schedule:", reply_markup=keyboard)


# Callback query handler for schedule options
@router.callback_query(lambda call: call.data.startswith("schedule_"))
async def schedule_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    schedule_input = callback_query.data.split("_")[1]

    # Process user's choice
    if schedule_input == "once":
        await state.update_data(schedule="once")
        await state.set_state(AddHabit.date)
        await callback_query.message.answer("Enter the date in YYYY-MM-DD format:")

    elif schedule_input == "every":
        await state.update_data(schedule="every day")
        await state.set_state(AddHabit.time)
        await callback_query.message.answer("Enter the time in HH:MM format:")

    elif schedule_input == "weekly":
        await state.update_data(schedule="weekly")
        await state.set_state(AddHabit.day_of_week)
        # Create inline keyboard for day of the week options
        keyboard_builder = InlineKeyboardBuilder()
        days_of_week = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for day in days_of_week:
            keyboard_builder.button(text=day, callback_data=f"day_of_week_{day}")
        keyboard_builder.adjust(2)
        keyboard = keyboard_builder.as_markup()
        await callback_query.message.answer()
        await callback_query.message.edit_text(
            "Choose a day of the week:", reply_markup=keyboard
        )

    elif schedule_input == "monthly":
        await state.update_data(schedule="monthly")
        await state.set_state(AddHabit.day_of_month)
        await callback_query.message.answer("Enter the day of the month (1-31):")


# Callback query handler for day of the week options
@router.callback_query(lambda call: call.data.startswith("day_of_week_"))
async def day_of_week_callback(callback_query: types.CallbackQuery, state: FSMContext):
    day_of_week = callback_query.data.split("_")[3]
    await state.update_data(day_of_week=day_of_week)
    await state.set_state(AddHabit.time)
    await callback_query.message.answer("Enter the time in HH:MM format:")


# Handler to capture day of the month
@router.message(AddHabit.day_of_month)
async def get_day_of_month(message: types.Message, state: FSMContext):
    try:
        day_of_month = int(message.text.strip())
        if 1 <= day_of_month <= 31:
            await state.update_data(day_of_month=day_of_month)
            await state.set_state(AddHabit.time)
            await message.answer("Enter the time in HH:MM format:")
        else:
            await message.answer("Invalid day. Please enter a day of the month (1-31):")
    except ValueError:
        await message.answer(
            "Invalid input. Please enter a day of the month as a number (1-31):"
        )


# Handler to capture date in YYYY-MM-DD format
@router.message(AddHabit.date)
async def get_habit_date(message: types.Message, state: FSMContext):
    date_str = message.text.strip()

    try:
        # Validate date format
        year, month, day = map(int, date_str.split("-"))
        if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
            await state.update_data(date=date_str)
            await state.set_state(AddHabit.time)
            await message.answer("Enter the time in HH:MM format:")
        else:
            await message.answer(
                "Invalid date. Please enter the date in YYYY-MM-DD format (e.g., 2023-10-05):"
            )
    except ValueError:
        await message.answer(
            "Invalid format. Please enter the date in YYYY-MM-DD format (e.g., 2023-10-05):"
        )


# Handler to capture time in HH:MM format
@router.message(AddHabit.time)
async def get_habit_time(message: types.Message, state: FSMContext):
    time_str = message.text.strip()

    try:
        # Validate time format
        hours, minutes = map(int, time_str.split(":"))
        if 0 <= hours < 24 and 0 <= minutes < 60:
            await state.update_data(time=time_str)
            habit_data = await state.get_data()
            user_id = message.from_user.id
            if user_id not in user_data:
                user_data[user_id] = []
            user_data[user_id].append(habit_data)
            await state.clear()
            await message.answer("Habit added successfully!")
        else:
            await message.answer(
                "Invalid time. Please enter the time in HH:MM format (e.g., 14:30):"
            )
    except ValueError:
        await message.answer(
            "Invalid format. Please enter the time in HH:MM format (e.g., 14:30):"
        )


# Function to get ordinal suffix for day of the month
def get_ordinal_suffix(day):
    if 10 <= day % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return suffix
