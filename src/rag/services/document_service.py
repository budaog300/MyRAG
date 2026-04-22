import asyncio
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
from langchain_community.document_loaders import TextLoader
from typing import List

from src.rag.repository import VectorBaseRepository, KeywordBaseRepository
from src.rag.schemas.document import RawDocumentSchema


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

    def _chunk_docs(
        self,
        documents: List[RawDocumentSchema],
        chunk_size: int = 1000,
        chunk_overlap: int = 300,
        add_start_index: bool = True,
    ):
        all_splits = []
        md_spitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header_1"),
                ("##", "Header_2"),
                ("###", "Header_3"),
            ]
        )
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=add_start_index,
        )
        for path_obj in documents:
            loader = TextLoader(path_obj.filename, encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                header_splits = md_spitter.split_text(doc.page_content)
                for chunk in header_splits:
                    sub_chunks = text_splitter.split_text(chunk.page_content)
                    for sub_chunk in sub_chunks:
                        all_splits.append(
                            {
                                "metadata": chunk.metadata,
                                "content": sub_chunk,
                                "source": str(path_obj.filename),
                            }
                        )
        return all_splits

    async def ingest_files(
        self,
        collection_name: str,
        documents: List[RawDocumentSchema],
        chunk_size: int = 1000,
        chunk_overlap: int = 300,
    ):
        chunks = self._chunk_docs(
            documents,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        await asyncio.gather(
            self.repo.upsert(collection_name, chunks, model=self.model),
            self.keyword_repo.index_documents(collection_name, chunks),
        )
