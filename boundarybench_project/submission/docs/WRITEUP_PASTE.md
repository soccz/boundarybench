### Project Name

BoundaryBench

### Your Team

Solo submission.

### Problem Statement

Frontier models can look strong on structured tasks while still failing a more basic metacognitive question: do they know when the evidence supports one unique answer, and when it does not?

Most evaluations reward answer generation, but they do not cleanly separate solving a determinate problem from recognizing that a problem is underdetermined. A model that answers every question correctly when the answer exists may still overcommit when it does not. BoundaryBench measures that distinction.

It targets the Metacognition track by evaluating whether a model can detect the boundary between tables that support one exact answer and tables that are missing information or allow multiple valid answers. The benchmark asks not only "can the model answer?" but also "does the model know whether its answer is uniquely justified?"

### Task & benchmark construction

BoundaryBench is a synthetic closed-world table benchmark. Each item contains a small table (3–5 rows, 2–5 columns), a question, a gold decision (answer or abstain), an acceptable answer set for determinate items, and a failure_family label for underdetermined items.

The benchmark uses a two-stage design:

1. **Stage 1 (forced answer):** The model must give its best single answer, even if uncertain. This prevents simple refusal.
2. **Stage 2 (boundary judgment):** The model must judge whether that answer was determinate (uniquely supported by the table) or underdetermined (missing information or multiple valid answers).

This design is central. A single-stage abstain prompt can collapse into instruction-following — the model learns to say "I don't know" without actually evaluating whether the evidence supports a unique answer. By forcing an answer first and asking for a boundary judgment second, BoundaryBench separates answer generation ability from metacognitive self-evaluation.

For determinate items, success requires both a correct answer and a determinate boundary label. For underdetermined items, success requires an underdetermined boundary label regardless of the forced answer.

### Dataset

The dataset contains 500 items, all synthetic and authored for this benchmark. This reduces contamination risk from memorized public QA sets and keeps every label auditable. The dataset was constructed in multiple rounds with automated and manual quality audits between each round.

- 250 determinate items (single lookup, filter+compare, aggregation)
- 250 underdetermined items, uniformly distributed across five failure families:

| Failure family | Items | Description |
|----------------|-------|-------------|
| missing_value | 50 | A cell needed for the answer is blank |
| no_satisfying_row | 50 | The information needed is genuinely absent from the table |
| tie | 50 | Multiple rows share the exact same top value |
| ordering_ambiguity | 50 | Question requires combining criteria with no defined weighting |
| incomplete_agg | 50 | A missing cell blocks a required aggregation |

This uniform distribution enables statistically meaningful per-family analysis. With 50 items per family, differences of 10 percentage points or more in false certainty rate are detectable with high confidence.

### Technical details

BoundaryBench is implemented with the kaggle-benchmarks SDK using structured JSON outputs in both stages. The primary metric is false_certainty_rate: the fraction of underdetermined items where the model commits to determinate. Secondary metrics include answer_accuracy, boundary_accuracy, and missed_certainty_rate.

Because the benchmark uses synthetic local tables rather than open-domain facts, the model must rely on the displayed evidence rather than background knowledge. This keeps the signal focused on metacognitive boundary awareness rather than factual recall.

The false certainty signal was verified across three distinct prompt formulations (original, rephrased, compact). All three produce identical false certainty rates (std=0.000), confirming the signal is completely prompt-invariant.

### Results, insights, and conclusions

**Leaderboard (500 items, overall accuracy):**

| Model | Type | Overall accuracy |
|-------|------|-----------------|
| Qwen 3 235B | Open | 0.85 |
| Claude Sonnet 4.6 | Proprietary | 0.83 |
| Claude Sonnet 4 | Proprietary | 0.81 |
| Gemini 2.5 Flash | Proprietary | 0.79 |
| Gemini 2.5 Pro | Proprietary | 0.65 |

The 0.20 spread across five models confirms strong discriminatory power. Notably, the open-source Qwen 3 235B outperforms all proprietary models, suggesting that metacognitive boundary awareness does not correlate with model licensing or provider.

**False certainty by failure family (Gemini 2.5 Flash, n=50 per family):**

| Failure family | FC rate |
|----------------|---------|
| no_satisfying_row | **0.940** |
| missing_value | **0.700** |
| incomplete_agg | 0.200 |
| tie | 0.122 |
| ordering_ambiguity | 0.118 |

This is the central finding. When the table lacks information needed to answer, the model commits to determinate 94% of the time. But when the problem is structural ambiguity — tied values or undefined orderings — the model detects it reliably. False certainty is primarily a failure of **absence detection**, not ambiguity detection. This distinction is invisible to any benchmark that reports only aggregate accuracy.

**Confidence calibration:** False certainty cases show avg boundary confidence of 0.995 vs 0.985 for correct cases. The model is more confident when wrong — confidence scores cannot serve as a post-hoc filter for overcommitment.

**Object-meta mismatch:** In 104/250 underdetermined items (41.6%), the model's answer text explicitly acknowledges the problem, then the boundary judgment overrides it with full confidence. For example, the model states "battery hours not available in the table" then marks the question as determinate (conf=1.00). This dissociation between object-level reasoning and meta-level judgment cannot be detected by accuracy-only benchmarks.

**Conclusion:** Frontier models systematically overcommit on whether an answer is uniquely justified, even when their own reasoning identifies the problem. The failure-family hierarchy provides actionable diagnostic signal that aggregate accuracy cannot capture.

### Organizational affiliations

No organizational affiliation.

### References & citations

- DeepMind. Measuring progress toward AGI: A cognitive framework.
- Kaggle Benchmarks documentation and SDK examples.
