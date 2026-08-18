import uuid
import asyncio
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
from langchain_community.document_loaders import TextLoader
from typing import List, Dict, Any

from src.rag.components.splitters import BaseDocumentSplitter
from src.rag.services.convert_service import DocumentConverterService
from src.rag.schemas.document import RawDocumentSchema, RAGDocument
from src.rag.repositories import BaseVectorRepository
from src.rag.repositories import BaseKeywordRepository

class DocumentService:
    def __init__(
        self,
        repo: BaseVectorRepository,
        keyword_repo: BaseKeywordRepository,
        converter_service: DocumentConverterService,
        splitter: BaseDocumentSplitter,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.repo = repo
        self.keyword_repo = keyword_repo
        self.converter_service = converter_service
        self.splitter = splitter
        self.model = model

    async def ingest_files(
        self,
        collection_name: str,
        documents: List[RawDocumentSchema],
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ) -> None:
        all_chunks: List[RAGDocument] = []

        for doc in documents:
            markdown_content = await self.converter_service.convert_to_markdown(doc.source)

            chunks = self.splitter.split(
                doc=doc,
                markdown_text=markdown_content,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            all_chunks.extend([c.model_dump() if hasattr(c, 'model_dump') else c for c in chunks])

        await asyncio.gather(
            self.repo.upsert(collection_name, all_chunks, model=self.model),
            self.keyword_repo.index_documents(collection_name, all_chunks),
        )