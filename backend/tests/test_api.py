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
* the single-call budget (thinking disabled, structured JSON output, no
  chunk fan-out, no automatic repair pass)
"""

import json
import os
import sys
from types import SimpleNamespace
from typing import Any, Dict, List

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


def _fake_client(contents: str | List[str], finish_reason: str = "stop"):
    """Stand-in for AsyncOpenAI that records every provider call's kwargs."""
    queue = contents if isinstance(contents, list) else [contents]
    calls: List[Dict[str, Any]] = []

    async def create(**kwargs):
        calls.append(kwargs)
        content = queue[len(calls) - 1] if len(calls) <= len(queue) else queue[-1]
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=content),
                    finish_reason=finish_reason,
                )
            ]
        )

    client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )
    return client, calls


class TestCallBudget:
    """One provider request per document - guarded by explicit tests."""

    def test_default_chunk_ceiling_covers_the_entire_api_input_cap(self, monkeypatch):
        monkeypatch.delenv("MAX_CHUNK_CHARS", raising=False)
        assert transformer.max_chunk_chars() >= 50000
        document = "A" * 50000
        assert transformer.split_text(document) == [document]

    @pytest.mark.anyio
    async def test_valid_json_costs_exactly_one_provider_call(self, monkeypatch):
        monkeypatch.delenv("LLM_JSON_REPAIR_PASS", raising=False)
        payload = _valid_payload()
        client, calls = _fake_client(json.dumps(payload))

        result = await transformer._complete_with_json_guard(client, "prompt")

        assert result["document_title"] == payload["document_title"]
        assert len(calls) == 1

    @pytest.mark.anyio
    async def test_malformed_json_does_not_spend_a_second_call_by_default(
        self, monkeypatch
    ):
        monkeypatch.delenv("LLM_JSON_REPAIR_PASS", raising=False)
        client, calls = _fake_client("Sure! Here is the json: definitely-not-json")

        with pytest.raises(transformer.MalformedModelOutputError):
            await transformer._complete_with_json_guard(client, "prompt")

        assert len(calls) == 1

    @pytest.mark.anyio
    async def test_repair_pass_is_opt_in_and_costs_a_second_call(self, monkeypatch):
        monkeypatch.setenv("LLM_JSON_REPAIR_PASS", "1")
        client, calls = _fake_client(
            ["not json", json.dumps(_valid_payload())]
        )

        result = await transformer._complete_with_json_guard(client, "prompt")

        assert result["document_title"] == "Deliberate Practice and Expertise"
        assert len(calls) == 2
        assert calls[0]["response_format"] == {"type": "json_object"}
        # The repair call de-escalates out of JSON mode for compatibility.
        assert "response_format" not in calls[1]

    @pytest.mark.anyio
    async def test_full_size_document_is_transformed_in_a_single_call(
        self, monkeypatch
    ):
        monkeypatch.delenv("MAX_CHUNK_CHARS", raising=False)
        monkeypatch.delenv("LLM_JSON_REPAIR_PASS", raising=False)
        # Just under the 50,000 character request cap - the largest document the
        # public API can accept.
        document = (SOURCE_TEXT + " ") * 122
        assert 40000 < len(document) <= 50000

        calls: List[Dict[str, Any]] = []

        async def fake_request_completion(client_arg, messages, json_mode=False):
            calls.append({"json_mode": json_mode, "messages": messages})
            return json.dumps(_valid_payload())

        monkeypatch.setattr(
            transformer, "_request_completion", fake_request_completion
        )

        result = await transformer.transform_document(document)

        assert len(calls) == 1
        assert calls[0]["json_mode"] is True
        assert [b.block_id for b in result.blocks] == [1, 2]


class TestThinkingModeDisabled:
    """Thinking mode is off; JSON output is structured and non-truncating."""

    @pytest.mark.anyio
    async def test_deepseek_host_disables_thinking_by_auto_detect(self, monkeypatch):
        monkeypatch.setenv("OPENAI_BASE_URL", "https://api.deepseek.com")
        monkeypatch.delenv("LLM_DISABLE_THINKING", raising=False)
        monkeypatch.delenv("LLM_MAX_TOKENS", raising=False)
        client, calls = _fake_client(json.dumps(_valid_payload()))

        await transformer._request_completion(client, [], json_mode=True)

        kwargs = calls[0]
        assert kwargs["extra_body"] == {"thinking": {"type": "disabled"}}
        assert kwargs["response_format"] == {"type": "json_object"}
        assert kwargs["max_tokens"] == transformer.DEFAULT_MAX_OUTPUT_TOKENS

    @pytest.mark.anyio
    async def test_non_deepseek_host_omits_the_thinking_parameter(self, monkeypatch):
        monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        monkeypatch.delenv("LLM_DISABLE_THINKING", raising=False)
        client, calls = _fake_client(json.dumps(_valid_payload()))

        await transformer._request_completion(client, [], json_mode=True)

        assert "extra_body" not in calls[0]
        assert calls[0]["response_format"] == {"type": "json_object"}

    @pytest.mark.anyio
    async def test_explicit_flag_forces_thinking_off_on_any_provider(self, monkeypatch):
        monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        monkeypatch.setenv("LLM_DISABLE_THINKING", "1")
        client, calls = _fake_client(json.dumps(_valid_payload()))

        await transformer._request_completion(client, [], json_mode=True)

        assert calls[0]["extra_body"] == {"thinking": {"type": "disabled"}}

    @pytest.mark.anyio
    async def test_truncated_completion_raises_actionable_error(self, monkeypatch):
        monkeypatch.setenv("LLM_MAX_TOKENS", "256")
        client, calls = _fake_client('{"blocks": [{"headline": "cut off', "length")

        with pytest.raises(transformer.ResponseTruncatedError) as excinfo:
            await transformer._request_completion(client, [], json_mode=True)

        assert "LLM_MAX_TOKENS" in str(excinfo.value)
        assert len(calls) == 1

    def test_health_exposes_the_call_budget(self):
        body = client.get("/api/health").json()
        assert body["thinking_disabled"] in (True, False)
        assert body["structured_output"] == "json_object"
        assert body["max_provider_calls_per_request"] == 1
        assert body["json_repair_pass"] is False
