import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory

from src.core.config import settingsAI

auth_data = settingsAI.get_auth_data


class LLMGenerator:
    def __init__(
        self,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 512,
    ):
        llm = ChatOpenAI(
            model=model,
            api_key=auth_data["API_KEY"],
            base_url=auth_data["BASE_URL"],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        history = InMemoryChatMessageHistory()
        self.chat = RunnableWithMessageHistory(llm, lambda _: history)

    async def generate(self, query: str, chat_id: str):
        config = {"configurable": {"session_id": chat_id}}
        response = await self.chat.ainvoke(query, config=config)
        return response


async def main():
    llm = LLMGenerator(model="openai/gpt-4o-mini")
    print("Диалог")
    while True:
        user_input = await asyncio.to_thread(input, "Вы: ")
        if user_input.lower() == "exit":
            break
        result = await llm.generate(query=user_input, chat_id="1")
        print(f"Бот: {result.content}")


if __name__ == "__main__":
    asyncio.run(main())
