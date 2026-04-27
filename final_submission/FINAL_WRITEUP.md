# BoundaryBench: Detecting False Certainty About Answerability

## Your Team

Independent researcher.

## Problem Statement

A model reads a table of employees with departments and salaries. Asked "What is Alice's email?", it answers: "The table doesn't contain email information." Then, asked whether its answer was uniquely determined by the evidence: *determinate, confidence 1.00*. It identified the problem -- then overrode that judgment.

This is false certainty. Prior work on selective prediction (Geifman & El-Yaniv, 2017), TruthfulQA (Lin et al., 2022), SelfAware (Yin et al., 2023), and calibration (Kadavath et al., 2022) studies related capabilities. BoundaryBench differs by using synthetic tables where answerability is formally verifiable, a two-stage design separating answer generation from boundary judgment, and per-type failure diagnosis.

BoundaryBench targets the `Metacognition` track: can a model detect the boundary between tables that support one exact answer and tables where information is missing or allows multiple valid answers?

## Task & Benchmark Construction

Each item contains a small table (3-5 rows, 2-5 columns), a question, and a gold decision. The two-stage design:

1. **Stage 1 (forced answer):** The model must give its best single answer, even if uncertain.
2. **Stage 2 (boundary judgment):** The model judges whether that answer was `determinate` (uniquely supported) or `underdetermined` (missing information or multiple valid answers).

By forcing an answer first, BoundaryBench prevents simple refusal strategies that collapse into instruction-following. Both stages use structured JSON output without chain-of-thought. For determinate items, success requires a correct answer and `determinate` label. For underdetermined items, success requires `underdetermined` regardless of the forced answer.

## Dataset

500 synthetic items, constructed in multiple rounds with automated and manual quality audits. Synthetic authorship reduces contamination risk and keeps every label auditable.

- 250 determinate items (single lookup, filter+compare, aggregation)
- 250 underdetermined items across six failure families:

| Failure family | Items | Description |
|----------------|-------|-------------|
| missing_value | 50 | A cell needed for the answer is blank |
| no_satisfying_row | 50 | The information needed is genuinely absent from the table |
| tie | 49 | Multiple rows share the exact same top value |
| criterion_underspecification | 48 | Question requires combining criteria with no defined weighting |
| ordering_ambiguity | 3 | Temporal or sequence ordering is ambiguous (exploratory; excluded from per-family analysis) |
| incomplete_agg | 50 | A missing cell blocks a required aggregation |

The five larger families (48-50 items each) enable per-family analysis. At these sample sizes, large differences in false certainty rate (30 percentage points or more) are detectable with reasonable confidence, while smaller effects may require larger samples.

## Technical Details

Implemented with the `kaggle-benchmarks` SDK. Answer matching uses string normalization with numeric fallback. The primary metric is `false_certainty_rate`: the fraction of underdetermined items where the model commits to `determinate`. Secondary metrics: `answer_accuracy`, `boundary_accuracy`, `missed_certainty_rate`. Synthetic tables prevent reliance on background knowledge.

## Results, Insights, and Conclusions

### Key Finding: Object-Meta Mismatch

In 104 out of 250 underdetermined items (41.6%), the model's answer text explicitly acknowledges the problem -- then the structured boundary judgment contradicts it:

- **bwv2_006:** Table lists employees with Name, Department, and Salary. No email column exists. Question: "What is Alice's email?" The model answers: "The table doesn't contain email information." Stage 2: `determinate`, confidence 1.00.
- **bwv2_007:** A product table omits battery life data. Question asks about battery hours. The model answers: "battery hours not available in the table." Stage 2: `determinate`, confidence 1.00.

The model's answer-stage output acknowledges the issue, but the boundary-stage structured output does not reflect this. This inconsistency may be amplified by the structured output format, which forces a binary decision without intermediate reasoning tokens. Regardless of mechanism, this pattern would not surface in benchmarks evaluating only answer correctness.

### Overall Results (500 items, Gemini 2.5 Flash)

| Metric | Value |
|--------|-------|
| Answer accuracy (determinate items) | 0.980 |
| Boundary accuracy (all items) | 0.792 |
| False certainty rate (underdetermined items) | 0.416 |
| Missed certainty rate (determinate items) | 0.000 |

The near-zero missed certainty rate reveals an asymmetry: models default to certainty, not caution. They almost never wrongly abstain on answerable questions -- but frequently overcommit on unanswerable ones.

### Leaderboard (500 items)

| Model | Type | Overall | Answer acc | Boundary acc | FC rate |
|-------|------|---------|-----------|-------------|---------|
| Qwen 3 235B | Open | 0.836 | 0.904 | 0.874 | 0.228 |
| Claude Sonnet 4.6 | Proprietary | 0.828 | 0.768 | **0.944** | **0.112** |
| Claude Sonnet 4 | Proprietary | 0.792 | 0.952 | 0.810 | 0.356 |
| Gemini 2.5 Flash | Proprietary | 0.782 | 0.980 | 0.792 | 0.416 |

