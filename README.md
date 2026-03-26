# BoundaryBench

**A metacognition benchmark for measuring epistemic boundary awareness in frontier AI models.**

> Do AI models know when the evidence supports one unique answer — and when it does not?

BoundaryBench is a benchmark submitted to the [Kaggle "Measuring AGI — Cognition and Values"](https://www.kaggle.com/competitions/measuring-agi) competition (Metacognition track). It evaluates whether large language models can distinguish between **determinate** questions (where the given data uniquely determines an answer) and **underdetermined** questions (where information is missing or ambiguous).

## Key Insight

Frontier models can solve determinate structured problems while **systematically overcommitting** on whether the available evidence uniquely supports an answer. This failure — **false certainty** — is invisible to benchmarks that only measure answer accuracy.

## How It Works

BoundaryBench uses a **two-stage evaluation** on synthetic closed-world tables:

1. **Stage 1 (Forced Answer):** The model must provide its best single answer, even if uncertain.
2. **Stage 2 (Boundary Judgment):** The model must judge whether that answer was *determinate* (uniquely supported) or *underdetermined* (missing info or multiple valid answers).

This separates **answer generation ability** from **metacognitive self-evaluation** — a distinction single-stage abstain prompts cannot capture.

## Dataset

500 synthetic table-QA items, evenly split:

- **250 determinate** items (single lookup, filter+compare, aggregation)
- **250 underdetermined** items across 5 failure families:

| Failure Family | Items | Description |
|---|---|---|
| `missing_value` | 50 | A cell needed for the answer is blank |
| `no_satisfying_row` | 50 | Required information is absent from the table |
| `tie` | 50 | Multiple rows share the exact same top value |
| `ordering_ambiguity` | 50 | Combining criteria with no defined weighting |
| `incomplete_agg` | 50 | A missing cell blocks a required aggregation |

## Results

### Leaderboard (500 items)

| Model | Overall Accuracy | False Certainty Rate |
|---|---|---|
| Qwen 3 235B (Open) | 0.85 | — |
| Claude Sonnet 4.6 | 0.83 | — |
| Claude Sonnet 4 | 0.81 | — |
| Gemini 2.5 Flash | 0.79 | 0.416 |
| Gemini 2.5 Pro | 0.65 | — |

### False Certainty by Failure Family (Gemini 2.5 Flash)

| Failure Family | FC Rate |
|---|---|
| `no_satisfying_row` | **0.940** |
| `missing_value` | **0.700** |
| `incomplete_agg` | 0.200 |
| `tie` | 0.122 |
| `ordering_ambiguity` | 0.118 |

**Core finding:** False certainty is primarily a failure of **absence detection**, not ambiguity detection. Models recognize structural ambiguity (ties, ordering) but fail to notice when evidence is simply not present.

### Object-Meta Mismatch

In 41.6% of underdetermined items, the model's answer text **explicitly acknowledges** the problem — then the structured boundary judgment overrides it with `determinate` at confidence > 0.99.

## Metrics

- **False Certainty Rate** — fraction of underdetermined items labeled `determinate`
- **Answer Accuracy** — correctness on determinate items
- **Boundary Accuracy** — correct boundary judgment across all items
- **Object-Meta Mismatch** — cases where reasoning contradicts the boundary label

## Project Structure

```
├── src/                          # Core scoring and task logic
│   ├── table_world_core.py       # Prompt construction and scoring
│   └── boundarybench_task.py     # Kaggle SDK task wrapper
├── data/                         # JSONL datasets (pilot → 500 items)
├── boundarybench_project/        # Submission assets
│   └── submission/
│       └── docs/
│           ├── FINAL_WRITEUP.md
│           ├── RESULTS_SUMMARY.md
│           └── SUBMISSION_CHECKLIST.md
├── kaggle_boundarybench_*.py     # Kaggle notebook scripts (various versions)
├── BOUNDARY_BENCH_SPEC.md        # Full benchmark specification
├── FINDINGS_V2.md                # Experimental findings
└── ANALYSIS_NEXT_STEPS.md        # Analysis roadmap
```

## License

CC0 — this benchmark is released into the public domain per Kaggle competition requirements.
