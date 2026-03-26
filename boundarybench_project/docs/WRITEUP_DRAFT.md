# BoundaryBench: Detecting False Certainty About Answerability

## Your Team

Solo submission.

## Problem Statement

Many frontier models can produce correct answers on structured problems, but this does not guarantee that they correctly understand when an answer is uniquely justified by the available evidence. Existing benchmarks often conflate answer generation with metacognitive awareness. In particular, they do not cleanly separate:

- solving a determinate problem, and
- recognizing that a problem is underdetermined.

BoundaryBench targets this gap. The benchmark asks a simple question: can a model tell whether a table supports one unique answer, or whether the information is insufficient or non-unique?

The benchmark is designed for the `Metacognition` track. Its central claim is that frontier models may answer determinate questions well while still overcommitting on whether an answer is uniquely justified.

## Task & Benchmark Construction

BoundaryBench is a synthetic closed-world table benchmark. Each item contains:

- a small table,
- a question,
- a gold decision: `answer` or `abstain`,
- and an acceptable answer set for determinate items.

The final design uses a two-stage task:

1. The model is first forced to provide a best single answer.
2. The model is then asked whether that answer was `determinate` or `underdetermined`.

This design matters because it reduces simple abstain-compliance effects. Instead of only measuring whether the model follows an abstain instruction, it measures whether the model can evaluate the epistemic status of its own answer.

For determinate items, success requires:

- the answer content is correct, and
- the model marks the item as `determinate`.

For underdetermined items, success requires:

- the model marks the item as `underdetermined`.

The main metrics are:

- `answer_accuracy`
- `boundary_accuracy`
- `false_certainty_rate`
- `missed_certainty_rate`

`false_certainty_rate` is the key metric. It measures how often a model claims that an underdetermined item is determinate.

## Dataset

The dataset is synthetic and authored for this benchmark. This reduces contamination risk from memorized public QA sets and makes the gold labels defensible.

Current benchmark size:

- 50 items total
- 25 determinate items
- 25 underdetermined items

Underdetermined items are distributed across several failure families:

- missing values
- no satisfying row
- tie / non-unique optimum
- ordering ambiguity
- incomplete aggregate

This structure allows the benchmark to move beyond a single “abstain or not” signal and identify where false certainty arises.

## Technical Details

The benchmark is implemented with the `kaggle-benchmarks` SDK.

Each item is evaluated with structured JSON outputs in two stages:

- forced answer stage
- boundary judgment stage

The benchmark uses synthetic tables rather than open-domain facts, so the model must rely on the local evidence shown in the prompt. This helps isolate metacognitive boundary detection rather than background knowledge.

The scoring logic records both object-level and meta-level behavior. This makes it possible to detect a particularly important failure mode:

- the answer text itself implicitly acknowledges insufficient information,
- but the model still marks the item as `determinate`.

## Results, Insights, and Conclusions

On the 50-item benchmark:

### Gemini 2.5 Flash

- Overall accuracy: `0.840`
- Answer accuracy: `1.000`
- Boundary accuracy: `0.840`
- False certainty rate: `0.333`
- Missed certainty rate: `0.000`

### Claude Sonnet 4

- Overall accuracy: `0.760`
- Answer accuracy: `0.962`
- Boundary accuracy: `0.780`
- False certainty rate: `0.458`
- Missed certainty rate: `0.000`

The most important result is that both models perform strongly on determinate items, but differ more clearly on underdetermination detection. This suggests that raw answer generation and metacognitive boundary awareness are separable capabilities.

The benchmark also reveals a stronger qualitative pattern: some failures are not ordinary wrong answers. Instead, the model’s answer text may acknowledge ambiguity or missing information, while the structured boundary judgment still commits to `determinate`. This indicates a mismatch between object-level reasoning and meta-level commitment.

The main insight from BoundaryBench is therefore:

`Frontier models can answer determinate questions well while still overcommitting on whether an answer is uniquely justified.`

## Organizational Affiliations

No organizational affiliation.

## References & Citations

- DeepMind. *Measuring progress toward AGI: A cognitive framework.*
- Kaggle Benchmarks documentation and SDK examples.
