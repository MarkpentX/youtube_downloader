import asyncio
import os

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import BufferedInputFile

from helpers import write_password, check_login, download_video, download_audio

TOKEN = "Enter your token here"
router = Router()


class YouTubeDownloadAudio(StatesGroup):
    url = State()


class YouTubeDownloadVideo(StatesGroup):
    url = State()


class Registration(StatesGroup):
    username = State()
    password = State()


class Login(StatesGroup):
    username = State()
    password = State()


@router.message(Command("start"))
async def start_handler(message: types.Message):
    kb = [
        [types.KeyboardButton(text="/registration")],
        [types.KeyboardButton(text="/login")],
        [types.KeyboardButton(text="/video")],
        [types.KeyboardButton(text="/audio")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Enter a command")
    await message.answer("Hello!", reply_markup=keyboard)


@router.message(Command("registration"))
async def registration_handler(message: types.Message, state: FSMContext):
    await message.answer("Hello\nPlease enter your username")
    await state.set_state(Registration.username)


@router.message(Registration.username)
async def username_handler(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Username added.\nPlease enter a password")
    await state.set_state(Registration.password)


@router.message(Registration.password)
async def password_handler(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    # we get the DATA you have been written
    user_data = await state.get_data()
    write_password(user_data["username"], user_data["password"])
    await message.answer("Password has been added. You can use the bot.")
    await state.clear()


@router.message(Command("login"))
async def registration_handler(message: types.Message, state: FSMContext):
    await message.answer("Hello\nPlease enter your login")
    await state.set_state(Login.username)


@router.message(Login.username)
async def username_handler(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Please enter a password")
    await state.set_state(Login.password)


@router.message(Login.password)
async def password_handler(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    # we get the DATA you have been written
    user_data = await state.get_data()
    result = check_login(user_data["username"], user_data["password"])

    if result:
        await message.answer(f"You have successfully logged in as {user_data['username']}")
    else:
        await message.answer("Invalid username or password")

    await state.clear()


@router.message(Command("video"))
async def video_handler(message: types.Message, state: FSMContext):
    await message.answer("Enter an youtube URL")
    await state.set_state(YouTubeDownloadVideo.url)


@router.message(YouTubeDownloadVideo.url)
async def url_handler(message: types.Message, state: FSMContext):
    await message.answer("Loading...")
    await state.update_data(url=message.text)
    user_data = await state.get_data()
    filename = message.from_user.username + ".mp4"

    result = download_video(user_data["url"], filename)
    if result:
        with open(f"{filename}", "rb") as file:
            await message.answer_video(
                BufferedInputFile(file.read(), filename=filename),
                caption="Your video:"
            )
        os.remove(filename)
    else:
        await message.answer("Invalid URL")


@router.message(Command("audio"))
async def audio_handler(message: types.Message, state: FSMContext):
    await message.answer("Enter youtube url audio")
    await state.set_state(YouTubeDownloadAudio.url)


@router.message(YouTubeDownloadAudio.url)
async def url_handler(message: types.Message, state: FSMContext):
    await message.answer("loading...")
    await state.update_data(url=message.text)
    user_data = await state.get_data()
    url = user_data["url"]

    filename = message.from_user.username + ".mp4"
    # result - True (audio has been downloaded) | False (Error)
    result = download_audio(url, filename)
    if result:
        audio_filename = filename.replace(".mp4", ".mp3")
        with open(audio_filename, "rb") as file:
            await message.answer_audio(
                BufferedInputFile(file.read(), filename=filename),
                caption="Your audio:"
            )
        os.remove(filename)
        os.remove(audio_filename)

    else:
        await message.answer("Invalid URL")


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())