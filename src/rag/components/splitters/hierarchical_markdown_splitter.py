import uuid
from typing import List, Tuple
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from src.core.constants import DOCUMENT_DELIMITER
from src.rag.components.splitters import BaseDocumentSplitter
from src.rag.schemas.document import RawDocumentSchema, RAGDocument


class HierarchicalMarkdownSplitter(BaseDocumentSplitter):
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
        parent_chunk_size: int = 3000,
        child_chunk_size: int = 400,
        child_chunk_overlap: int = 50
    ) -> Tuple[List[RAGDocument], List[RAGDocument]]:        
        md_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False,
        )       

        parent_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=200,
            separators=["\n\n\n", "\n\n", "\n", " ", ""]
        )

        child_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=child_chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        
        final_chunks: List[RAGDocument] = []

        sections = markdown_text.split(self.delimiter)
        
        for section_idx, section in enumerate(sections):
            if not section.strip():
                continue

            header_splits = md_splitter.split_text(markdown_text)

            for header_split in header_splits:
                # 1. Нарезаем секцию на Parent-чанки
                raw_parents = parent_text_splitter.split_text(header_split.page_content)
                breadcrumbs = " > ".join([str(v) for v in header_split.metadata.values()])
                
                for parent_index, parent_raw_text in enumerate(raw_parents):                    
                    context_prefix = (
                        f"[Источник: {doc.source} | Раздел: {breadcrumbs}]\n\n"
                        if breadcrumbs else f"[Источник: {doc.source}]\n\n"
                    )
                    parent_enriched_content = context_prefix + parent_raw_text
                    parent_chunk_id = str(uuid.uuid5(
                        uuid.NAMESPACE_DNS, 
                        f"{doc.doc_id}:{section_idx}:{parent_index}:{parent_raw_text}"
                    ))
                    parent_metadata = {
                        "chunk_id": parent_chunk_id,
                        "doc_id": doc.doc_id,                        
                        "chunk_index": parent_index,
                        "breadcrumbs": breadcrumbs,
                        **doc.metadata
                    }

                    parent_doc = RAGDocument(
                        content=parent_enriched_content,
                        raw_content=parent_raw_text,
                        metadata=parent_metadata,
                        source=doc.source,
                        is_parent=True
                    )
                    final_chunks.append(parent_doc)

                    # 2. Нарезаем данный Parent-чанк на Child-чанки
                    raw_children = child_text_splitter.split_text(parent_raw_text)

                    for child_index, child_raw_text in enumerate(raw_children):
                        child_chunk_id = str(uuid.uuid5(
                            uuid.NAMESPACE_DNS, 
                            f"{doc.doc_id}:{section_idx}:{child_index}:{child_raw_text}"
                        ))
                        
                        child_enriched_content = context_prefix + child_raw_text

                        child_metadata = {
                            "chunk_id": child_chunk_id,
                            "parent_id": parent_chunk_id,
                            "doc_id": doc.doc_id,
                            "chunk_index": child_index,
                            "breadcrumbs": breadcrumbs,                            
                            **doc.metadata,
                        }

                        child_doc = RAGDocument(
                            content=child_enriched_content,
                            raw_content=child_raw_text,
                            metadata=child_metadata,
                            source=doc.source,
                            is_parent=False
                        )
                        final_chunks.append(child_doc)

        return final_chunks