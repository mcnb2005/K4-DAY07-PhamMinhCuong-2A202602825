"""Changing a corpus must also change its questions, provenance and evaluation."""

import json
from copy import deepcopy

import pytest

from bench import DEFAULT_CORPUS, DEFAULT_QUERIES, ROOT, run_benchmark, validate_queries
from src import load_corpus


def queries():
    return json.loads(DEFAULT_QUERIES.read_text(encoding="utf-8"))


def test_default_benchmark_uses_selected_uit_ecosystem():
    report = run_benchmark()
    assert len(report["corpus"]) == 7
    assert {doc["metadata"]["university"] for doc in report["corpus"]} == {"UIT", "VNU-HCM"}
    assert {doc["metadata"]["category"] for doc in report["corpus"]} == {
        "dang_ky_hoc_phan", "hoc_phi", "hoc_bong", "thu_vien", "ky_tuc_xa", "phuc_khao"}
    assert "uit-vnuhcm" in report["corpus_dir"]
    for strategy in report["strategies"].values():
        assert len(strategy["queries"]) == 5
        filtered = strategy["filter_ab"]["filtered"]
        assert filtered and all(row["metadata"]["audience"] == "student" for row in filtered)
        assert all("vinuni" not in row["metadata"]["source_url"].lower()
                   for query in strategy["queries"] for row in query["results"])


def test_custom_corpus_requires_matching_query_file():
    with pytest.raises(ValueError, match="matching"):
        run_benchmark(corpus_dir=ROOT / "data" / "vinuni-library")


def test_vinuni_queries_cannot_silently_measure_uit_corpus():
    with pytest.raises(ValueError, match="gold document"):
        run_benchmark(queries_path=ROOT / "data" / "benchmark_queries.json")


@pytest.mark.parametrize("field,value,message", [
    ("evidence_phrases", [], "nonempty"),
    ("evidence_phrases", ["a fact absent from this corpus"], "missing"),
    ("metadata_filter", {"audience": "faculty"}, "excludes"),
])
def test_invalid_gold_or_filter_is_rejected(field, value, message):
    data = deepcopy(queries())
    data[0][field] = value
    with pytest.raises(ValueError, match=message):
        validate_queries(load_corpus(DEFAULT_CORPUS), data)


def test_filter_ab_follows_filtered_question_after_reordering(tmp_path):
    data = queries()
    data = data[1:] + data[:1]
    path = tmp_path / "reordered.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    report = run_benchmark(queries_path=path)
    for strategy in report["strategies"].values():
        assert strategy["filter_ab"]["query_id"] == "Q1"
        assert strategy["filter_ab"]["filtered"] == strategy["queries"][-1]["results"]
