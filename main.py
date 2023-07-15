import logging
from req_analyse import check_changes
from tgbot import dp
import asyncio
from config import BOT_API_TOKEN
from aiogram.utils.executor import start_webhook

# webhook
WEBHOOK_HOST = 'https://tg.leaque.com'  # Укажите URL-адрес вашего сервера (https://your.domain)
WEBHOOK_PATH = f"/bot"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver
WEBAPP_HOST = 'localhost'  # Укажите IP
WEBAPP_PORT = 9009  # Укажите порт


async def on_startup(dp):
    await dp.bot.set_webhook(WEBHOOK_URL)
    asyncio.create_task(check_changes())


async def on_shutdown(dp):
    logging.warning('Shutting down..')
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=False,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )

