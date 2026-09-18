"""
Cognita - Pydantic v2 schemas.

These schemas define the strict JSON contract between the LLM orchestrator
(transformer.py) and the React frontend. Any response that does not conform is
rejected before it ever reaches the client, which prevents hallucinated
structures from breaking the reader workspace.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class MicroQuizOption(BaseModel):
    id: str = Field(description="Unique letter identifier: A, B, C, or D")
    text: str = Field(description="Text of the multiple-choice option")
    is_correct: bool = Field(description="True if this is the correct answer")
    feedback: str = Field(
        description="Immediate feedback explaining why this is correct or incorrect"
    )


class MicroQuiz(BaseModel):
    question: str = Field(
        description="A quick conceptual comprehension question testing core logic"
    )
    options: List[MicroQuizOption] = Field(
        min_length=3, max_length=4, description="Three or four answer options"
    )
    explanation: str = Field(
        description="Clear explanation reinforcing the cognitive takeaway"
    )


class ReadingBlock(BaseModel):
    block_id: int = Field(description="Sequential identifier starting at 1")
    headline: str = Field(
        description="Ultra-concise, engaging sub-heading for the concept"
    )
    estimated_reading_seconds: int = Field(
        ge=5,
        le=600,
        description="Realistic reading time (based on 130 WPM for neurodivergent pacing)",
    )
    bionic_chunks: List[str] = Field(
        description="Sentences pre-segmented into short cognitive reading lines (15-20 words max)"
    )
    key_takeaway: str = Field(
        description="One single high-impact bullet summarizing this block"
    )
    source_citation_anchor: str = Field(
        description="Exact verbatim sentence or phrase from the original source text for verification"
    )
    quiz: Optional[MicroQuiz] = Field(
        default=None,
        description="Interactive micro-quiz every 2-3 blocks to re-engage attention",
    )


class TransformationResponse(BaseModel):
    document_title: str = Field(description="Short descriptive title of the source text")
    overall_read_time_minutes: int = Field(
        ge=1, description="Total estimated focused reading time in minutes"
    )
    difficulty_score: int = Field(description="Scale 1-10 assessing linguistic complexity")
    executive_summary: str = Field(
        description="3-sentence high-level conceptual orientation"
    )
    blocks: List[ReadingBlock] = Field(description="Ordered list of cognitive reading blocks")
    nuance_caveats: List[str] = Field(
        description="Academic caveats or subtle technical points that readers must not overlook"
    )


class TransformRequest(BaseModel):
    raw_text: str = Field(
        ...,
        min_length=100,
        max_length=50000,
        description="Raw academic text input",
    )


def response_json_schema_string() -> str:
    """Return a compact, human/LLM readable rendering of the target contract.

    The LLM is instructed to emit JSON matching this schema. We render the
    schema explicitly inside the prompt because not every OpenAI-compatible
    provider supports strict structured-output enforcement.
    """
    return """{
  "document_title": "string",
  "overall_read_time_minutes": 0,
  "difficulty_score": 0,
  "executive_summary": "string (exactly 3 sentences)",
  "blocks": [
    {
      "block_id": 1,
      "headline": "string",
      "estimated_reading_seconds": 0,
      "bionic_chunks": ["string", "string"],
      "key_takeaway": "string",
      "source_citation_anchor": "verbatim substring copied from the user's source text",
      "quiz": {
        "question": "string",
        "options": [
          {"id": "A", "text": "string", "is_correct": true, "feedback": "string"},
          {"id": "B", "text": "string", "is_correct": false, "feedback": "string"},
          {"id": "C", "text": "string", "is_correct": false, "feedback": "string"}
        ],
        "explanation": "string"
      }
    }
  ],
  "nuance_caveats": ["string"]
}"""
