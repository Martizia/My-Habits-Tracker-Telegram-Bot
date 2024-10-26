from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from os import getenv
import logging

TOKEN = getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# Set up logging
logging.basicConfig(level=logging.INFO)

# A dictionary to store user habits
user_data = {}


# Command handler for /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Welcome to the Habit Tracker Bot! Use /menu to manage your habits."
    )


# Command handler for /menu
@dp.message(Command("menu"))
async def menu(message: types.Message):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Add Habit", callback_data="add_habit")
    keyboard_builder.button(text="Edit Habit", callback_data="edit_habit")
    keyboard_builder.button(text="Delete Habit", callback_data="delete_habit")
    keyboard_builder.button(text="View Habits", callback_data="view_habits")
    keyboard = keyboard_builder.as_markup()

    await message.answer("Select an option:", reply_markup=keyboard)


# Callback query handler for menu options
@dp.callback_query(
    lambda call: call.data in ["add_habit", "edit_habit", "delete_habit", "view_habits"]
)
async def menu_callback(callback_query: types.CallbackQuery, state: FSMContext):
    option = callback_query.data

    if option == "add_habit":
        await state.set_state(AddHabit.name)
        await callback_query.message.answer("Enter the name of the habit:")
    elif option == "edit_habit":
        await callback_query.message.answer("Select a habit to edit:")
        # Code for editing habit
    elif option == "delete_habit":
        await callback_query.message.answer("Select a habit to delete:")
        # Code for deleting habit
    elif option == "view_habits":
        user_id = callback_query.from_user.id
        habits = user_data.get(user_id, [])
        if not habits:
            await callback_query.message.answer("No habits found.")
        else:
            for i, habit in enumerate(habits):
                habit_list = f"{i + 1}. {habit['name']}, {habit['schedule']}"
                if habit.get("day_of_week"):
                    habit_list += f" every {habit['day_of_week']}"
                elif habit.get("day_of_month"):
                    day_of_month = habit["day_of_month"]
                    suffix = get_ordinal_suffix(day_of_month)
                    habit_list += f" on the {day_of_month}{suffix}"
                habit_list += f" at {habit['time']}"
                await callback_query.message.answer(habit_list)


# Define states for adding a habit
class AddHabit(StatesGroup):
    name = State()
    schedule = State()
    day_of_week = State()
    day_of_month = State()
    time = State()


# Handler to capture habit name
@dp.message(AddHabit.name)
async def get_habit_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    habit_name = message.text
    await state.update_data(name=habit_name)
    await state.set_state(AddHabit.schedule)
    await message.answer(
        "Choose a repeat schedule:\n1. Once\n2. Every day\n3. Specific day of the week\n4. Specific day of the month"
    )


# Handler to capture habit schedule
@dp.message(AddHabit.schedule)
async def get_habit_schedule(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    schedule_input = message.text.strip().lower()

    # Process user's choice
    if schedule_input in ["1", "once"]:
        await state.update_data(schedule="once")
        await state.set_state(AddHabit.time)
        await message.answer("Enter the time in HH:MM format:")

    elif schedule_input in ["2", "every day"]:
        await state.update_data(schedule="every day")
        await state.set_state(AddHabit.time)
        await message.answer("Enter the time in HH:MM format:")

    elif schedule_input in ["3", "specific day of the week"]:
        await state.update_data(schedule="weekly")
        await state.set_state(AddHabit.day_of_week)
        await message.answer("Enter the day of the week (e.g., Monday, Tuesday):")

    elif schedule_input in ["4", "specific day of the month"]:
        await state.update_data(schedule="monthly")
        await state.set_state(AddHabit.day_of_month)
        await message.answer("Enter the day of the month (1-31):")

    else:
        await message.answer(
            "Invalid input. Please select a repeat schedule:\n1. Once\n2. Every day\n3. Specific day of the week\n4. Specific day of the month"
        )


# Handler to capture day of the week
@dp.message(AddHabit.day_of_week)
async def get_day_of_week(message: types.Message, state: FSMContext):
    day_of_week = message.text.strip().capitalize()

    if day_of_week in [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]:
        await state.update_data(day_of_week=day_of_week)
        await state.set_state(AddHabit.time)
        await message.answer("Enter the time in HH:MM format:")
    else:
        await message.answer(
            "Invalid day. Please enter a valid day of the week (e.g., Monday, Tuesday):"
        )


# Handler to capture day of the month
@dp.message(AddHabit.day_of_month)
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


# Handler to capture time in HH:MM format
@dp.message(AddHabit.time)
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


# Run the bot
if __name__ == "__main__":
    dp.run_polling(bot)
