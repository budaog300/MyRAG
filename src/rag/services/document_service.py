import uuid
import asyncio
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
        splitter: BaseDocumentSplitter
    ):
        self.repo = repo
        self.keyword_repo = keyword_repo
        self.converter_service = converter_service
        self.splitter = splitter
        
    async def ingest_files(
        self,
        collection_name: str,
        documents: List[RawDocumentSchema],
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ) -> None:
        all_children: List[Dict[str, Any]] = []
        all_parents: List[Dict[str, Any]] = []

        for doc in documents:
            markdown_text = await self.converter_service.convert_to_markdown(doc.source)

            chunks = self.splitter.split(
                doc=doc,
                markdown_text=markdown_text,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            for chunk in chunks:
                chunk_dict = chunk.model_dump() if hasattr(chunk, 'model_dump') else chunk
                if chunk_dict.get("is_parent"):
                    all_parents.append(chunk_dict)
                else:
                    all_children.append(chunk_dict)

        tasks = [
            self.repo.upsert(collection_name, all_children, is_vector=True),
            self.keyword_repo.index_documents(collection_name, all_children)
        ]
        
        if all_parents:
            parents_collection_name = f"{collection_name}_parents"
            tasks.extend([
                self.repo.upsert(parents_collection_name, all_parents, is_vector=False),
                # self.keyword_repo.index_documents(parents_collection_name, all_parents)
            ])

        await asyncio.gather(*tasks)