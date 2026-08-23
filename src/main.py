import time
from typing import List
from fastapi import FastAPI, HTTPException, Request, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from src.core.logger import logger
from src.core.config import settingsAI
from src.rag.services import RAGService, DocumentService, AIService
from src.rag.repositories import QdrantRepository, ElasticRepository
from src.rag.repositories.context_enricher import ContextEnricher
from src.rag.retrievers import VectorRetriever, BM25Retriever, HybridRetriever
from src.core.ai_config import AIServiceConfig
from src.api.deps import RAGDep, DocumentDep
from src.api.routes import router_vector_repo, router_keyword_repo
from src.api.schemas import QuerySchema


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запускаем приложение...")
    ai_config = settingsAI.build_ai_config()
    ai_service = AIService(ai_config)
    
    app.state.repo = QdrantRepository(embedder=ai_service.embedder)
    app.state.keyword_repo = ElasticRepository()
    enricher = ContextEnricher(app.state.repo)

    vector_retriever = VectorRetriever(app.state.repo)
    keyword_retriever = BM25Retriever(app.state.keyword_repo)
    hybrid_retriever = HybridRetriever([vector_retriever, keyword_retriever])

    # app.state.document_service = DocumentService(
    #     app.state.repo,
    #     app.state.keyword_repo,
    #     model="sentence-transformers/all-MiniLM-L6-v2",
    # )
    app.state.rag_service = RAGService(ai_service, hybrid_retriever, enricher)
    logger.info("Приложение запущено!")

    yield

    logger.info("Останавливаем приложение...")
    await app.state.repo.close()
    await app.state.keyword_repo.close()
    logger.info("Приложение остановлено!")


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
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <title>RAG Search</title>

            <style>
                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    min-height: 100vh;
                    font-family: Arial, sans-serif;
                    background: #f5f6f8;

                    display: flex;
                    justify-content: center;
                    align-items: center;
                }

                .container {
                    width: 100%;
                    max-width: 700px;
                    padding: 32px;
                    background: white;
                    border-radius: 16px;
                    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
                }

                h1 {
                    margin: 0 0 8px;
                    font-size: 24px;
                }

                .description {
                    margin: 0 0 24px;
                    color: #6b7280;
                }

                label {
                    display: block;
                    margin-bottom: 8px;
                    font-weight: 600;
                }

                textarea {
                    width: 100%;
                    min-height: 110px;
                    padding: 14px;
                    border: 1px solid #d1d5db;
                    border-radius: 10px;
                    resize: vertical;
                    font-size: 15px;
                    font-family: inherit;
                    outline: none;
                }

                textarea:focus {
                    border-color: #2563eb;
                }

                button {
                    width: 100%;
                    margin-top: 12px;
                    padding: 13px;
                    border: none;
                    border-radius: 10px;
                    background: #2563eb;
                    color: white;
                    font-size: 15px;
                    cursor: pointer;
                }

                button:hover {
                    background: #1d4ed8;
                }

                button:disabled {
                    background: #93c5fd;
                    cursor: not-allowed;
                }

                .answer {
                    margin-top: 24px;
                }

                #answer {
                    min-height: 160px;
                    padding: 16px;
                    background: #f9fafb;
                    border: 1px solid #e5e7eb;
                    border-radius: 10px;
                    line-height: 1.6;
                    white-space: pre-wrap;
                }
            </style>
        </head>

        <body>

            <div class="container">
                <h1>RAG Search</h1>
                <p class="description">
                    Задайте вопрос по базе документов
                </p>

                <label for="query">Вопрос</label>

                <textarea
                    id="query"
                    placeholder="Введите ваш вопрос..."
                ></textarea>

                <button id="send" onclick="search()">
                    Найти ответ
                </button>

                <div class="answer">
                    <label>Ответ</label>
                    <div id="answer">
                        Ответ появится здесь
                    </div>
                </div>
            </div>

            <script>
                async function search() {
                    const query = document.getElementById("query").value.trim();
                    const answer = document.getElementById("answer");
                    const button = document.getElementById("send");

                    if (!query) {
                        return;
                    }

                    button.disabled = true;
                    button.textContent = "Поиск...";
                    answer.textContent = "Ищу ответ...";

                    try {
                        const resp = await fetch("/search", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({
                                query: query,
                                collection_name: "sber_docs"
                            })
                        });

                        if (!resp.ok) {
                            throw new Error("Server error");
                        }

                        const data = await resp.json();
                        answer.textContent = data.answer;

                    } catch (error) {
                        answer.textContent =
                            "Произошла ошибка при получении ответа.";
                    } finally {
                        button.disabled = false;
                        button.textContent = "Найти ответ";
                    }
                }
            </script>

        </body>
        </html>
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
    answer = await rag_service.run(query_data.query, query_data.collection_name, retrieve_limit=30)
    if not answer:
        raise HTTPException(status_code=500, detail="Ошибка ответа либо ответа нет")
    return answer


app.include_router(router_vector_repo)
app.include_router(router_keyword_repo)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
