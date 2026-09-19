"""Load the flat string front matter used by this lab, then chunk the body."""

import json
from pathlib import Path
from typing import Protocol

from .models import Document


class Chunker(Protocol):
    def chunk(self, text: str) -> list[str]: ...


def load_markdown(path: Path) -> Document:
    """Accept plain or JSON-quoted scalar strings, not arbitrary YAML features."""
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing front matter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError(f"{path}: unclosed front matter")
    metadata = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator or not key.strip() or key.strip() in metadata:
            raise ValueError(f"{path}: invalid or repeated metadata key")
        value = value.strip()
        if value.startswith('"'):
            value = json.loads(value)
        else:
            value = value.split(" #", 1)[0].strip()
        if not isinstance(value, str) or not value:
            raise ValueError(f"{path}: metadata must contain nonempty strings")
        metadata[key.strip()] = value
    required = {"doc_id", "title", "audience", "department", "source_url", "retrieved_at", "document_version"}
    if missing := required - metadata.keys():
        raise ValueError(f"{path}: missing metadata {sorted(missing)}")
    if metadata["audience"] not in {"student", "faculty", "staff", "all"}:
        raise ValueError(f"{path}: invalid audience")
    metadata["source"] = path.as_posix()
    content = "".join(lines[end + 1:]).strip()
    if not content:
        raise ValueError(f"{path}: empty document body")
    return Document(metadata["doc_id"], content, metadata)


def load_corpus(directory: Path) -> list[Document]:
    documents = [load_markdown(path) for path in sorted(directory.glob("*.md"))]
    if not documents:
        raise ValueError(f"No Markdown documents found in {directory}")
    if len({doc.id for doc in documents}) != len(documents):
        raise ValueError("Corpus document IDs must be unique")
    return documents


def chunk_documents(documents: list[Document], chunker: Chunker) -> list[Document]:
    return [
        Document(f"{doc.id}#{index}", content,
                 {**doc.metadata, "doc_id": doc.id, "chunk_index": index})
        for doc in documents
        for index, content in enumerate(chunker.chunk(doc.content))
    ]
