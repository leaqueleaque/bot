from aiogram import executor, types, Dispatcher, Bot
from req_analyse import check_changes
from tgbot import dp, bot
import asyncio
from fastapi import FastAPI
from config import BOT_API_TOKEN

app = FastAPI()
WEBHOOK_HOST = 'https://your.domain'  # Write your domain
WEBHOOK_PATH = f"/bot/{BOT_API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"


@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )
    asyncio.create_task(check_changes())


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    Dispatcher.set_current(dp)
    Bot.set_current(bot)
    await dp.process_update(telegram_update)


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()

