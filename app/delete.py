from aiogram import types, Router

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.shared import user_data


router = Router()


# Define states for deleting a habit
class DeleteHabit(StatesGroup):
    select_habit = State()


# Function to display delete habit menu
async def delete_habit_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    habits = user_data.get(user_id, [])
    if not habits:
        await message.answer("No habits found.")
    else:
        keyboard_builder = InlineKeyboardBuilder()
        for i, habit in enumerate(habits):
            habit_name = habit.get("name", "Unknown Habit")
            keyboard_builder.button(text=habit_name, callback_data=f"delete_habit_{i}")
        keyboard_builder.adjust(1)
        keyboard = keyboard_builder.as_markup()
        await message.answer("Select a habit to delete:", reply_markup=keyboard)


# Callback query handler for deleting a habit
@router.callback_query(lambda call: call.data.startswith("delete_habit_"))
async def delete_habit_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    habit_index = int(callback_query.data.split("_")[2])
    habits = user_data.get(user_id, [])
    if 0 <= habit_index < len(habits):
        deleted_habit = habits.pop(habit_index)
        await callback_query.message.answer(
            f"Habit '{deleted_habit['name']}' deleted successfully!"
        )
    else:
        await callback_query.message.answer("Invalid habit selection.")
