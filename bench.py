"""Reproducible K4-L3A benchmark. Run: python bench.py --provider mock."""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

from src import (
    ChunkingStrategyComparator, EmbeddingStore, FixedSizeChunker, HeadingChunker,
    KnowledgeBaseAgent, LocalEmbedder, MockEmbedder, RecursiveChunker,
    SentenceChunker, chunk_documents, compute_similarity, load_corpus,
)

ROOT = Path(__file__).resolve().parent
DEFAULT_CORPUS = ROOT / "data" / "uit-vnuhcm"
DEFAULT_QUERIES = ROOT / "data" / "uit-vnuhcm-queries.json"


def normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def evidence_present(results: list[dict], query: dict) -> bool:
    # Check answer evidence, not merely whether a matching document was returned.
    context = normalized(" ".join(
        row["content"] for row in results if row["metadata"]["doc_id"] == query["gold_doc_id"]
    ))
    return all(normalized(phrase) in context for phrase in query["evidence_phrases"])


def extractive_demo(prompt: str) -> str:
    """Show exactly what a real LLM would receive; never use the gold answer."""
    context = prompt.split("CONTEXT:\n", 1)[1].split("\n\nQUESTION:\n", 1)[0]
    return "[DEMO: trích ngữ cảnh, chưa có LLM sinh câu trả lời]\n" + context


def validate_queries(documents: list, queries: list[dict]) -> None:
    """Reject mismatched datasets instead of silently measuring impossible golds."""
    if len(queries) != 5:
        raise ValueError("The lab requires exactly five benchmark queries")
    if len({query["id"] for query in queries}) != len(queries):
        raise ValueError("Benchmark query IDs must be unique")
    sources = {doc.id: doc for doc in documents}
    for query in queries:
        doc = sources.get(query["gold_doc_id"])
        if doc is None:
            raise ValueError(f"{query['id']}: gold document is not in the selected corpus")
        phrases = query["evidence_phrases"]
        if not phrases or any(not phrase.strip() for phrase in phrases):
            raise ValueError(f"{query['id']}: evidence phrases must be nonempty")
        if not all(normalized(phrase) in normalized(doc.content) for phrase in phrases):
            raise ValueError(f"{query['id']}: evidence is missing from its gold document")
        filters = query.get("metadata_filter") or {}
        if not all(key in doc.metadata and doc.metadata[key] == value for key, value in filters.items()):
            raise ValueError(f"{query['id']}: metadata filter excludes its gold document")
    if not any(query.get("metadata_filter") for query in queries):
        raise ValueError("At least one benchmark query must use metadata filtering")


