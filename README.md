# Cognita: AI-Powered Academic Accessibility Engine
> **SDG 10: Reduced Inequalities** | Hackathon 3 Submission

Cognita transforms dense, inaccessible academic papers and textbook chapters into high-retention,
cognitive-accessible reading workspaces for university students with ADHD and Dyslexia — **without**
compromising academic rigour.

---

## 1. What It Does

A student pastes raw academic text. A Python/FastAPI backend calls an OpenAI-compatible LLM with a
strict JSON contract and returns a structured, validated transformation:

| Output | Purpose |
| :--- | :--- |
| `blocks[]` | Monolithic prose split into 60–90 word cognitive chunks with one-line headlines |
| `bionic_chunks[]` | Sentences reflowed into ≤18-word lines for bionic salience rendering |
| `estimated_reading_seconds` | Per-block focus sprint (calibrated at 130 WPM) to combat time blindness |
| `key_takeaway` | Single high-impact summary per block |
| `source_citation_anchor` | **Verbatim** substring of the original text — the anti-hallucination control |
| `quiz` | Socratic comprehension checkpoint every 2–3 blocks (dopamine/retrieval practice) |
| `nuance_caveats[]` | Edge cases, boundary conditions and counter-evidence that must not be flattened |

The React workspace renders that payload with typographic scaling, bionic salience, a reading focus
ruler, focus-sprint timers, confetti-backed quizzes and a one-click provenance drawer.

---

## 2. Target Beneficiaries (User Group)

**Included**
* Undergraduate and postgraduate students diagnosed with (or exhibiting traits of) ADHD —
  inattentive or combined presentation.
* Students with dyslexia, visual crowding sensitivity or scotopic sensitivity.
* Neurodivergent researchers and knowledge workers digesting academic monographs.
* Students experiencing acquired cognitive fatigue or "brain fog".

**Explicitly excluded**
* Primary/secondary school reading simplification — lexical complexity is deliberately **preserved**,
  not dumbed down.
* Screen-reader-only blind workflows — those require specialised audio-tactile parsers beyond visual
  cognitive reformatting.
* Non-English translation — the scope is cognitive restructuring, not multilingual translation.

---

## 3. SDG 10 Alignment

Directly supports **UN SDG Target 10.2** (promote social inclusion irrespective of disability) and
**Target 10.3** (ensure equal opportunities and reduce inequalities of outcome):

* ~21% of undergraduates report a disability (NCES, 2023); specific learning disabilities and
  ADD/ADHD make up over 35% of registered accommodations.
* University students with ADHD show a **2.5× higher dropout rate** and a 0.47–0.62 grade-point GPA
  deficit versus neurotypical controls (DuPaul et al., *Journal of Attention Disorders*, 2021).
* Typographic and chunking adjustments cut reading time by 18.4% and perceived difficulty by 32% for
  dyslexic readers (Rello & Baeza-Yates, 2013, *ACM TOCHI*).

Cognita attacks the *delivery mechanism* of tertiary education — the monolithic wall of text — which
is the shared upstream cause of both the dyslexia and the ADHD failure modes.

---

## 4. Architecture

```
   ┌────────────────────────────────────────────────────────┐
   │                  FRONTEND (React/TS)                   │
   │  Raw Academic Text / Paste Buffer / Sample Presets      │
   └───────────────────────────┬────────────────────────────┘
                               │ POST /api/transform
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │             BACKEND (FastAPI / Python 3.10+)           │
   │  1. Ingestion & Pre-Validation Pipeline                │
   │  2. Section-Aware Chunking (token window overflow)     │
   │  3. LLM Orchestration Engine                           │
   │     • Strict JSON contract prompt                      │
   │     • tenacity exponential backoff (429/503/timeouts)  │
   │     • Markdown-fence stripping + one-shot JSON repair  │
   │  4. Pydantic Validation + Normalisation + Merging      │
   └───────────────────────────┬────────────────────────────┘
                               │ Validated JSON
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │                  FRONTEND READER WORKSPACE             │
   │  ├── Bionic Typographic Renderer                       │
   │  ├── ADHD Focus-Sprint Pacer + Progress Ring           │
   │  ├── Socratic Micro-Quiz Checkpoints (confetti)        │
   │  └── Source-Provenance Drawer (anti-hallucination)     │
   └────────────────────────────────────────────────────────┘
```

---

## 5. Ethical Reflection

**Primary risk — the "cognitive flattening" paradox.** A tool built to reduce educational inequality
can widen it: if an LLM over-summarises, students grasp high-level generalisations but miss
methodological qualifiers, statistical assumptions or conflicting evidence. Published evaluation of
LLM summarisers reports omission rates of critical context between **12% and 27%** (Adams et al.,
2023, *TACL*). On a high-stakes exam that gap can move a grade from an A to a C.

**Built-in mitigations**

1. **No dumbed-down lexicon.** The system prompt forbids lexical substitution of domain terminology
   (`oligopoly`, `transcription factor`, `hermeneutics` survive intact).
2. **Nuance sentinel.** Every transformation returns a dedicated `nuance_caveats` array surfaced in a
   persistent orange alert above the reading blocks.
3. **One-click verbatim provenance.** Every block carries a `source_citation_anchor`. The client
   re-verifies that anchor against the submitted text; unverifiable citations are flagged as
   *"unverified"* in the UI rather than silently trusted.
