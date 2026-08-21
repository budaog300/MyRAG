import uuid
from typing import List
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from src.core.constants import DOCUMENT_DELIMITER
from src.rag.components.splitters import BaseDocumentSplitter
from src.rag.schemas.document import RawDocumentSchema, RAGDocument


class MarkdownDocumentSplitter(BaseDocumentSplitter):
    def __init__(
        self, 
        headers_to_split_on: list[tuple[str, str]] | None = None,
        delimiter: str = DOCUMENT_DELIMITER,
    ):
        self.headers_to_split_on = headers_to_split_on or [
            ("#", "Header_1"),
            ("##", "Header_2"),
            ("###", "Header_3"),
            ("####", "Header_4"),
        ]
        self.delimiter = delimiter

    def split(
        self, 
        doc: RawDocumentSchema, 
        markdown_text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 100
    ) -> List[RAGDocument]:
        md_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False,
        )
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n\n", "\n\n", "\n", ". ", " ", ""],
        )

        final_chunks: List[RAGDocument] = []
        chunk_index = 0
        
        sections = markdown_text.split(self.delimiter)
        
        for section in sections:
            if not section.strip():
                continue

            header_splits = md_splitter.split_text(markdown_text)

            for header_split in header_splits:
                sub_chunks = text_splitter.split_text(header_split.page_content)
                breadcrumbs = " > ".join([str(v) for v in header_split.metadata.values()])

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

                    chunk = RAGDocument(
                        content=enriched_content,
                        raw_content=sub_chunk,
                        metadata=chunk_metadata,
                    )
                    final_chunks.append(chunk)
                    chunk_index += 1

        return final_chunks