def run_benchmark(
    provider: str = "mock", chunk_size: int = 300,
    corpus_dir: Path | None = None, queries_path: Path | None = None,
) -> dict:
    corpus_dir = Path(corpus_dir or DEFAULT_CORPUS).resolve()
    if queries_path is None and corpus_dir != DEFAULT_CORPUS.resolve():
        raise ValueError("A custom corpus requires a matching queries_path / --queries file")
    queries_path = Path(queries_path or DEFAULT_QUERIES).resolve()
    documents = load_corpus(corpus_dir)
    queries = json.loads(queries_path.read_text(encoding="utf-8"))
    validate_queries(documents, queries)
    if provider not in {"mock", "local"}:
        raise ValueError("Unknown embedding provider")
    # Fail explicitly if the chosen real backend is unavailable; no hidden fallback.
    embedder = MockEmbedder() if provider == "mock" else LocalEmbedder()
    cache: dict[str, list[float]] = {}

    def embed(text: str) -> list[float]:
        if text not in cache:
            cache[text] = embedder(text)
        return cache[text]

    strategies = {
        "fixed_size": FixedSizeChunker(chunk_size, min(50, chunk_size // 4)),
        "by_sentences": SentenceChunker(2),
        "recursive": RecursiveChunker(chunk_size=chunk_size),
        "heading": HeadingChunker(chunk_size),
    }
    report = {
        "corpus_dir": corpus_dir.as_posix(),
        "queries_path": queries_path.as_posix(),
        "python": platform.python_version(),
        "provider": provider,
        "backend": embedder._backend_name,
        "llm": "extractive demo only; answer correctness not graded",
        "chunk_size": chunk_size,
        "corpus": [{"id": doc.id, "characters": len(doc.content), "metadata": doc.metadata} for doc in documents],
        "baseline": {doc.id: ChunkingStrategyComparator().compare(doc.content, 200) for doc in documents[:3]},
        "strategies": {},
    }
    for name, chunker in strategies.items():
        chunks = chunk_documents(documents, chunker)
        store = EmbeddingStore(name, embedding_fn=embed)
        store.add_documents(chunks)
        agent = KnowledgeBaseAgent(store, extractive_demo)
        rows = []
        for query in queries:
            results = store.search_with_filter(query["question"], 3, query["metadata_filter"])
            rows.append({
                "query_id": query["id"],
                "question": query["question"],
                "metadata_filter": query["metadata_filter"],
                "results": results,
                "source_hit": any(row["metadata"]["doc_id"] == query["gold_doc_id"] for row in results),
                "evidence_top1": evidence_present(results[:1], query),
                "evidence_top3": evidence_present(results, query),
                "agent_answer": agent.answer_with_filter(query["question"], 3, query["metadata_filter"]),
            })
        filter_index = next(index for index, query in enumerate(queries) if query.get("metadata_filter"))
        filter_query = queries[filter_index]
        unfiltered = store.search(filter_query["question"], 3)
        report["strategies"][name] = {
            "chunk_count": len(chunks),
            "avg_length": sum(len(doc.content) for doc in chunks) / len(chunks),
            "source_hits": sum(row["source_hit"] for row in rows),
            "evidence_hits": sum(row["evidence_top3"] for row in rows),
            "queries": rows,
            "filter_ab": {
                "query_id": filter_query["id"],
                "unfiltered": unfiltered,
                "unfiltered_evidence": evidence_present(unfiltered, filter_query),
                "metadata_filter": filter_query["metadata_filter"],
                "filtered": rows[filter_index]["results"],
                "filtered_evidence": rows[filter_index]["evidence_top3"],
            },
        }
    pairs = json.loads((ROOT / "data" / "similarity_pairs.json").read_text(encoding="utf-8"))
    report["similarity"] = [{**pair, "score": compute_similarity(embed(pair["a"]), embed(pair["b"]))} for pair in pairs]
    return report


def markdown_report(report: dict) -> str:
    lines = [
        "# Kết quả benchmark", "",
        f"Corpus: `{Path(report['corpus_dir']).name}` — {len(report['corpus'])} tài liệu.",
        f"Bộ câu hỏi: `{Path(report['queries_path']).name}`.",
        f"Python {report['python']}; embedding: `{report['backend']}`; chunk_size={report['chunk_size']}.",
        "SentenceChunker dùng 2 câu/chunk; comparator baseline dùng 3 câu/chunk, size=200.",
        "Agent chỉ trích ngữ cảnh bằng hàm giả lập; chưa đánh giá câu trả lời của LLM thật.",
        ("Mock dùng MD5 và số giả ngẫu nhiên: điểm số không phản ánh ngữ nghĩa, không dùng để chọn mô hình tốt nhất."
         if report["provider"] == "mock" else "Đang dùng embedding đa ngữ local; vẫn cần đánh giá câu trả lời của LLM thật."), "",
        "`Source hit`: có đúng tài liệu. `Evidence hit`: ngữ cảnh từ tài liệu đó chứa đủ các cụm đáp án đã khai báo.",
        "Evidence hit là phép kiểm chuỗi hỗ trợ kiểm tra thủ công, không phải thang điểm chất lượng LLM.", "",
        "| Chiến lược | Số chunk | Độ dài TB | Source hit@3 | Evidence hit@3 |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, data in report["strategies"].items():
        lines.append(f"| {name} | {data['chunk_count']} | {data['avg_length']:.1f} | {data['source_hits']}/5 | {data['evidence_hits']}/5 |")
    for name, data in report["strategies"].items():
        lines += ["", f"## {name}", "", "| Câu | Top-3: chunk (score) | Đủ bằng chứng top-1 / top-3 |", "|---|---|---|"]
        for row in data["queries"]:
            top = "; ".join(f"{result['id']} ({result['score']:.4f})" for result in row["results"])
            lines.append(f"| {row['query_id']} | {top} | {row['evidence_top1']} / {row['evidence_top3']} |")
        lines += ["", f"### A/B bộ lọc {data['filter_ab']['query_id']}", "",
                  f"Metadata filter: `{json.dumps(data['filter_ab']['metadata_filter'], ensure_ascii=False)}`", ""]
        for mode in ("unfiltered", "filtered"):
            top = "; ".join(f"{r['id']} ({r['metadata']['audience']}, {r['score']:.4f})" for r in data["filter_ab"][mode])
            lines.append(f"- {mode}: {top}. Đủ bằng chứng: {data['filter_ab'][mode + '_evidence']}.")
    lines += ["", "## Baseline trên ba tài liệu", "", "| Tài liệu | Chiến lược | Số chunk | Độ dài TB |", "|---|---|---:|---:|"]
    for doc_id, strategies in report["baseline"].items():
        for name, data in strategies.items():
            lines.append(f"| {doc_id} | {name} | {data['count']} | {data['avg_length']:.1f} |")
    lines += ["", "## Dự đoán trước khi chạy", "", "| Cặp | Câu A | Câu B | Dự đoán theo ngữ nghĩa | Cosine thực tế |", "|---|---|---|---|---:|"]
    for index, row in enumerate(report["similarity"], 1):
        lines.append(f"| {index} | {row['a']} | {row['b']} | {row['prediction']} | {row['score']:.4f} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["mock", "local"], default="mock")
    parser.add_argument("--chunk-size", type=int, default=300)
    parser.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--queries", type=Path, help="Matching query JSON; required for a custom corpus")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "report" / "results")
    args = parser.parse_args()
    report = run_benchmark(args.provider, args.chunk_size, args.corpus_dir, args.queries)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "benchmark.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown = markdown_report(report)
    (args.output_dir / "benchmark.md").write_text(markdown, encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
