from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import aiohttp

from src.core.config import settingsBot

auth_data = settingsBot.get_auth_data
TOKEN = auth_data["TELEGRAM_BOT_TOKEN"]
API_URL = "http://localhost:8000/search"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Отправь мне вопрос, я передам его в RAG систему")


@dp.message()
async def handle_query(message: types.Message):
    user_query = message.text
    print(f"Получено: {user_query}")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            API_URL, json={"query": user_query, "collection_name": "sber_docs"}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                answer = data.get("answer", "Нет ответа")
            else:
                answer = f"Ошибка API: {resp.status}"

    await message.answer(answer)


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
