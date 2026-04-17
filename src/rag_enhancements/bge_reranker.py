from typing import Optional, Sequence
from langchain_core.callbacks import Callbacks
from langchain_core.documents import Document
from langchain_core.documents.compressor import BaseDocumentCompressor
from sentence_transformers import CrossEncoder


class BgeRerank(BaseDocumentCompressor):
    model_name: str = "BAAI/bge-reranker-v2-m3"
    top_n: int = 5
    model: CrossEncoder = CrossEncoder(model_name)

    def bge_rerank(self, query, docs):
        model_inputs = [[query, doc] for doc in docs]
        scores = self.model.predict(model_inputs)
        results = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return results[: self.top_n]

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        if len(documents) == 0:
            return []

        doc_list = list(documents)
        _docs = [d.page_content for d in doc_list]
        results = self.bge_rerank(query, _docs)
        final_results = []

        for r in results:
            doc = doc_list[r[0]]
            doc.metadata["relevance_score"] = r[1]
            final_results.append(doc)

        return final_results
