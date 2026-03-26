### Project Name

BoundaryBench

### Your Team

Solo submission.

### Problem Statement

Frontier models can look strong on structured tasks while still failing a more basic metacognitive question: do they know when the evidence supports one unique answer, and when it does not?

Most evaluations reward answer generation, but they do not cleanly separate solving a determinate problem from recognizing that a problem is underdetermined. A model that answers every question correctly when the answer exists may still overcommit when it does not — claiming certainty where none is warranted. BoundaryBench measures that distinction.

It targets the Metacognition track by evaluating whether a model can detect the boundary between tables that support one exact answer and tables that are missing information or allow multiple valid answers. The benchmark asks not only "can the model answer?" but also "does the model know whether its answer is uniquely justified?"

This matters because overcommitment is invisible to standard accuracy metrics. A model that answers 95% of questions correctly may look excellent, but if it also claims certainty on 40% of questions where no unique answer exists, it is systematically misleading users about the reliability of its responses.

### Task & benchmark construction

BoundaryBench is a synthetic closed-world table benchmark. Each item contains a small table (3–5 rows, 2–5 columns), a question, a gold decision (answer or abstain), an acceptable answer set for determinate items, and a failure_family label for underdetermined items.

The benchmark uses a two-stage design:

1. **Stage 1 (forced answer):** The model must give its best single answer, even if uncertain. This prevents simple refusal and forces the model to engage with the evidence.
2. **Stage 2 (boundary judgment):** The model must then judge whether that answer was determinate (uniquely supported by the table) or underdetermined (missing information or multiple valid answers).

This design is central. A single-stage abstain prompt can collapse into instruction-following — the model learns to say "I don't know" as a pattern rather than genuinely evaluating whether the evidence supports a unique answer. By forcing an answer first and asking for a boundary judgment second, BoundaryBench separates answer generation ability from metacognitive self-evaluation. The two-stage structure also enables detection of object-meta mismatch: cases where the model's answer text correctly identifies an issue but its boundary judgment contradicts that reasoning.

For determinate items, success requires both a correct answer and a determinate boundary label. For underdetermined items, success requires an underdetermined boundary label regardless of the forced answer.

### Dataset

The dataset contains 500 items, all synthetic and authored for this benchmark. This reduces contamination risk from memorized public QA sets and keeps every label auditable. The dataset was constructed in multiple rounds with automated and manual quality audits between each round, including verification of all arithmetic, filter conditions, and tie values.

- 250 determinate items spanning three question types: single lookup, filter+compare, and aggregation
- 250 underdetermined items, uniformly distributed across five failure families:

| Failure family | Items | Description |
|----------------|-------|-------------|
| missing_value | 50 | A cell needed for the answer is blank |
| no_satisfying_row | 50 | The information needed is genuinely absent from the table |
| tie | 50 | Multiple rows share the exact same top value |
| ordering_ambiguity | 50 | Question requires combining criteria with no defined weighting |
| incomplete_agg | 50 | A missing cell blocks a required aggregation |

This uniform distribution (50 items per family) enables statistically meaningful per-family analysis. Differences of 10 percentage points or more in false certainty rate are detectable with high confidence, allowing the benchmark to distinguish which types of underdetermination each model handles well or poorly.

### Technical details

BoundaryBench is implemented with the kaggle-benchmarks SDK using structured JSON outputs in both stages. The primary metric is false_certainty_rate: the fraction of underdetermined items where the model commits to determinate. Secondary metrics include answer_accuracy, boundary_accuracy, and missed_certainty_rate.

Because the benchmark uses synthetic local tables rather than open-domain facts, the model must rely on the displayed evidence rather than background knowledge. This keeps the signal focused on metacognitive boundary awareness rather than factual recall.

To verify that the signal is not an artifact of prompt wording, the false certainty rate was tested across three distinct prompt formulations (original, rephrased, compact). All three produce identical false certainty rates (std=0.000), confirming the signal is completely prompt-invariant and reflects a genuine model property.

### Results, insights, and conclusions

**Leaderboard (500 items, overall accuracy):**

| Model | Type | Overall accuracy |
|-------|------|-----------------|
| Qwen 3 235B | Open | 0.85 |
| Claude Sonnet 4.6 | Proprietary | 0.83 |
| Claude Sonnet 4 | Proprietary | 0.81 |
| Gemini 2.5 Flash | Proprietary | 0.79 |
| Gemini 2.5 Pro | Proprietary | 0.65 |

The 0.20 spread across five models confirms strong discriminatory power. Notably, the open-source Qwen 3 235B outperforms all proprietary models, suggesting that metacognitive boundary awareness does not correlate with model licensing or provider. Gemini 2.5 Pro scores substantially lower than Flash, showing that model size within the same family does not automatically improve this capability.

**False certainty by failure family (Gemini 2.5 Flash, n=50 per family):**

| Failure family | FC rate |
|----------------|---------|
| no_satisfying_row | **0.940** |
| missing_value | **0.700** |
| incomplete_agg | 0.200 |
| tie | 0.122 |
| ordering_ambiguity | 0.118 |

This is the central finding. When the table lacks information needed to answer, the model commits to determinate 94% of the time. When a required cell is blank, the rate is 70%. But when the problem is structural ambiguity — tied values or undefined orderings — the model detects it reliably.

This hierarchy reveals that false certainty is primarily a failure of **absence detection**, not ambiguity detection. Models can recognize when two candidates tie for first place, but they struggle to recognize when the evidence needed to answer simply is not present. This distinction is invisible to any benchmark that reports only aggregate accuracy.

**Confidence calibration:** False certainty cases show average boundary confidence of 0.995, compared to 0.985 for correct cases. The model is more confident when it is wrong. This means confidence scores cannot be used as a post-hoc filter for overcommitment — the model's own uncertainty signal is inverted precisely where it matters most.

**Object-meta mismatch:** In 104 out of 250 underdetermined items (41.6%), the model's answer text explicitly acknowledges the problem, then the structured boundary judgment overrides it with full confidence. For example, the model states "battery hours not available in the table" yet marks the question as determinate with confidence 1.00. Similarly, it states "none of the animals in the table are black" and still commits to determinate. This dissociation between object-level reasoning and meta-level judgment is the most striking failure pattern discovered by BoundaryBench, and it cannot be detected by any benchmark that only evaluates answer correctness.

**Conclusion:** Frontier models systematically overcommit on whether an answer is uniquely justified, even when their own reasoning identifies the problem. The failure-family hierarchy — from 94% false certainty on absent information to 12% on structural ambiguity — provides actionable diagnostic signal that aggregate accuracy cannot capture. BoundaryBench demonstrates that raw answer generation and metacognitive boundary awareness are separable capabilities, and that current frontier models have substantial room for improvement on the latter.

### Organizational affiliations

No organizational affiliation.

### References & citations

- DeepMind. Measuring progress toward AGI: A cognitive framework. 2025.
- Kadavath et al. Language Models (Mostly) Know What They Know. arXiv:2207.05221, 2022.
- Steyvers & Peters. Metacognition and Uncertainty Communication in Humans and Large Language Models. Perspectives on Psychological Science, 2025.
- Yona et al. Large Language Models Lack Essential Metacognition for Reliable Medical Reasoning. Nature Communications, 2024.
- Tao et al. Reflection-Bench: Probing AI with Reflection. arXiv:2410.16270, 2024.
- Lyu et al. KalshiBench: Measuring LLM Epistemic Calibration via Prediction Markets. arXiv:2512.16030, 2025.
- Kaggle Benchmarks documentation and SDK examples.
