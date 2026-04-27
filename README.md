# BoundaryBench

**A metacognition benchmark for measuring epistemic boundary awareness in frontier AI models.**

> Does the model know when the evidence supports one unique answer — and when it does not?

BoundaryBench was submitted to the [Kaggle "Measuring AGI — Cognition and Values"](https://www.kaggle.com/competitions/measuring-agi) competition (Metacognition track, Apr 2026). It evaluates whether large language models can distinguish between **determinate** questions (where the given data uniquely determines an answer) and **underdetermined** questions (where information is missing or ambiguous).

- **Project page:** https://soccz.github.io/projects/boundarybench/
- **Kaggle benchmark:** https://www.kaggle.com/benchmarks/s0occz/boundarybench

## Key Insight

Frontier models can solve determinate structured problems while **systematically overcommitting** on whether the available evidence uniquely supports an answer. This failure — **false certainty** — is invisible to benchmarks that only measure answer accuracy.

The headline finding: a steep gradient from **96% false certainty on absent information** down to **6% on underspecified criteria**. Models can detect ambiguity but fail at absence detection.

## How It Works

BoundaryBench uses a **two-stage evaluation** on synthetic closed-world tables:

1. **Stage 1 (Forced Answer):** The model must provide its best single answer, even if uncertain.
2. **Stage 2 (Boundary Judgment):** The model must judge whether that answer was *determinate* (uniquely supported) or *underdetermined* (missing info or multiple valid answers).

By forcing an answer first, this design prevents single-stage abstain prompts from collapsing into instruction-following. It separates **answer generation ability** from **boundary detection**.

## Dataset

500 synthetic table-QA items, evenly split:

- **250 determinate** items (single lookup, filter+compare, aggregation)
- **250 underdetermined** items across six failure families:

| Failure Family | Items | Description |
|---|---|---|
| `missing_value` | 50 | A cell needed for the answer is blank |
| `no_satisfying_row` | 50 | Required information is absent from the table |
| `tie` | 49 | Multiple rows share the exact same top value |
| `criterion_underspecification` | 48 | Question requires combining criteria with no defined weighting |
| `incomplete_agg` | 50 | A missing cell blocks a required aggregation |
| `ordering_ambiguity` | 3 | Temporal/sequence ordering is ambiguous (exploratory) |

## Results

### Leaderboard (500 items)

| Model | Type | Overall | Answer acc | Boundary acc | FC rate |
|---|---|---|---|---|---|
| Qwen 3 235B | Open | **0.836** | 0.904 | 0.874 | 0.228 |
| Claude Sonnet 4.6 | Proprietary | 0.828 | 0.768 | **0.944** | **0.112** |
| Claude Sonnet 4 | Proprietary | 0.792 | 0.952 | 0.810 | 0.356 |
| Gemini 2.5 Flash | Proprietary | 0.782 | **0.980** | 0.792 | 0.416 |

The overall accuracy spread is only 0.054, but the false certainty rate spans **0.304** — revealing that aggregate accuracy hides large differences in metacognitive behavior.

### Answer–Boundary Trade-off

Claude Sonnet 4.6 has the **lowest** answer accuracy (0.768) but the **highest** boundary accuracy (0.944) and lowest false certainty (0.112). Conversely, Gemini 2.5 Flash hits near-perfect answer accuracy (0.980) with the highest false certainty (0.416). Improved metacognitive awareness appears to come at a cost: the model that is most cautious about claiming certainty also hedges more on forced answers.

### Cross-Model Failure Profiles (False Certainty Rate)

| Failure family | Flash | Sonnet 4 | Sonnet 4.6 | Qwen 3 |
|---|---|---|---|---|
| `no_satisfying_row` | **0.960** | 0.580 | 0.060 | 0.080 |
| `missing_value` | 0.700 | 0.460 | 0.360 | 0.360 |
| `tie` | 0.184 | **0.694** | 0.122 | 0.184 |
| `incomplete_agg` | 0.160 | 0.040 | 0.000 | 0.260 |
| `criterion_underspec` | 0.062 | 0.021 | 0.000 | 0.208 |

The hierarchy is **not identical across models**. All four struggle with `missing_value`, but they diverge sharply elsewhere: Sonnet 4 fails on `tie` (0.694) while Sonnet 4.6 nearly eliminates it (0.122); Flash shows extreme `no_satisfying_row` failure (0.960) while Sonnet 4.6 and Qwen 3 largely solve it. These model-specific profiles provide diagnostic signal beyond aggregate accuracy.

### Object-Meta Mismatch

In 41.6% of underdetermined items (Gemini 2.5 Flash), the model's answer text **explicitly acknowledges** the problem — then the structured boundary judgment overrides it with `determinate` at confidence ≈ 1.00.

```
bwv2_006 — missing column ("email")
  Answer:   "The table doesn't contain email information"
  Boundary: determinate (confidence: 1.00)

bwv2_007 — missing battery_hours value
  Answer:   "battery hours not available in the table"
  Boundary: determinate (confidence: 1.00)
```

The model correctly reasons about the absence at the object level, then asserts certainty at the meta level. This dissociation is invisible to benchmarks evaluating only answer correctness.

### Robustness

Tested across three prompt formulations (original, rephrased, compact) on every model. All variants produce **identical false certainty rates** (std=0.000, range=0.000) with 100% per-item agreement — the signal is item-determined, not prompt-determined.

## Metrics

- **False Certainty Rate** — fraction of underdetermined items labeled `determinate` (primary)
- **Answer Accuracy** — correctness on determinate items
- **Boundary Accuracy** — correct boundary judgment across all items
- **Missed Certainty Rate** — determinate items wrongly flagged as underdetermined (~0 across all models)
- **Object-Meta Mismatch** — cases where Stage 1 reasoning contradicts Stage 2 label

## Limitations

- Tables are intentionally small (3–5 rows) to isolate boundary judgment; results may not transfer to larger, noisier data.
- The `no_satisfying_row` and `missing_value` families have surface-level cues (absent columns, empty cells) that simple heuristics could detect.
- The two-stage design means the model sees its own prior answer in Stage 2, potentially creating anchoring effects.
- No human baseline is included.
- The `ordering_ambiguity` family contains only 3 items and is exploratory.

## Project Structure

```
├── final_submission/                 # Final submission assets
│   ├── kaggle_boundarybench_v7_final.py
│   ├── FINAL_WRITEUP.md
│   ├── BENCHMARK_DESCRIPTION.md
│   ├── DISCUSSION_POST.md
│   ├── REVIEW_SUMMARY.md
│   └── boundarybench_cover.png
├── src/                              # Core scoring and task logic
│   ├── table_world_core.py           # Prompt construction and scoring
│   └── boundarybench_task.py         # Kaggle SDK task wrapper
├── data/                             # JSONL datasets (pilot → 500 items)
├── boundarybench_project/            # Earlier submission iterations
├── kaggle_boundarybench_v6_500_final.py  # Kaggle notebook (executed version)
├── BOUNDARY_BENCH_SPEC.md            # Full benchmark specification
└── FINDINGS_V2.md                    # Experimental findings
```

## References

- Geifman, Y. & El-Yaniv, R. (2017). Selective classification for deep neural networks. *NeurIPS.*
- Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring how models mimic human falsehoods. *ACL.*
- Yin, Z., et al. (2023). Do large language models know what they don't know? *ACL Findings.*
- Kadavath, S., et al. (2022). Language models (mostly) know what they know. arXiv:2207.05221.
- DeepMind (2025). Measuring progress toward AGI: A cognitive framework.

## License

CC0 — this benchmark is released into the public domain per Kaggle competition requirements.
