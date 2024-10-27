from aiogram import types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.shared import user_data

router = Router()


# Define states for editing the habit
class EditHabit(StatesGroup):
    select_habit = State()  # Which habit to edit
    select_field = State()  # What to edit (name/time/date/day_of_week/day_of_month)
    edit_name = State()
    edit_time = State()
    edit_date = State()
    edit_day_of_week = State()
    edit_day_of_month = State()


# Function to display edit habit menu
async def edit_habit_menu(message: types.Message, state: FSMContext):
    await state.set_state(EditHabit.select_habit)
    user_id = message.from_user.id
    habits = user_data.get(user_id, [])
    if not habits:
        await message.answer("No habits found.")
        await state.clear()
        return

    keyboard_builder = InlineKeyboardBuilder()
    for i, habit in enumerate(habits):
        habit_name = habit.get("name", "Unknown Habit")
        keyboard_builder.button(text=habit_name, callback_data=f"select_habit_{i}")
    keyboard_builder.adjust(1)
    keyboard = keyboard_builder.as_markup()
    await message.answer("Select a habit to edit:", reply_markup=keyboard)


# Callback query handler for selecting which habit to edit
@router.callback_query(
    EditHabit.select_habit, lambda call: call.data.startswith("select_habit_")
)
async def edit_habit_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    habit_index = int(callback_query.data.split("_")[2])
    habits = user_data.get(user_id, [])

    if 0 <= habit_index < len(habits):
        habit = habits[habit_index]
        await state.update_data(habit_index=habit_index)
        await state.set_state(EditHabit.select_field)

        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(text="Name", callback_data="edit_name")
        keyboard_builder.button(text="Time", callback_data="edit_time")
        if "date" in habit:
            keyboard_builder.button(text="Date", callback_data="edit_date")
        if "day_of_week" in habit:
            keyboard_builder.button(
                text="Day of Week", callback_data="edit_day-of-week"
            )
        if "day_of_month" in habit:
            keyboard_builder.button(
                text="Day of Month", callback_data="edit_day-of-month"
            )
        keyboard_builder.adjust(1)
        keyboard = keyboard_builder.as_markup()
        await callback_query.answer()
        await callback_query.message.answer(
            "What do you want to edit?", reply_markup=keyboard
        )
    else:
        await callback_query.message.answer("Invalid habit selection.")
        await state.clear()


# Callback query handler for selecting what to edit
@router.callback_query(
    EditHabit.select_field, lambda call: call.data.startswith("edit_")
)
async def edit_select_callback(callback_query: types.CallbackQuery, state: FSMContext):
    option = callback_query.data.split("_")[1]

    # Store the edit type for later use
    await state.update_data(edit_type=option)

    if option == "name":
        await state.set_state(EditHabit.edit_name)
        await callback_query.answer()
        await callback_query.message.answer("Enter the new name for the habit:")
    elif option == "time":
        await state.set_state(EditHabit.edit_time)
        await callback_query.answer()
        await callback_query.message.answer("Enter the new time in HH:MM format:")
    elif option == "date":
        await state.set_state(EditHabit.edit_date)
        await callback_query.answer()
        await callback_query.message.answer("Enter the new date in YYYY-MM-DD format:")
    elif option == "day-of-week":
        await state.set_state(EditHabit.edit_day_of_week)
        await callback_query.answer()
        await callback_query.message.answer(
            "Select the new day of the week:",
            reply_markup=create_day_of_week_keyboard(),
        )
    elif option == "day-of-month":
        await state.set_state(EditHabit.edit_day_of_month)
        await callback_query.answer()
        await callback_query.message.answer("Enter the new day of the month:")


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
        await state.clear()


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
        await state.clear()


# Handler to capture new habit date
@router.message(EditHabit.edit_date)
async def get_new_habit_date(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_habit_date = message.text
    habit_data = await state.get_data()
    habit_index = habit_data.get("habit_index")
    habits = user_data.get(user_id, [])

    if 0 <= habit_index < len(habits):
        habits[habit_index]["date"] = new_habit_date
        await state.clear()
        await message.answer("Habit date updated successfully!")
    else:
        await message.answer("Invalid habit selection.")
        await state.clear()


def create_day_of_week_keyboard():
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
        keyboard_builder.button(text=day, callback_data=f"day_{day}")
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


# Handler to capture new habit day of week
@router.callback_query(
    EditHabit.edit_day_of_week, lambda call: call.data.startswith("day_")
)
async def get_new_habit_day_of_week(
    callback_query: types.CallbackQuery, state: FSMContext
):
    user_id = callback_query.from_user.id
    new_day_of_week = callback_query.data.split("_")[1]
    habit_data = await state.get_data()
    habit_index = habit_data.get("habit_index")
    habits = user_data.get(user_id, [])

    if 0 <= habit_index < len(habits):
        habits[habit_index]["day_of_week"] = new_day_of_week
        await state.clear()
        await callback_query.answer()
        await callback_query.message.answer("Habit day of week updated successfully!")
    else:
        await callback_query.message.answer("Invalid habit selection.")
        await state.clear()


# Handler to capture new habit day of month
@router.message(EditHabit.edit_day_of_month)
async def get_new_habit_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_day_of_month = int(message.text)
    habit_data = await state.get_data()
    habit_index = habit_data.get("habit_index")
    habits = user_data.get(user_id, [])

    if 0 <= habit_index < len(habits):
        habits[habit_index]["day_of_month"] = new_day_of_month
        await state.clear()
        await message.answer("Habit day of the month updated successfully!")
    else:
        await message.answer("Invalid habit selection.")
        await state.clear()
