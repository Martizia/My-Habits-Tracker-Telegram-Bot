from aiogram import types, Router

from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext

from app.add import AddHabit, get_ordinal_suffix
from app.delete import DeleteHabit, delete_habit_menu
from app.edit import EditHabit, edit_habit_menu
from app.shared import user_data

import logging


router = Router()

# user_data = {}


# Command handler for /start
@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Welcome to the Habit Tracker Bot! Use /menu to manage your habits."
    )


# Command handler for /menu
@router.message(Command("menu"))
async def menu(message: types.Message):
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text="Add Habit")
    keyboard_builder.button(text="Edit Habit")
    keyboard_builder.button(text="Delete Habit")
    keyboard_builder.button(text="View Habits")
    keyboard_builder.adjust(2)
    keyboard = keyboard_builder.as_markup(resize_keyboard=True)
    await message.answer("Select an option:", reply_markup=keyboard)


# Message handler for menu options
@router.message(
    lambda message: message.text
    in ["Add Habit", "Edit Habit", "Delete Habit", "View Habits"]
)
async def menu_message_handler(message: types.Message, state: FSMContext):
    option = message.text

    if option == "Add Habit":
        await state.set_state(AddHabit.name)
        await message.answer("Enter the name of the habit:")
    elif option == "Edit Habit":
        await state.set_state(EditHabit.edit_select)
        await edit_habit_menu(message, state)
    elif option == "Delete Habit":
        await state.set_state(DeleteHabit.select_habit)
        await delete_habit_menu(message, state)
    elif option == "View Habits":
        user_id = message.from_user.id
        habits = user_data.get(user_id, [])
        if not habits:
            await message.answer("No habits found.")
        else:
            for i, habit in enumerate(habits):
                try:
                    habit_list = f"{i + 1}. {habit['name']}, {habit['schedule']}"
                    if habit.get("date"):
                        habit_list += f" {habit['date']}"
                    elif habit.get("day_of_week"):
                        habit_list += f" every {habit['day_of_week']}"
                    elif habit.get("day_of_month"):
                        day_of_month = habit["day_of_month"]
                        suffix = get_ordinal_suffix(day_of_month)
                        habit_list += f" on the {day_of_month}{suffix}"
                    habit_list += f" at {habit['time']}"
                    await message.answer(habit_list)
                except KeyError as e:
                    logging.error(f"KeyError: {e} in habit {habit}")
                    await message.answer("Error displaying habit. Please try again.")
