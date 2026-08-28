import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.logger import logger
from src.services import RAGService, AIService, CollectionService, S3Service
from src.rag.repositories import QdrantRepository, ElasticRepository
from src.rag.repositories.context_enricher import ContextEnricher
from src.rag.retrievers import VectorRetriever, BM25Retriever, HybridRetriever
from src.api.exception_handlers import register_exception_handlers
from src.api.routes import router_vector_repo, router_keyword_repo, router_admin_repo, router_ingest, router_health
from src.broker.publisher import RabbitMQPublisher
from src.db.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запускаем приложение...")
    ai_service = AIService()

    publisher = RabbitMQPublisher()
    await publisher.connect()
    await publisher.setup_topology()
    app.state.publisher = publisher

    app.state.s3_service = S3Service()
    
    app.state.repo = QdrantRepository(embedder=ai_service.embedder)
    app.state.keyword_repo = ElasticRepository()
    enricher = ContextEnricher(app.state.repo)

    vector_retriever = VectorRetriever(app.state.repo)
    keyword_retriever = BM25Retriever(app.state.keyword_repo)
    hybrid_retriever = HybridRetriever([vector_retriever, keyword_retriever])

    app.state.rag_service = RAGService(ai_service, hybrid_retriever, enricher)
    logger.info("Приложение запущено!")

    yield

    logger.info("Останавливаем приложение...")
    await engine.dispose()
    await app.state.publisher.close()
    await app.state.repo.close()
    await app.state.keyword_repo.close()    
    logger.info("Приложение остановлено!")


app = FastAPI(lifespan=lifespan, title="RAG Service API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)

register_exception_handlers(app)

app.include_router(router_vector_repo, prefix="/api/v1")
app.include_router(router_keyword_repo, prefix="/api/v1")
app.include_router(router_admin_repo, prefix="/api/v1")
app.include_router(router_ingest, prefix="/api/v1")
app.include_router(router_health, prefix="/api/v1")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start
    response.headers["X-Process-Time"] = str(process_time)
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
