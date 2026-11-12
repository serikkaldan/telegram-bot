import asyncio
import json
import logging
import random
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "7569121658:AAEIT6HNQORFgHEKfKXUS4eRgriVPluIIQg"

bot = Bot(token=TOKEN)
dp = Dispatcher()


# --- ДЕРЕКҚОРДЫ БАСҚАРУ (Қолданушылар өшпеуі үшін SQLite) ---
def init_db():
  conn = sqlite3.connect("users.db")
  cursor = conn.cursor()
  cursor.execute(
      """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
    """
  )
  conn.commit()
  conn.close()


def add_user(user_id: int):
  conn = sqlite3.connect("users.db")
  cursor = conn.cursor()
  cursor.execute(
      "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,)
  )
  conn.commit()
  conn.close()


# --- CONTENT.JSON ФАЙЛЫН ОҚУ ---
def load_content():
  try:
    with open("content.json", "r", encoding="utf-8") as f:
      return json.load(f)
  except FileNotFoundError:
    return {
        "history_today": ["Мәлімет әзірге жоқ."],
        "great_figures": ["Мәлімет әзірге жоқ."],
        "interesting_facts": ["Мәлімет әзірге жоқ."],
        "tests": [],
    }


# /start командасы (Арнаға тексерусіз бірден мәзір ашады)
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
  user_id = message.from_user.id
  add_user(user_id)  # Қолданушыны базаға сақтау

  # Қаласаңыз, осы жерге арнаға сілтеме жасайтын батырма қосып қоюға болады
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="📅 Бүгінгі күн тарихта", callback_data="history_today"
              )
          ],
          [
              InlineKeyboardButton(
                  text="👤 Ұлы тұлғалар", callback_data="great_figures"
              )
          ],
          [
              InlineKeyboardButton(
                  text="💡 Қызықты деректер", callback_data="interesting_facts"
              )
          ],
          [
              InlineKeyboardButton(
                  text="🧩 Тест сұрақтары", callback_data="start_test"
              )
          ],
          [
              InlineKeyboardButton(
                  text="📢 Біздің арна", url="https://t.me/jas_power_qsa"
              )
          ],
      ]
  )
  await message.answer(
      "Сәлем! Мен «ТАРИХ КҮНТІЗБЕСІ» телеграм ботымын! 📜\n\n"
      "Төмендегі мәзірден қажетті бөлімді таңдаңыз:",
      reply_markup=keyboard,
  )


@dp.callback_query(F.data == "history_today")
async def send_history(callback: types.CallbackQuery):
  content = load_content()
  fact = random.choice(content["history_today"])
  await callback.message.answer(fact, parse_mode="Markdown")
  await callback.answer()


@dp.callback_query(F.data == "great_figures")
async def send_figure(callback: types.CallbackQuery):
  content = load_content()
  figure = random.choice(content["great_figures"])
  await callback.message.answer(figure, parse_mode="Markdown")
  await callback.answer()


@dp.callback_query(F.data == "interesting_facts")
async def send_fact(callback: types.CallbackQuery):
  content = load_content()
  fact = random.choice(content["interesting_facts"])
  await callback.message.answer(fact, parse_mode="Markdown")
  await callback.answer()


@dp.callback_query(F.data == "start_test")
async def send_test(callback: types.CallbackQuery):
  content = load_content()
  if not content["tests"]:
    await callback.message.answer("Әзірге тест сұрақтары қосылмаған.")
    await callback.answer()
    return

  test_item = random.choice(content["tests"])

  keyboard_buttons = []
  for text, status in test_item["options"]:
    keyboard_buttons.append(
        [InlineKeyboardButton(text=text, callback_data=f"test_{status}")]
    )

  keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
  await callback.message.answer(
      test_item["question"], reply_markup=keyboard, parse_mode="Markdown"
  )
  await callback.answer()


@dp.callback_query(F.data.startswith("test_"))
async def check_test_answer(callback: types.CallbackQuery):
  action = callback.data.split("_")[1]
  if action == "correct":
    await callback.message.answer("Дұрыс! Керемет нәтиже! 🎉")
  else:
    await callback.message.answer("Қате, бірақ келесі жолы жолыңыз болады! 💪")
  await callback.answer()


async def main():
  init_db()  # Дерекқорды іске қосу
  logging.basicConfig(level=logging.INFO)
  print("«Тарих күнтізбесі» боты іске қосылды...")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())