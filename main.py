import asyncio
import locale
import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command

from add_excercises import add_exc
from excercises import rp
from history import hi
from utils import main_menu


load_dotenv()
TOKEN = os.getenv("TOKEN")


bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_routers(rp, add_exc, hi)
locale.setlocale(locale.LC_ALL, "")


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f'Привет {message.from_user.username}')
    await main_menu(message)


@dp.callback_query(F.data == "MainMenu")
async def callback_main(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        f'Привет {callback.from_user.username}')
    await main_menu(callback.message)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
