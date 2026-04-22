import time
from typing import List
from fastapi import FastAPI, HTTPException, Request, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from src.rag.services import RAGService, DocumentService
from src.rag.repository import QdrantRepository, ElasticRepository
from src.rag.retrieval import VectorRetriever, BM25Retriever, HybridRetriever
from src.api.deps import RAGDep, DocumentDep
from src.api.routes import router_vector_repo, router_keyword_repo
from src.api.schemas import QuerySchema


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.repo = QdrantRepository()
    app.state.keyword_repo = ElasticRepository()

    vector_retriever = VectorRetriever(app.state.repo)
    keyword_retriever = BM25Retriever(app.state.keyword_repo)
    hybrid_retriever = HybridRetriever([vector_retriever, keyword_retriever])

    app.state.document_service = DocumentService(
        app.state.repo,
        app.state.keyword_repo,
        model="sentence-transformers/all-MiniLM-L6-v2",
    )
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


# @app.post("/ingest", summary="Загрузить документацию")
# async def ingest(
#     doc_service: DocumentDep,
#     collection_name: str = Form(...),
#     chunk_size: int = Form(1000),
#     chunk_overlap: int = Form(300),
#     documents: list[UploadFile] = File(..., description="Files"),
# ):
#     # document_data = IngestDataSchema(
#     #     collection_name=collection_name,
#     #     chunk_size=chunk_size,
#     #     chunk_overlap=chunk_overlap,
#     # )

#     print(documents)
#     return await doc_service.ingest_files(
#         collection_name, documents, chunk_size, chunk_overlap
#     )


@app.post("/search", summary="Запрос в документацию (RAG)")
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
