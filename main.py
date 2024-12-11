import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove


from config import token
from funcs import workflow

TOKEN = token

dp = Dispatcher()
wf = workflow()
state = 0 # 1 - playlist, 2 - album, 3 - single song
logging.basicConfig(level=logging.INFO)

kb = [
    [
        types.KeyboardButton(text="Playlist"),
        types.KeyboardButton(text="Album"),
        types.KeyboardButton(text="Single song")
    ],
]
keyboard = types.ReplyKeyboardMarkup(
    keyboard=kb,
    resize_keyboard=True,
    input_field_placeholder="Choose type"
)



@dp.message(Command("start"))
async def command_start_handler(message: types.Message) -> None:
    await message.answer(f"Hello, {message.from_user.full_name}! Which type you want to download?", 
                        reply_markup=keyboard
                         )

@dp.message(F.text.lower() == "playlist")
async def setStatePS(message: types.Message):
    global state
    state = 1
    await message.answer("Send link to your playlist", reply_markup=ReplyKeyboardRemove())


@dp.message(F.text.lower() == "album")
async def setStateAL(message:types.Message):
    global state
    state = 2
    await message.answer("Send link to your album", reply_markup=ReplyKeyboardRemove())

@dp.message(F.text.lower() == "single song")
async def setStateSS(message:types.Message):
    global state
    state = 3
    await message.answer("Send link to your song", reply_markup=ReplyKeyboardRemove())


@dp.message(lambda message: message.text and message.text.startswith('http'))
async def downloadHandler(message: types.Message):
    global state
    if state:
        url = message.text
        songs = wf.get_playlist_list(url, state)
        state = 0
        await message.answer("Wait for downloading to end...")
        await wf.download_and_send_songs(songs, message)
        await message.answer("What do you want to download next? ", reply_markup=keyboard)
    else:
        await message.answer("You didn't pick your mode of donwloading!!")




async def main() -> None:
    bot = Bot(token=TOKEN)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())