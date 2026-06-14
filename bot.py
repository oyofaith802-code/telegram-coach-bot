import os
import asyncio
import logging
import json
from datetime import date

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message


TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("BOT TOKEN NOT FOUND. Set environment variable TOKEN.")
# =========================
# TOKEN (LOCAL TEST ONLY)
# =========================
TOKEN = "8917128981:AAE9XsMaaj1Xp1hQ-hAGBRw2ggw437eurIc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =========================
# MEMORY FILE
# =========================
MEMORY_FILE = "memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


memory = load_memory()


def init_user(user_id: str):
    if user_id not in memory:
        memory[user_id] = {
            "goal": None,
            "streak": 0,
            "last_active": None
        }
        save_memory(memory)


# =========================
# START COMMAND
# =========================
@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = str(message.from_user.id)
    init_user(user_id)

    user = memory[user_id]

    if user["goal"]:
        await message.answer(
            f"GOAL: {user['goal']}\nSTREAK: {user['streak']}\n\nDid you complete today? (Yes/No)"
        )
    else:
        await message.answer("Send me your goal to start strict coaching.")


# =========================
# MAIN LOGIC
# =========================
@dp.message()
async def coach_handler(message: Message):
    user_id = str(message.from_user.id)
    init_user(user_id)

    text = message.text.lower()
    today = str(date.today())

    user = memory[user_id]

    # SET GOAL
    if not user["goal"]:
        user["goal"] = message.text
        user["streak"] = 0
        user["last_active"] = None
        save_memory(memory)

        await message.answer(
            f"GOAL SET:\n{message.text}\n\nNow answer: Did you complete today? (Yes/No)"
        )
        return

    # DAILY CHECK-IN
    if text in ["yes", "no"]:
        if user["last_active"] == today:
            await message.answer("Already checked in today.")
            return

        if text == "yes":
            user["streak"] += 1
            reply = f"Good. Streak = {user['streak']} 🔥"
        else:
            user["streak"] = 0
            reply = "Streak reset ❌ Stay disciplined."

        user["last_active"] = today
        save_memory(memory)

        await message.answer(reply)
        return

    # DEFAULT RESPONSE
    await message.answer(
        f"GOAL: {user['goal']}\nSTREAK: {user['streak']}\n\nYes or No?"
    )


# =========================
# RUN BOT
# =========================
async def main():
    logging.basicConfig(level=logging.INFO)
    print("Bot is running...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())