"""Regression checks for data loss, filtering order, provenance and RAG context."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from bench import evidence_present
from src import (
    ChunkingStrategyComparator, Document, EmbeddingStore, FixedSizeChunker,
    HeadingChunker, KnowledgeBaseAgent, RecursiveChunker, SentenceChunker,
    chunk_documents, compute_similarity, load_corpus, load_markdown,
)


def test_sentence_punctuation_and_unicode():
    assert SentenceChunker(2).chunk("  Một câu.\nCâu hai!  Câu ba?\tCâu cuối. ") == [
        "Một câu. Câu hai!", "Câu ba? Câu cuối."]


@pytest.mark.parametrize("chunker", [SentenceChunker(), RecursiveChunker(), HeadingChunker()])
def test_blank_text(chunker):
    assert chunker.chunk(" \n\t") == []


@pytest.mark.parametrize("separators", [None, [], ["\n\n"], [". ", " "], ["|"]])
def test_recursive_is_lossless_and_bounded(separators):
    text = "Dòng ngắn.\n" * 12 + "\n\n" + "x" * 103 + "|Kết thúc!"
    chunks = RecursiveChunker(separators, 40).chunk(text)
    assert "".join(chunks) == text
    assert all(0 < len(chunk) <= 40 for chunk in chunks)


def test_recursive_merges_short_lines():
    chunks = RecursiveChunker(chunk_size=40).chunk("abc\n" * 20)
    assert list(map(len, chunks)) == [40, 40]


@pytest.mark.parametrize("size,overlap", [(0, 0), (-1, 0), (10, 10), (10, -1)])
def test_fixed_size_rejects_nonprogressing_windows(size, overlap):
    with pytest.raises(ValueError):
        FixedSizeChunker(size, overlap)


def test_warmup_chunk_counts():
    assert len(FixedSizeChunker(500, 50).chunk("a" * 10000)) == 23
    assert len(FixedSizeChunker(500, 100).chunk("a" * 10000)) == 25


def test_comparator_empty_and_small_sizes():
    assert all(stats["count"] == 0 and stats["avg_length"] == 0
               for stats in ChunkingStrategyComparator().compare("", 1).values())
    assert ChunkingStrategyComparator().compare("abc", 1)["fixed_size"]["chunks"] == list("abc")


def test_cosine_dimensions_and_nonunit_vectors():
    assert compute_similarity([3, 4], [6, 8]) == pytest.approx(1)
    assert compute_similarity([], []) == 0
    with pytest.raises(ValueError):
        compute_similarity([1, 2], [1])


def test_heading_context_repeated_without_losing_body():
    body = "Câu văn dài giữ đầy đủ nội dung. " * 9
    prefix = "# Sổ tay\n## Học vụ\n\n"
    chunks = HeadingChunker(100).chunk("# Sổ tay\n\n## Học vụ\n\n" + body)
    assert len(chunks) > 1
    assert all(chunk.startswith(prefix) and len(chunk) <= 100 for chunk in chunks)
    assert "".join(chunk[len(prefix):] for chunk in chunks) == body.strip()


def test_filter_happens_before_top_k_and_uses_all_fields():
    vectors = {"q": [1, 0], "faculty": [1, 0], "student": [0.8, 0.6], "other": [0.9, 0.1]}
    store = EmbeddingStore(embedding_fn=vectors.__getitem__)
    store.add_documents([
        Document("f", "faculty", {"audience": "faculty", "category": "books"}),
        Document("s", "student", {"audience": "student", "category": "books"}),
        Document("o", "other", {"audience": "student", "category": "rooms"}),
    ])
    result = store.search_with_filter("q", 1, {"audience": "student", "category": "books"})
    assert [row["id"] for row in result] == ["s"]
    assert store.search_with_filter("q", 2, {"unknown": None}) == []
    assert store.search_with_filter("q", 3, {}) == store.search("q", 3)


def test_metadata_is_owned_and_delete_removes_all_source_chunks():
    metadata = {"doc_id": "source", "nested": {"tag": "original"}}
    store = EmbeddingStore()
    store.add_documents([Document("s#0", "first", metadata), Document("s#1", "second", metadata), Document("other", "third")])
    metadata["nested"]["tag"] = "changed"
    result = store.search("first", 1)[0]
    assert result["metadata"]["nested"]["tag"] == "original"
    result["metadata"]["nested"]["tag"] = "changed again"
    assert store.search("first", 1)[0]["metadata"]["nested"]["tag"] == "original"
    assert store.delete_document("source")
    assert store.get_collection_size() == 1
    assert not store.delete_document("source")


def test_empty_search_and_nonpositive_top_k_do_not_embed():
    embedder = Mock(return_value=[1, 0])
    store = EmbeddingStore(embedding_fn=embedder)
    assert store.search("q") == []
    embedder.assert_not_called()
    store.add_documents([Document("d", "content")])
    embedder.reset_mock()
    assert store.search("q", 0) == store.search("q", -1) == []
    embedder.assert_not_called()


def test_dimension_mismatch_does_not_partially_add_batch():
    store = EmbeddingStore(embedding_fn=lambda text: [1.0] if text == "bad" else [1.0, 0.0])
    store.add_documents([Document("a", "ok")])
    with pytest.raises(ValueError):
        store.add_documents([Document("b", "ok"), Document("c", "bad")])
    assert store.get_collection_size() == 1
    with pytest.raises(ValueError):
        store.search("bad")


def test_stores_with_same_name_are_isolated():
    first, second = EmbeddingStore("same"), EmbeddingStore("same")
    first.add_documents([Document("d", "data")])
    assert second.get_collection_size() == 0


def test_agent_grounding_and_filtered_context():
    store = EmbeddingStore()
    store.add_documents([
        Document("s", "Student evidence", {"audience": "student", "source_url": "https://example.edu/student"}),
        Document("f", "Faculty evidence", {"audience": "faculty"}),
    ])
    llm = Mock(return_value="grounded answer [1]")
    agent = KnowledgeBaseAgent(store, llm)
    assert agent.answer_with_filter("question", metadata_filter={"audience": "student"}) == "grounded answer [1]"
    prompt = llm.call_args.args[0]
    assert "Student evidence" in prompt and "Faculty evidence" not in prompt
    assert "[1] source: https://example.edu/student" in prompt
    assert "QUESTION:\nquestion" in prompt
    assert "không đủ thông tin" in prompt
    llm.reset_mock()
    assert "Không tìm thấy" in agent.answer_with_filter("question", metadata_filter={"audience": "staff"})
    llm.assert_not_called()


@pytest.mark.parametrize("dataset,count", [("vinuni-library", 5), ("uit-vnuhcm", 7)])
def test_real_corpus_ingestion_and_chunk_provenance(dataset, count):
    documents = load_corpus(Path(__file__).resolve().parents[1] / "data" / dataset)
    assert len(documents) == count
    assert {doc.metadata["audience"] for doc in documents} == {"student", "faculty", "all"}
    chunks = chunk_documents(documents, HeadingChunker())
    for chunk in chunks:
        assert chunk.id.startswith(chunk.metadata["doc_id"] + "#")
        assert chunk.metadata["source_url"].startswith("https://")
        assert "source_url:" not in chunk.content


def test_loader_rejects_unclosed_frontmatter(tmp_path):
    path = tmp_path / "broken.md"
    path.write_text("---\ndoc_id: broken\n# Content", encoding="utf-8")
    with pytest.raises(ValueError, match="unclosed"):
        load_markdown(path)


def test_evaluation_requires_answer_evidence_not_only_source():
    query = {"gold_doc_id": "gold", "evidence_phrases": ["3 tài liệu", "2 tuần"]}
    assert not evidence_present([{"metadata": {"doc_id": "gold"}, "content": "Tài liệu liên quan nhưng thiếu đáp án."}], query)
    assert not evidence_present([{"metadata": {"doc_id": "wrong"}, "content": "3 tài liệu trong 2 tuần"}], query)
    assert evidence_present([{"metadata": {"doc_id": "gold"}, "content": "3 tài liệu trong 2 tuần"}], query)
