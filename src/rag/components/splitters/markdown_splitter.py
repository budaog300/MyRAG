import uuid
from typing import List
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from src.core.constants import DOCUMENT_DELIMITER
from src.rag.components.splitters import BaseDocumentSplitter
from src.rag.schemas.document import RawDocumentSchema, RAGDocument


class MarkdownDocumentSplitter(BaseDocumentSplitter):
    def __init__(
        self,
        chunk_size: int = 400,
        chunk_overlap: int = 50,
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
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(
        self, 
        doc: RawDocumentSchema, 
        markdown_text: str,
        **kwargs
    ) -> List[RAGDocument]:
        md_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False,
        )
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n\n", "\n\n", "\n", ". ", " ", ""],
        )

        final_chunks: List[RAGDocument] = []
        
        sections = markdown_text.split(self.delimiter)
        
        for section_idx, section in enumerate(sections):
            if not section.strip():
                continue

            header_splits = md_splitter.split_text(markdown_text)

            for header_split in header_splits:
                sub_chunks = text_splitter.split_text(header_split.page_content)
                breadcrumbs = " > ".join([str(v) for v in header_split.metadata.values()])

                for chunk_index, sub_chunk in enumerate(sub_chunks):
                    context_prefix = (
                        f"[Источник: {doc.source} | Раздел: {breadcrumbs}]\n\n"
                        if breadcrumbs
                        else f"[Источник: {doc.source}]\n\n"
                    )
                    enriched_content = context_prefix + sub_chunk
                    chunk_id = str(uuid.uuid5(
                        uuid.NAMESPACE_DNS, 
                        f"{doc.doc_id}:{section_idx}:{chunk_index}:{sub_chunk}"
                    ))
                    chunk_metadata = {
                        "chunk_id": chunk_id,
                        "doc_id": doc.doc_id,                        
                        "chunk_index": chunk_index,
                        "breadcrumbs": breadcrumbs,
                        **doc.metadata,
                    }

                    chunk = RAGDocument(
                        content=enriched_content,
                        raw_content=sub_chunk,
                        metadata=chunk_metadata,
                        source=doc.source,
                    )
                    final_chunks.append(chunk)

        return final_chunks