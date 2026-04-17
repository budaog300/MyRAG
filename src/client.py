import aiohttp
import asyncio


API_URL = "http://localhost:8000/search"


async def ask(query: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            API_URL, json={"query": query, "collection_name": "sber_docs"}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                answer = data.get("answer", "Нет ответа")
            else:
                answer = f"Ошибка API: {resp.status}"

    return answer


async def main():
    print("RAG Клиент (введи 'exit' для выхода)")
    while True:
        try:
            query = await asyncio.to_thread(input, "Введите запрос: ")
            if query.lower() == "exit":
                break
            answer = await ask(query)
            print(f"Бот: {answer}/n/n---------------------------------")
        except Exception as e:
            raise e


if __name__ == "__main__":
    asyncio.run(main())
