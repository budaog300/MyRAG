import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from src.services.rag_service import RAGService
from src.schemas.schemas import QuerySchema
from src.repository import QdrantRepository, ElasticRepository
from src.retrieval import VectorRetriever, BM25Retriever, HybridRetriever
from src.core.deps import RAGDep
from src.repository.keyword_store.routes import router as router_vector_repo
from src.repository.vector_store.routes import router as router_keyword_repo


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.repo = QdrantRepository()
    app.state.keyword_repo = ElasticRepository()

    vector_retriever = VectorRetriever(app.state.repo)
    keyword_retriever = BM25Retriever(app.state.keyword_repo)
    hybrid_retriever = HybridRetriever(vector_retriever, keyword_retriever)

    app.state.rag_service = RAGService(hybrid_retriever, model="openai/gpt-4o-mini")
    yield
    await app.state.repo.close()
    await app.state.keyword_repo.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
async def get_chat_ui() -> HTMLResponse:
    return HTMLResponse(
        """
            <input id="query" placeholder="Вопрос">
            <button onclick="search()">Отправить</button>
            <div id="answer"></div>

            <script>
                async function search() {
                    const resp = await fetch("/search", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ query: query.value, collection_name: "sber_docs" })
                    });
                    const data = await resp.json();
                    answer.innerText = data.answer;
                }
            </script>
        """
    )


@app.get("/health", tags=["Проверка сервера"])
async def health():
    return {"message": "success"}


@app.post("/search", summary="Запрос в RAG")
async def rag_query(query_data: QuerySchema, rag_service: RAGDep):
    answer = await rag_service.run(query_data.query, query_data.collection_name)
    if not answer:
        raise HTTPException(status_code=500, detail="Ошибка ответа либо ответа нет")
    return answer


app.include_router(router_vector_repo)
app.include_router(router_keyword_repo)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
