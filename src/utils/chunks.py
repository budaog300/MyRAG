from pathlib import Path
from typing import List
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
from langchain_community.document_loaders import TextLoader


def read_folder(folder_path: str):
    return [path for path in Path(folder_path).iterdir() if path.is_file()]


def read_files(files: List[Path]):
    return [path for path in files if path.is_file()]


def chunk_docs(
    files: List[Path],
    chunk_size: int,
    chunk_overlap: int = 0,
    add_start_index: bool = True,
):
    file_paths = read_files(files)
    all_splits = []
    md_spitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "Header_1"), ("##", "Header_2"), ("###", "Header_3")]
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=add_start_index,
    )
    for path in file_paths:
        loader = TextLoader(path, encoding="utf-8")
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
                            "source": str(path),
                        }
                    )
    return all_splits