Claude Sonnet 4.6 shows a striking trade-off: the lowest answer accuracy (0.768) but the highest boundary accuracy (0.944) and lowest false certainty rate (0.112). This suggests that improved metacognitive awareness may come at the cost of answer-stage confidence -- the model that is most cautious about claiming certainty also hedges more on forced answers. Conversely, Gemini 2.5 Flash achieves near-perfect answer accuracy (0.980) but the highest false certainty (0.416).

### False Certainty by Failure Family

False certainty is not uniformly distributed -- it follows a steep hierarchy:

| Failure family | n | FC rate | 95% CI |
|----------------|---|---------|--------|
| no_satisfying_row | 50 | **0.960** | [0.86, 0.99] |
| missing_value | 50 | **0.700** | [0.56, 0.81] |
| tie | 49 | 0.184 | [0.09, 0.31] |
| incomplete_agg | 50 | 0.160 | [0.08, 0.28] |
| criterion_underspecification | 48 | 0.062 | [0.02, 0.16] |

On Gemini 2.5 Flash, when the table lacks the needed information entirely, the model commits to `determinate` 96% of the time. When a required cell is blank, the rate is 70%. Structural ambiguities (ties, underspecified criteria) are detected more reliably.

This hierarchy suggests that false certainty in this benchmark is primarily a failure of **absence detection** rather than ambiguity detection. Models can recognize when two candidates tie for first place, but they struggle to recognize when the evidence needed to answer is not present.

### Cross-Model False Certainty by Failure Family

| Failure family | Flash | Sonnet 4 | Sonnet 4.6 | Qwen 3 |
|----------------|-------|----------|------------|--------|
| no_satisfying_row | **0.960** | **0.580** | 0.060 | 0.080 |
| missing_value | **0.700** | **0.460** | **0.360** | **0.360** |
| tie | 0.184 | **0.694** | 0.122 | 0.184 |
| incomplete_agg | 0.160 | 0.040 | 0.000 | 0.260 |
| criterion_underspec | 0.062 | 0.021 | 0.000 | 0.208 |

The hierarchy is **not identical across models** -- this is the key discriminatory finding. All four models struggle with `missing_value` (0.36-0.70), but they diverge sharply on other families. Sonnet 4 has the highest `tie` false certainty (0.694) while Sonnet 4.6 nearly eliminates it (0.122). Flash shows extreme `no_satisfying_row` failure (0.960) while Sonnet 4.6 and Qwen 3 largely solve it. These model-specific failure profiles provide targeted diagnostic signal beyond aggregate accuracy.

### Confidence and Robustness

Boundary confidence was uniformly high (~0.993) across both correct and false-certainty cases -- a null result for confidence-based filtering. The false certainty signal was tested across three prompt formulations (original, rephrased, compact). Rates were stable (std=0.000 on each model tested), suggesting the signal is item-determined rather than prompt-determined, though further testing across models would strengthen this claim.

### Limitations

The tables are intentionally small (3-5 rows) to isolate boundary judgment; results may not transfer to larger, noisier data. The `no_satisfying_row` and `missing_value` families have surface-level cues (absent columns, empty cells) exploitable by heuristics. The two-stage design means the model sees its own prior answer, potentially creating anchoring effects. No human baseline is included. The `ordering_ambiguity` family (3 items) is exploratory and should be expanded.

### Conclusion

In our sample, frontier models consistently overcommit on whether an answer is uniquely justified, even when their own reasoning identifies the problem. The failure-family hierarchy -- from 96% false certainty on absent information to 6% on underspecified criteria -- provides diagnostic signal that aggregate accuracy cannot capture.

For model developers, the steepest improvement opportunity is in absence detection: teaching models to recognize when the information category required to answer a question is entirely absent from the provided context. For developers building RAG systems, agents, or pipelines where a model must say "I don't have enough information," this is the exact failure mode that causes silent overcommitment.

We invite the community to test additional models and report results.

## Organizational Affiliations

No organizational affiliation.

## References & Citations

- DeepMind (2025). Measuring progress toward AGI: A cognitive framework.
- Kaggle Benchmarks SDK documentation and examples.
- Kadavath, S., et al. (2022). Language models (mostly) know what they know. arXiv:2207.05221.
- Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring how models mimic human falsehoods. ACL.
- Yin, Z., et al. (2023). Do large language models know what they don't know? ACL Findings.
- Geifman, Y. & El-Yaniv, R. (2017). Selective classification for deep neural networks. NeurIPS.
