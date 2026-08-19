import httpx
from typing import List, Dict, Any, Optional
from src.rag.ai.providers import BaseRerankerProvider, BaseAIProvider


class APIRerankerProvider(BaseAIProvider, BaseRerankerProvider):
    async def rerank(
        self, query: str, documents: List[str], top_n: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if not documents:
            return []
        payload = {
            "model": self.config.model_name,
            "query": query,
            "documents": documents,
            "top_n": top_n or len(documents),
            **self.config.extra_params,
        }

        data = await self._post(payload)

        results = []
        for item in data.get("results", data.get("data", [])):
            results.append({
                "index": item["index"],
                "score": item["relevance_score"] if "relevance_score" in item else item["score"]
            })
        return results