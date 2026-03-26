# Submission Metadata

## Recommended Title

BoundaryBench

## Recommended Subtitle

A Metacognitive Benchmark for Underdetermination Detection in Frontier Models

## Why This Positioning

- `Metacognition` 트랙 적합성이 바로 드러난다.
- 단순 abstention benchmark가 아니라 `underdetermination detection`이라는 더 구체적인 능력을 강조한다.
- frontier model 비교 실험과 바로 연결된다.
- 과장된 표현 없이도 연구형 제출물처럼 보인다.

## One-Line Hook

Frontier models can answer determinate questions well while still overcommitting on whether an answer is uniquely justified.

## Cover Image Text

BoundaryBench

Detecting False Certainty About Answerability

## Short Description

BoundaryBench is a closed-world metacognition benchmark that separates answer generation from answerability judgment. Models first produce a best answer, then decide whether the evidence uniquely justifies that answer. The core signal is false certainty on underdetermined items.

## Recommended Writeup Opening

Frontier models often look strong on structured tasks because they can produce plausible answers. BoundaryBench asks a narrower metacognitive question: can a model tell when the evidence supports one uniquely justified answer, and when it does not?

## Recommended Result Framing

- Gemini 2.5 Flash: stronger boundary detection, lower false certainty
- Claude Sonnet 4: weaker boundary detection, higher false certainty
- GPT-4o: unavailable in Kaggle runtime during evaluation, excluded transparently

## What To Emphasize

- This is not just a QA benchmark.
- The key metric is `false_certainty_rate`.
- The main contribution is separating answer generation from boundary judgment.
- The benchmark reveals a failure mode that raw accuracy hides.

## What Not To Emphasize

- prompt engineering tricks
- maximizing one model's score
- unavailable GPT-4o results
- broad AGI claims beyond the observed signal
