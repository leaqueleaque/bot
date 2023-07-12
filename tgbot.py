import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from config import BOT_API_TOKEN, ADMINS

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def introduction(message: types.Message):
    await message.answer(
        "<b>Вітаю вас у телеграм боті сповіщень з криптовалютної біржи leaque.com!</>"
        " \n\n<em>З цього моменту ви будете сповіщенні про всі дії юзері вашого сервісу!</em>",
        parse_mode="HTML"
                         )
    print(message.chat.id)
    ADMINS.append(message.chat.id)

