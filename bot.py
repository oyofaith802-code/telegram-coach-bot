import os
import asyncio
import logging
from datetime import date

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from rag import build, search
import database as db
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN not found")

bot = Bot(token=TOKEN)
dp = Dispatcher()


# -------------------------
# START
# -------------------------
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Send me your goal to start coaching.")


# -------------------------
# MAIN HANDLER
# -------------------------
@dp.message()
async def handler(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    today = str(date.today())

    user = db.get_user(user_id)

    if not user:
        user = {"goal": None, "streak": 0, "last_active": None}

    # 1. SET GOAL
    if not user.get("goal"):
        db.set_goal(user_id, text)
        await message.answer("Goal saved ✅\nNow answer daily: Yes / No")
        return

    # 2. CHECK-IN
    if text.lower() in ["yes", "no"]:

        if user.get("last_active") == today:
            await message.answer("Already checked in today.")
            return

        if text.lower() == "yes":
            new_streak = user.get("streak", 0) + 1
            db.update_streak(user_id, new_streak)
            reply = f"Good job 🔥 Streak: {new_streak}"
        else:
            db.update_streak(user_id, 0)
            reply = "Streak reset ❌ Stay disciplined."

        db.set_last_active(user_id, today)
        await message.answer(reply)
        return

    # 3. RAG RESPONSE
    results, _ = search(text)   # IMPORTANT FIX

    context = "\n\n".join(results)

    await message.answer(
        f"📚 From your coaching book:\n\n{context}\n\n---\n🧭 {text}"
    )


# -------------------------
# START BOT
# -------------------------
async def main():
    logging.basicConfig(level=logging.INFO)

    build()   # MUST RUN FIRST

    print("Bot running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())