from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from gigachat import GigaChat
import os
from dotenv import load_dotenv
import random
import json
import asyncio

load_dotenv()

GIGACHAT_API_KEY = os.getenv('GIGACHAT_API_KEY')
BOT_TOKEN = os.getenv('BOT_TOKEN')

if GIGACHAT_API_KEY is None:
    raise ValueError("GIGACHAT_API_KEY environment variable not set")
if BOT_TOKEN is None:
        raise ValueError("BOT_TOKEN environment variable not set")

llm = GigaChat(credentials=GIGACHAT_API_KEY,
               verify_ssl_certs=False,
               model="GigaChat:latest")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

message_history = {}
prompt = "Ты являешься участником чата. Тебе нужно принимать участие в обсуждении чего либо так, будто ты Тайлер Дерден. К тебе поступают сообщения в формате json, где указано, кто написал сообщение и текст сообщения. Тебе нужно отвечать так, будто ты участник чата - просто текст сообщения. То есть ты просто человек и ты отвечаешь как будто ты Тайлер Дерден"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот активирован и готов считать сообщения!")

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
        history = json.dumps(message_history, ensure_ascii=False)
        resp = llm.chat(prompt + history)
        await bot.send_message(
            chat_id=chat_id,
            text=f"{resp.choices[0].message.content}"
        )
        message_history[chat_id] = []

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
