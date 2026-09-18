"""
Cognita backend tests.

The LLM provider is stubbed out so the suite validates the *contract and
resilience layer* deterministically and offline:

* input validation (too short / too long)
* happy-path structural validation and block renumbering
* malformed block pruning
* markdown-fence stripping and JSON repair
* section chunking of oversized documents
* anchor verification helpers
"""

import json
import os
import sys
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import transformer  # noqa: E402
from main import app  # noqa: E402

client = TestClient(app)

SOURCE_TEXT = (
    "Deliberate practice requires immediate feedback on performance. "
    "Ericsson argues that elite performers do not simply accumulate hours; "
    "they refine specific sub-skills under expert supervision. "
    "However, the model poorly predicts performance in domains with ill-defined "
    "success criteria, such as creative writing or strategic management. "
    "Critics additionally note that sample sizes in early studies were small."
)


def _valid_payload() -> Dict[str, Any]:
    return {
        "document_title": "Deliberate Practice and Expertise",
        "overall_read_time_minutes": 3,
        "difficulty_score": 7,
        "executive_summary": "One. Two. Three.",
        "blocks": [
            {
                "block_id": 1,
                "headline": "Feedback Drives Refinement",
                "estimated_reading_seconds": 40,
                "bionic_chunks": [
                    "Deliberate practice requires immediate feedback on performance.",
                    "Elite performers refine specific sub-skills under expert supervision.",
                ],
                "key_takeaway": "Feedback, not raw hours, produces expertise.",
                "source_citation_anchor": "Deliberate practice requires immediate feedback on performance.",
                "quiz": {
                    "question": "What drives skill refinement?",
                    "options": [
                        {"id": "A", "text": "Raw hours", "is_correct": False, "feedback": "No."},
                        {"id": "B", "text": "Immediate feedback", "is_correct": True, "feedback": "Yes."},
                        {"id": "C", "text": "Talent alone", "is_correct": False, "feedback": "No."},
                    ],
                    "explanation": "Feedback closes the correction loop.",
                },
            },
            {
                "block_id": 2,
                "headline": "Domain Boundary Condition",
                "estimated_reading_seconds": 35,
                "bionic_chunks": [
                    "The model poorly predicts performance where success is ill-defined."
                ],
                "key_takeaway": "The theory has domain limits.",
                "source_citation_anchor": "the model poorly predicts performance in domains with ill-defined success criteria",
                "quiz": None,
            },
        ],
        "nuance_caveats": ["Early studies used small samples."],
    }


@pytest.fixture(autouse=True)
def _configured_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-a-placeholder")


def test_health_endpoint_reports_model_metadata():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "model" in body and "base_url" in body
    assert body["api_key_configured"] is True


def test_transform_rejects_short_input():
    response = client.post("/api/transform", json={"raw_text": "too short"})
    assert response.status_code == 422
    assert "too short" in response.json()["detail"].lower()


def test_transform_rejects_oversized_input():
    response = client.post("/api/transform", json={"raw_text": "x" * 50001})
    assert response.status_code == 422
    assert "50,000" in response.json()["detail"]


