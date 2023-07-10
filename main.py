from aiogram import executor
from req_analyse import check_changes
from tgbot import dp
import asyncio


async def on_startup(bd):
    asyncio.create_task(check_changes())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
