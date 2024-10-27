from aiogram import Bot, Dispatcher, Router

from aiogram.fsm.storage.memory import MemoryStorage
from os import getenv
import logging

from app.main import router as main_router
from app.add import router as add_router
from app.delete import router as delete_router
from app.edit import router as edit_router
from app.shared import user_data


TOKEN = getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)
router.include_router(main_router)
router.include_router(add_router)
router.include_router(delete_router)
router.include_router(edit_router)

# Set up logging
logging.basicConfig(level=logging.INFO)


# Run the bot
if __name__ == "__main__":
    dp.run_polling(bot)
