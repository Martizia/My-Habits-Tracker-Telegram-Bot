from aiogram import types, Router

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.shared import user_data

router = Router()


# Define states for editing the habit
class EditHabit(StatesGroup):
    edit_select = State()
    edit_name = State()
    edit_time = State()
    edit_date = State()


# Function to display edit habit menu
async def edit_habit_menu(message: types.Message, state: FSMContext):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Name", callback_data="edit_name")
    keyboard_builder.button(text="Time", callback_data="edit_time")
    # keyboard_builder.button(text="Date", callback_data="edit_date")
    keyboard_builder.adjust(1)
    keyboard = keyboard_builder.as_markup()
    await message.answer("What do you want to edit?", reply_markup=keyboard)


# Callback query handler for selecting what to edit
@router.callback_query(lambda call: call.data.startswith("edit_"))
async def edit_select_callback(callback_query: types.CallbackQuery, state: FSMContext):
    option = callback_query.data.split("_")[1]

    if option == "name":
        await state.set_state(EditHabit.edit_name)
    elif option == "time":
        await state.set_state(EditHabit.edit_time)
    # elif option == "date":
    #     await state.set_state(EditHabit.edit_date)

    user_id = callback_query.from_user.id
    habits = user_data.get(user_id, [])
    if not habits:
        await callback_query.message.answer("No habits found.")
    else:
        keyboard_builder = InlineKeyboardBuilder()
        for i, habit in enumerate(habits):
            habit_name = habit.get("name", "Unknown Habit")
            keyboard_builder.button(text=habit_name, callback_data=f"edit_habit_{i}")
        keyboard_builder.adjust(1)
        keyboard = keyboard_builder.as_markup()
        await callback_query.message.answer(
            "Select a habit to edit:", reply_markup=keyboard
        )


# Callback query handler for editing a habit
@router.callback_query(lambda call: call.data.startswith("edit_habit_"))
async def edit_habit_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    habit_index = int(callback_query.data.split("_")[2])
    habits = user_data.get(user_id, [])
    if 0 <= habit_index < len(habits):
        await state.update_data(habit_index=habit_index)
        current_state = await state.get_state()
        if current_state == EditHabit.edit_name.state:
            await callback_query.message.answer("Enter the new name for the habit:")
        elif current_state == EditHabit.edit_time.state:
            await callback_query.message.answer("Enter the new time in HH:MM format:")
        # elif current_state == EditHabit.edit_date.state:
        #     await callback_query.message.answer(
        #         "Enter the new date in YYYY-MM-DD format:"
        #     )
    else:
        await callback_query.message.answer("Invalid habit selection.")


# Handler to capture new habit name
@router.message(EditHabit.edit_name)
async def get_new_habit_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_habit_name = message.text
    habit_data = await state.get_data()
    habit_index = habit_data.get("habit_index")
    habits = user_data.get(user_id, [])
    if 0 <= habit_index < len(habits):
        habits[habit_index]["name"] = new_habit_name
        await state.clear()
        await message.answer("Habit name updated successfully!")
    else:
        await message.answer("Invalid habit selection.")


# Handler to capture new habit time
@router.message(EditHabit.edit_time)
async def get_new_habit_time(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_habit_time = message.text
    habit_data = await state.get_data()
    habit_index = habit_data.get("habit_index")
    habits = user_data.get(user_id, [])
    if 0 <= habit_index < len(habits):
        habits[habit_index]["time"] = new_habit_time
        await state.clear()
        await message.answer("Habit time updated successfully!")
    else:
        await message.answer("Invalid habit selection.")


# Handler to capture new habit date
# @router.message(EditHabit.edit_date)
# async def get_new_habit_date(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     new_habit_date = message.text
#     habit_data = await state.get_data()
#     habit_index = habit_data.get("habit_index")
#     habits = user_data.get(user_id, [])
#     if 0 <= habit_index < len(habits):
#         habits[habit_index]["date"] = new_habit_date
#         await state.clear()
#         await message.answer("Habit date updated successfully!")
#     else:
#         await message.answer("Invalid habit selection.")