def test_transform_missing_api_key_returns_actionable_error(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-your-actual-api-key-here")
    response = client.post("/api/transform", json={"raw_text": SOURCE_TEXT * 3})
    assert response.status_code == 500
    assert "OPENAI_API_KEY" in response.json()["detail"]


@pytest.mark.anyio
async def test_transform_document_happy_path(monkeypatch):
    async def fake_completion(client_arg, user_prompt):
        return _valid_payload()

    monkeypatch.setattr(transformer, "_complete_with_json_guard", fake_completion)

    result = await transformer.transform_document(SOURCE_TEXT)
    assert result.document_title == "Deliberate Practice and Expertise"
    assert [b.block_id for b in result.blocks] == [1, 2]
    assert result.blocks[0].quiz is not None
    assert result.blocks[1].quiz is None
    assert result.nuance_caveats == ["Early studies used small samples."]


@pytest.mark.anyio
async def test_blocks_are_renumbered_sequentially(monkeypatch):
    payload = _valid_payload()
    payload["blocks"][0]["block_id"] = 99  # model mis-numbered the blocks

    async def fake_completion(client_arg, user_prompt):
        return payload

    monkeypatch.setattr(transformer, "_complete_with_json_guard", fake_completion)
    result = await transformer.transform_document(SOURCE_TEXT)
    assert [b.block_id for b in result.blocks] == [1, 2]


@pytest.mark.anyio
async def test_invalid_quiz_is_dropped_not_crashed(monkeypatch):
    payload = _valid_payload()
    payload["blocks"][0]["quiz"]["options"][0]["is_correct"] = True  # two correct answers

    async def fake_completion(client_arg, user_prompt):
        return payload

    monkeypatch.setattr(transformer, "_complete_with_json_guard", fake_completion)
    result = await transformer.transform_document(SOURCE_TEXT)
    assert result.blocks[0].quiz is None


@pytest.mark.anyio
async def test_malformed_blocks_are_pruned(monkeypatch):
    payload = _valid_payload()
    payload["blocks"].append({"headline": "Broken block with no chunks"})

    async def fake_completion(client_arg, user_prompt):
        return payload

    monkeypatch.setattr(transformer, "_complete_with_json_guard", fake_completion)
    result = await transformer.transform_document(SOURCE_TEXT)
    assert len(result.blocks) == 2


@pytest.mark.anyio
async def test_empty_blocks_raises_malformed_error(monkeypatch):
    async def fake_completion(client_arg, user_prompt):
        return {"blocks": []}

    monkeypatch.setattr(transformer, "_complete_with_json_guard", fake_completion)
    with pytest.raises(transformer.MalformedModelOutputError):
        await transformer.transform_document(SOURCE_TEXT)


class TestParsing:
    def test_strip_markdown_fences(self):
        raw = '```json\n{"a": 1}\n```'
        assert json.loads(transformer.strip_markdown_fences(raw)) == {"a": 1}

    def test_strip_conversational_preamble(self):
        raw = 'Sure! Here is the JSON:\n{"a": 1}\nLet me know if you need more.'
        assert json.loads(transformer.strip_markdown_fences(raw)) == {"a": 1}

    def test_trailing_comma_is_tolerated(self):
        assert transformer.parse_model_json('{"a": [1, 2,],}') == {"a": [1, 2]}

    def test_unparseable_payload_raises(self):
        with pytest.raises(transformer.MalformedModelOutputError):
            transformer.parse_model_json("not json at all")


class TestChunking:
    def test_small_document_is_single_chunk(self):
        assert transformer.split_text(SOURCE_TEXT, max_chars=15000) == [SOURCE_TEXT.strip()]

    def test_large_document_is_split_on_boundaries(self):
        paragraph = "Sentence about cognitive load. " * 60
        document = "\n\n".join([paragraph] * 8)
        chunks = transformer.split_text(document, max_chars=1500)
        assert len(chunks) > 1
        assert all(len(c) <= 1600 for c in chunks)

    def test_oversized_single_paragraph_is_split(self):
        document = "A single enormous sentence fragment. " * 400
        chunks = transformer.split_text(document, max_chars=1000)
        assert len(chunks) > 1


class TestAnchorVerification:
    def test_exact_anchor_is_found(self):
        assert transformer.find_anchor_span("immediate feedback", SOURCE_TEXT) is not None

    def test_whitespace_drift_is_tolerated(self):
        assert transformer.find_anchor_span("model poorly\npredicts", SOURCE_TEXT) is not None

    def test_absent_anchor_returns_none(self):
        assert transformer.find_anchor_span("this sentence is not in the source", SOURCE_TEXT) is None


class TestMerging:
    def test_merge_renumbers_blocks_and_dedupes_caveats(self):
        first = transformer.build_response(_valid_payload(), SOURCE_TEXT)
        second = transformer.build_response(_valid_payload(), SOURCE_TEXT)
        merged = transformer._merge([first, second])

        assert [b.block_id for b in merged.blocks] == [1, 2, 3, 4]
        assert merged.nuance_caveats == ["Early studies used small samples."]
        assert merged.overall_read_time_minutes >= 1
