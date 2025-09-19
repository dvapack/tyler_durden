from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI
import os
from dotenv import load_dotenv
import random
import json
import asyncio

from reels_loader import DataLoader

load_dotenv()

BASE_URL = os.getenv('BASE_URL')
BOT_TOKEN = os.getenv('BOT_TOKEN')

if BASE_URL is None:
    raise ValueError("BASE_URL environment variable not set")
if BOT_TOKEN is None:
        raise ValueError("BOT_TOKEN environment variable not set")

loader = DataLoader("links.json")
loader.load_links()

client = OpenAI(base_url=BASE_URL, api_key="lm-studio")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

message_history = {}
prompt = "Ты являешься участником чата. Тебе нужно принимать участие в обсуждении чего либо так, будто ты Тайлер Дерден. К тебе поступают сообщения в формате json, где указано, кто написал сообщение и текст сообщения. Тебе нужно отвечать так, будто ты участник чата - просто текст сообщения. То есть ты просто человек и ты отвечаешь как будто ты Тайлер Дерден"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот активирован!")

@dp.message(Command("get_reels"))
async def send_reels(message: types.Message):
    if message.chat.type == "private" or message.from_user.is_bot:
        return

    chat_id = message.chat.id
    link = loader.get_reel()
    await bot.send_message(
        chat_id=chat_id,
        text=link
    )

@dp.message(Command("ask_gpt"))
async def ask_gpt(message: types.Message):
    if message.chat.type == "private" or message.from_user.is_bot:
        return

    question_text = message.text.replace('/ask_gpt', '').strip()

    if not question_text:
        await message.reply("Пожалуйста, задайте вопрос после команды /ask_gpt")
        return

    chat_id = message.chat.id
    question = {"question": message.text}
    question_dump = json.dumps(question, ensure_ascii=False)

    completion = client.chat.completions.create(
      model="model-identifier",
      messages=[
        {"role": "user", "content": question_dump}
      ],
      temperature=0.7,
    )
    response_text = completion.choices[0].message.content
    await message.reply(response_text)

@dp.message()
async def save_and_reply(message: types.Message):
    if message.chat.type == "private" or message.from_user.is_bot:
        return

    chat_id = message.chat.id

    if chat_id not in message_history:
        message_history[chat_id] = []

    msg_data = {
        "from_user": message.from_user.full_name,
        "text": message.text or "[медиа/стикер]"
    }
    message_history[chat_id].append(msg_data)

    random_num = random.randint(1, 10)
    if len(message_history[chat_id]) >= random_num:
        history = json.dumps(message_history[chat_id], ensure_ascii=False)
        completion = client.chat.completions.create(
          model="model-identifier",
          messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": history}
          ],
          temperature=0.7,
        )
        await bot.send_message(
            chat_id=chat_id,
            text=f"{completion.choices[0].message.content}"
        )
        message_history[chat_id] = []

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
