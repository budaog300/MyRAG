import uuid
from typing import List, Tuple
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

class HierarchicalMarkdownSplitter(BaseDocumentSplitter):
    def __init__(self, headers_to_split_on: list[tuple[str, str]] | None = None):
        self.headers_to_split_on = headers_to_split_on or [
            ("#", "Header_1"),
            ("##", "Header_2"),
            ("###", "Header_3"),
            ("####", "Header_4"),
        ]

    def split(
        self, 
        doc: RawDocumentSchema, 
        markdown_text: str,
        parent_chunk_size: int = 3000,  # Увеличено, чтобы таблица помещалась целиком
        child_chunk_size: int = 400,     # Маленькие чанки для точного векторного поиска
        child_chunk_overlap: int = 50
    ) -> Tuple[List[RAGDocument], List[RAGDocument]]:
        
        # 1. Сплитим по заголовкам Markdown (Логические секции)
        md_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False,
        )
        header_splits = md_splitter.split_text(markdown_text)

        # Splitter для Parent-чанков
        parent_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=200,
            separators=["\n\n\n", "\n\n", "\n", " ", ""]
        )

        # Splitter для Child-чанков
        child_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=child_chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

        parent_chunks: List[RAGDocument] = []
        child_chunks: List[RAGDocument] = []
        
        parent_index = 0
        child_index = 0

        for header_split in header_splits:
            breadcrumbs = " > ".join([str(v) for v in header_split.metadata.values()])
            
            # Нарезаем секцию на Parent-чанки
            raw_parents = parent_text_splitter.split_text(header_split.page_content)

            for parent_raw_text in raw_parents:
                parent_id = str(uuid.uuid4())
                
                context_prefix = (
                    f"[Источник: {doc.source} | Раздел: {breadcrumbs}]\n\n"
                    if breadcrumbs else f"[Источник: {doc.source}]\n\n"
                )
                parent_enriched_content = context_prefix + parent_raw_text

                parent_metadata = {
                    "chunk_id": parent_id,
                    "doc_id": doc.doc_id,
                    "source": doc.source,
                    "chunk_index": parent_index,
                    "breadcrumbs": breadcrumbs,
                    "is_parent": True,
                    **header_split.metadata,
                    **doc.metadata,
                }

                parent_doc = RAGDocument(
                    content=parent_enriched_content,
                    raw_content=parent_raw_text,
                    metadata=parent_metadata,
                )
                parent_chunks.append(parent_doc)
                parent_index += 1

                # 2. Нарезаем данный Parent-чанк на Child-чанки
                raw_children = child_text_splitter.split_text(parent_raw_text)

                for child_raw_text in raw_children:
                    child_id = str(uuid.uuid4())
                    
                    # Прокидываем линк на родителя в метаданные и в контекст
                    child_enriched_content = context_prefix + child_raw_text

                    child_metadata = {
                        "chunk_id": child_id,
                        "parent_id": parent_id,  # Ссылка на родительский чанк!
                        "doc_id": doc.doc_id,
                        "source": doc.source,
                        "chunk_index": child_index,
                        "breadcrumbs": breadcrumbs,
                        "is_parent": False,
                        **header_split.metadata,
                        **doc.metadata,
                    }

                    child_doc = RAGDocument(
                        content=child_enriched_content,
                        raw_content=child_raw_text,
                        metadata=child_metadata,
                    )
                    child_chunks.append(child_doc)
                    child_index += 1

        return parent_chunks, child_chunks