import uuid
import asyncio
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
from langchain_community.document_loaders import TextLoader
from typing import List, Dict, Any

from src.rag.repository import VectorBaseRepository, KeywordBaseRepository
from src.rag.schemas.document import RawDocumentSchema
from src.rag.services.converter_service_bad import DocumentConverterService


class DocumentService:
    def __init__(
        self,
        repo: VectorBaseRepository,
        keyword_repo: KeywordBaseRepository,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.repo = repo
        self.keyword_repo = keyword_repo
        self.model = model
        self.converter = DocumentConverterService()

    def _chunk_markdown(
        self,
        doc: RawDocumentSchema,
        markdown_text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ) -> List[Dict[str, Any]]:
        headers_to_split_on = [
            ("#", "Header_1"),
            ("##", "Header_2"),
            ("###", "Header_3"),
            ("####", "Header_4"),
        ]
        md_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False,  # Оставляем заголовки в тексте
        )
        header_splits = md_splitter.split_text(markdown_text)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n\n", "\n\n", "\n", ". ", " ", ""],
        )

        final_chunks = []
        chunk_index = 0

        for header_split in header_splits:
            sub_chunks = text_splitter.split_text(header_split.page_content)

            breadcrumbs = " > ".join(
                [str(v) for v in header_split.metadata.values()]
            )

            for sub_chunk in sub_chunks:
                context_prefix = (
                    f"[Источник: {doc.source} | Раздел: {breadcrumbs}]\n\n"
                    if breadcrumbs
                    else f"[Источник: {doc.source}]\n\n"
                )
                enriched_content = context_prefix + sub_chunk

                chunk_metadata = {
                    "chunk_id": str(uuid.uuid4()),
                    "doc_id": doc.doc_id,
                    "source": doc.source,
                    "chunk_index": chunk_index,
                    "breadcrumbs": breadcrumbs,
                    **header_split.metadata,
                    **doc.metadata,
                }

                final_chunks.append(
                    {
                        "content": enriched_content,
                        "raw_content": sub_chunk,
                        "metadata": chunk_metadata,
                    }
                )
                chunk_index += 1

        return final_chunks

    async def ingest_files(
        self,
        collection_name: str,
        documents: List[RawDocumentSchema],
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ):
        all_chunks = []

        for doc in documents:
            markdown_content = self.converter.convert_to_markdown(doc)

            chunks = self._chunk_markdown(
                doc=doc,
                markdown_text=markdown_content,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            all_chunks.extend(chunks)

        await asyncio.gather(
            self.repo.upsert(collection_name, all_chunks, model=self.model),
            self.keyword_repo.index_documents(collection_name, all_chunks),
        )