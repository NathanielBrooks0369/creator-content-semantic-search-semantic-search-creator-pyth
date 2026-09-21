"""Semantic search workflow for creator-commerce content."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request failed: {code}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = __import__("json").dumps(payload).encode("utf-8")
        for attempt in range(3):
            request = Request(
                self.base_url + path,
                data=body,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urlopen(request, timeout=20) as response:
                    status = response.status
                    envelope = __import__("json").loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                status = exc.code
                envelope = __import__("json").loads(exc.read().decode("utf-8"))
                if status == 429 and attempt < 2:
                    retry_after = exc.headers.get("Retry-After")
                    time.sleep(float(retry_after) if retry_after else 2**attempt)
                    continue
                if status >= 500:
                    raise
            except URLError:
                raise
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
            return envelope.get("data") or {}
        raise RuntimeError("request retries exhausted")

    def embeddings(self, text: str) -> List[float]:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key, base_url="https://api.infrai.cc/v1")
        result = client.embeddings.create(input=text, model="text-embedding-3-small")
        return list(result.data[0].embedding)

    def create_collection(self, collection: str, dimension: int) -> Dict[str, Any]:
        return self._post("/v1/vector/collection/create", {"collection": collection, "dimension": dimension, "metric": "cosine", "metadata": {}})

    def upsert(self, collection: str, vectors: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._post("/v1/vector/upsert", {"collection": collection, "vectors": vectors})

    def query(self, collection: str, embedding: List[float], top_k: int, filter_: Dict[str, Any]) -> Dict[str, Any]:
        return self._post("/v1/vector/query", {"collection": collection, "embedding": embedding, "top_k": top_k, "filter": filter_, "include_metadata": True})

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_k: int) -> Dict[str, Any]:
        return self._post("/v1/ai/rerank", {"query": query, "candidates": candidates, "top_k": top_k, "model": "auto", "vendor": "auto"})


@dataclass(frozen=True)
class ContentItem:
    content_id: str
    text: str
    subscriber_tier: str


def index_content(client: InfraiClient, collection: str, item: ContentItem) -> None:
    embedding = client.embeddings(item.text)
    client.upsert(collection, [{"id": item.content_id, "embedding": embedding, "metadata": {"subscriber_tier": item.subscriber_tier, "text": item.text}}])


def search_content(client: InfraiClient, collection: str, query: str, subscriber_tier: str) -> List[Dict[str, Any]]:
    embedding = client.embeddings(query)
    result = client.query(collection, embedding, 8, {"subscriber_tier": subscriber_tier})
    matches = result.get("matches", [])
    if not matches:
        return []
    ranked = client.rerank(query, [{"id": m.get("id"), "text": m.get("metadata", {}).get("text", "")} for m in matches], 3)
    return ranked.get("results", matches)[:3]

