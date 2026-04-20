from typing import Optional, Sequence, List
from sentence_transformers import CrossEncoder

from src.schemas.schemas import RAGDocument


class Rerank:
    model_name: str = "BAAI/bge-reranker-v2-m3"
    top_n: int = 5
    model: CrossEncoder = CrossEncoder(model_name)

    def rerank(self, query: str, docs: List[str]):
        model_inputs = [[query, doc] for doc in docs]
        scores = self.model.predict(model_inputs)
        results = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return results[: self.top_n]

    def compress_documents(
        self,
        query: str,
        documents: List[RAGDocument],
    ) -> List[RAGDocument]:
        if len(documents) == 0:
            return []

        list_docs = list(documents)
        _docs = [doc.content for doc in list_docs]
        results = self.rerank(query, _docs)
        final_results = []
        print(results)
        for r in results:
            doc = list_docs[r[0]]
            doc.metadata["rerank_score"] = r[1]
            final_results.append(doc)

        return final_results
