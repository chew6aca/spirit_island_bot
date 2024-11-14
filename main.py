import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import DeleteWebhook
from dotenv import load_dotenv

import spirit_handler

load_dotenv()
TOKEN = os.getenv('TOKEN')
dp = Dispatcher(storage=MemoryStorage())
bot = Bot(token=TOKEN)


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    dp.include_routers(spirit_handler.router,)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
