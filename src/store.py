from __future__ import annotations

from typing import Any, Callable
from copy import deepcopy

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Uses an isolated in-memory store, as recommended by the K4 lab guide.
    Scores are dot products (cosine similarity for unit-normalized embeddings).
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = deepcopy(doc.metadata)
        metadata.setdefault("doc_id", doc.id)
        record = {
            "id": doc.id,
            "record_id": self._next_index,
            "content": doc.content,
            "metadata": metadata,
            "embedding": list(self._embedding_fn(doc.content)),
        }
        self._next_index += 1
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if top_k <= 0 or not records:
            return []
        query_embedding = self._embedding_fn(query)
        results = [
            {
                "id": record["id"],
                "content": record["content"],
                "metadata": deepcopy(record["metadata"]),
                "score": _dot(query_embedding, record["embedding"]),
            }
            for record in records
        ]
        return sorted(results, key=lambda result: result["score"], reverse=True)[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        One Document is one record; chunking belongs to the ingestion step.
        Repeated document IDs are allowed, including chunks of the same source.
        """
        records = [self._make_record(doc) for doc in docs]
        dimensions = {len(record["embedding"]) for record in self._store + records}
        if len(dimensions) > 1 or 0 in dimensions:
            raise ValueError("All embeddings must have the same positive dimension")
        self._store.extend(records)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        filters = metadata_filter or {}
        candidates = [
            record for record in self._store
            if all(key in record["metadata"] and record["metadata"][key] == value
                   for key, value in filters.items())
        ]
        return self._search_records(query, candidates, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        previous_size = len(self._store)
        self._store = [record for record in self._store if record["metadata"]["doc_id"] != doc_id]
        return len(self._store) < previous_size
