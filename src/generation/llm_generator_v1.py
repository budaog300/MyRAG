import aiohttp
import asyncio

from src.core.config import settingsAI

auth_data = settingsAI.get_auth_data


class LLMGenerator:
    def __init__(self, model: str):
        self.model = model

    async def generate(
        self,
        query: str,
        context: list[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 512,
    ):
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": "Запрос: {query}\n\nКонтекст: {context}".format(
                        query=query, context="\n\n".join(context)
                    ),
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_data['API_KEY']}",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=auth_data["API_URL"], headers=headers, json=data
                ) as response:
                    # print(response.status)
                    result = await response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Ошибка при генерации ответа: {e}")
            raise e


async def main():
    llm = LLMGenerator(model="openai/gpt-4o-mini")
    result = await llm.generate(query="Привет", context=["Жопа", "Груша"])
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

    # async def generate(
    #     self, query: str, context: str, temperature: float = 0.3, max_tokens: int = 512
    # ):
    #     try:
    #         response = await client.chat.completions.create(
    #             model="openai/gpt-4o-mini",  # openai/gpt-4o-mini  openai/gpt-4.1-nano
    #             messages=[
    #                 # {"role": "system", "content": system_prompt},
    #                 {"role": "user", "content": f"{prompt}"}
    #             ],
    #             temperature=temperature,
    #             max_tokens=max_tokens,
    #         )
    #         return response.choices[0].message.content
    #     except Exception as e:
    #         print(f"Ошибка при генерации ответа: {e}")
    #         raise e