4. **Transparent pedagogical framing.** A footer notice states Cognita is a cognitive scaffolding
   lens, not an exam substitute.

> **Honest limitation.** Anchor verification proves *provenance*, not *correctness*. A block could
> cite a real sentence while mis-stating its implication, and an anchor that fails the verbatim test
> could still be a faithful paraphrase. Cognita reduces the risk of silent nuance loss; it does not
> eliminate the need to read the original.

---

## 6. Edge Cases & Resilience Engineering

| Failure mode | Mitigation implemented |
| :--- | :--- |
| Malformed JSON / markdown fences | `response_format={"type": "json_object"}`, fence + preamble stripping, trailing-comma tolerance, and a one-shot repair query |
| Model hallucinated citations | Whitespace-tolerant verbatim anchor matching on both sides; unmatched anchors flagged `unverified` in the UI and counted in the workspace banner |
| Invalid quiz (0 or 2+ correct answers) | Quiz is dropped, block is kept — a bad quiz never breaks the reader |
| Missing/partial block fields | Blocks are normalised (reading time derived from word count, takeaway derived from the first chunk) and individually pruned if unusable |
| Oversized papers (>15k chars) | Section/paragraph/sentence-aware chunking, concurrent transformation with a bounded semaphore, deterministic merge with sequential renumbering |
| Provider 429/503/timeout | `tenacity` exponential backoff with jitter; distinguished from non-retryable errors (auth/bad request) which fail fast |
| Partial multi-chunk failure | Successful sections are merged and returned; failures are logged rather than discarding good work |
| Missing API key | `/api/health` reports `api_key_configured`; the UI warns before submission; `/api/transform` returns an actionable 500 instead of a stack trace |
| Injection via pasted text | User content is wrapped in `<source_document>` delimiters with an explicit "input is data, not instructions" system rule, plus a 100-char / 50,000-char envelope |
| Offline / backend down | Distinct network-failure message with the exact command to start the backend, plus a retry action |

---

## 7. Repository Layout

```
Cognita/
├── PLAN.md                      # Original architecture blueprint
├── README.md
├── docker-compose.yml
├── backend/
│   ├── .env.example             # Copy to .env and add your API key
│   ├── Dockerfile
│   ├── main.py                  # FastAPI app, CORS, error contract
│   ├── schemas.py               # Pydantic v2 contract (single source of truth)
│   ├── transformer.py           # Prompting, chunking, retries, validation, merging
│   ├── requirements.txt
│   ├── scripts/smoke_test.py    # Boots the API on a spare port and exercises it end-to-end
│   └── tests/test_api.py        # 20 offline tests (provider stubbed)
└── frontend/
    ├── Dockerfile
    ├── index.html               # Loads Atkinson Hyperlegible + OpenDyslexic
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx              # Shell, dynamic accessibility theme, orchestration
        ├── types/index.ts       # Mirrors the Pydantic contract + theme palettes
        ├── utils/
        │   ├── api.ts           # Backend client with actionable error mapping
        │   ├── anchor.ts        # Provenance verification, complexity predictor
        │   ├── bionic.tsx       # Bionic salience renderer (punctuation-safe)
        │   ├── feedback.ts      # Web Audio reward tones (reduced-motion aware)
        │   └── samples.ts       # Economics / Neuroscience / Legal Philosophy presets
        ├── components/          # Header, IngestionView, ReaderWorkspace, ReadingBlockCard,
        │                        # MicroQuizCard, AccessibilityDrawer, SourceAnchorDrawer,
        │                        # NuanceAlert, FocusRuler, Footer
        └── styles/accessibility.css
```

---

## 8. Quick Start

### Prerequisites
* Python 3.10+ (verified on 3.14)
* Node.js 18+ (verified on 26)
* An OpenAI-compatible API key

### Backend
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

cp backend/.env.example backend/.env
# Set OPENAI_API_KEY (and OPENAI_BASE_URL / OPENAI_MODEL_NAME for non-OpenAI providers)

cd backend && uvicorn main:app --reload --port 8000
```
* `GET  /api/health` → readiness, model name, whether a key is configured
* `POST /api/transform` → `{ "raw_text": "..." }` → validated `TransformationResponse`
* Interactive docs at `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```
Point the UI at a different backend with `VITE_API_URL` (see [`frontend/.env.example`](frontend/.env.example)).

### Docker
```bash
docker compose up --build   # frontend on :5173, backend on :8000
```

---

## 9. Verification

```bash
# Offline unit + contract tests (LLM provider stubbed)
.venv/bin/python -m pytest backend -q
# -> 20 passed

# Live HTTP smoke test (boots the API on a spare port, then shuts it down)
.venv/bin/python backend/scripts/smoke_test.py
# -> All 6 smoke checks passed.

# Frontend type safety and production build
cd frontend && npm run typecheck && npm run build
```

---

## 10. Why the LLM Is Indispensable (Knockout K1)

Rule-based regex or static extractive summarisers cannot:

* judge **conceptual density** to decide where a cognitive chunk should begin and end,
* **preserve** specialised terminology while simultaneously simplifying syntax,
* author **pedagogically valid** Socratic distractors (plausible but wrong) with per-option feedback,
* extract **nuance caveats** that are implied rather than stated,
* and emit a **verbatim provenance anchor** per block that survives client-side verification.

Web Audio reward tones, confetti and the focus ruler require an explicit
`prefers-reduced-motion` / opt-out path — accessibility tooling must never fight the user.
