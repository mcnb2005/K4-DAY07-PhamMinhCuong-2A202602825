"""Markdown section chunking for the university retrieval experiment."""

import re

from .chunking import RecursiveChunker


class HeadingChunker:
    """Keep the heading hierarchy on every piece of a long Markdown section."""

    def __init__(self, chunk_size: int = 300) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        chunks = []
        headings: list[tuple[int, str]] = []
        body: list[str] = []

        def flush() -> None:
            content = "".join(body).strip()
            if not content:
                return
            prefix = "\n".join(heading for _, heading in headings)
            prefix = prefix + "\n\n" if prefix else ""
            available = self.chunk_size - len(prefix)
            if available <= 0:
                raise ValueError("chunk_size is too small to preserve the heading hierarchy")
            chunks.extend(prefix + piece for piece in RecursiveChunker(chunk_size=available).chunk(content))

        for line in text.splitlines(keepends=True):
            match = re.match(r"^(#{1,6})\s+\S", line)
            if match:
                flush()
                body = []
                level = len(match.group(1))
                headings = [(depth, title) for depth, title in headings if depth < level]
                headings.append((level, line.strip()))
            else:
                body.append(line)
        flush()
        if not chunks and text.strip():
            return RecursiveChunker(chunk_size=self.chunk_size).chunk(text.strip())
        return chunks
