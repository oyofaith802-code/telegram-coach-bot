import asyncio
import logging
import json
import os
from datetime import date

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

# ---------------- TOKEN (PRODUCTION SAFE) ----------------
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("BOT TOKEN NOT FOUND. Set environment variable TOKEN.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------- MEMORY FILE ----------------
MEMORY_FILE = "memory.json"


# ---------------- LOAD MEMORY ----------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ---------------- SAVE MEMORY (SAFE) ----------------
def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


memory = load_memory()


# ---------------- INIT USER ----------------
def init_user(user_id: str):
    if user_id not in memory:
        memory[user_id] = {
            "goal": None,
            "streak": 0,
            "last_active": None
        }
        save_memory(memory)

    memory[user_id].setdefault("goal", None)
    memory[user_id].setdefault("streak", 0)
    memory[user_id].setdefault("last_active", None)


# ---------------- START COMMAND ----------------
@dp.message(CommandStart())
async def start_handler(message: Message):
    user_id = str(message.from_user.id)
    init_user(user_id)

    user = memory[user_id]

    if user["goal"]:
        await message.answer(
            f"""
🔥 STRICT COACH MODE

GOAL: {user['goal']}
STREAK: {user['streak']} days

Did you complete today's task? (Yes/No)
"""
        )
    else:
        await message.answer(
            "🔥 STRICT COACH MODE ACTIVE\n\nSend me your goal."
        )


# ---------------- MAIN COACH LOGIC ----------------
@dp.message()
async def coach_handler(message: Message):
    try:
        user_id = str(message.from_user.id)
        init_user(user_id)

        text = message.text.lower()
        today = str(date.today())

        user = memory[user_id]

        # ---------------- CHECK-IN SYSTEM ----------------
        if user["goal"] and text in ["yes", "no"]:
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

        # ---------------- SET GOAL ----------------
        if not user["goal"]:
            user["goal"] = message.text
            user["streak"] = 0
            user["last_active"] = None

            save_memory(memory)

            await message.answer(
                f"""
🔥 GOAL SET

{message.text}

ACTION PLAN:
1. Work daily on your goal
2. Complete at least 1 task per day
3. Never break streak twice in a row

Now answer:
Did you complete today's task? (Yes/No)
"""
            )
            return

        # ---------------- DEFAULT RESPONSE ----------------
        await message.answer(
            f"""
GOAL: {user['goal']}
STREAK: {user['streak']} days

Did you complete today's task? (Yes/No)
"""
        )

    except Exception as e:
        logging.error(str(e))
        await message.answer("⚠️ Error occurred but system recovered. Try again.")


# ---------------- DAILY REMINDER SYSTEM ----------------
async def daily_reminder():
    while True:
        await asyncio.sleep(3600)  # every 1 hour (production-safe)

        today = str(date.today())

        for user_id, data in memory.items():
            if data["goal"] and data["last_active"] != today:
                try:
                    await bot.send_message(
                        user_id,
                        f"""
⏰ DAILY REMINDER

GOAL: {data['goal']}
STREAK: {data['streak']} days

Did you complete today's task? (Yes/No)
"""
                    )
                except:
                    pass


# ---------------- MAIN ENTRY ----------------
async def main():
    logging.basicConfig(level=logging.INFO)
    print("Bot is running...")

    asyncio.create_task(daily_reminder())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())