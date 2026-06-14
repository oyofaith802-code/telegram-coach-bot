import os
import asyncio
import logging
from datetime import date

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

import database as db

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN not found in environment variables")

bot = Bot(token=TOKEN)
dp = Dispatcher()


# -------------------------
# START
# -------------------------
@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id

    db.init_user(user_id)

    await message.answer(
        "Welcome to AI Coach Bot 🚀\n\n"
        "Use /setgoal to set your goal."
    )


# -------------------------
# SET GOAL
# -------------------------
@dp.message(Command("setgoal"))
async def set_goal(message: Message):
    await message.answer("Send me your goal in one message.")


# -------------------------
# SAVE GOAL
# -------------------------
@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text
    today = str(date.today())

    user = db.get_user(user_id)

    # if no goal yet → set it
    if not user["goal"]:
        db.set_goal(user_id, text)
        await message.answer(
            f"Goal saved ✅\n\nNow tell me daily: Did you complete it today? (Yes/No)"
        )
        return

    # check-in logic
    if text.lower() in ["yes", "no"]:
        if user["last_active"] == today:
            await message.answer("You already checked in today.")
            return

        if text.lower() == "yes":
            db.update_streak(user_id, user["streak"] + 1)
            reply = f"Good job 🔥 Streak: {user['streak'] + 1}"
        else:
            db.update_streak(user_id, 0)
            reply = "Streak reset ❌ Stay disciplined."

        db.set_last_active(user_id, today)

        await message.answer(reply)
        return

    await message.answer("Reply Yes or No.")


# -------------------------
# RUN
# -------------------------
async def main():
    logging.basicConfig(level=logging.INFO)
    print("Bot running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())