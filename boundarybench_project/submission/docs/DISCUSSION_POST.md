# BoundaryBench: Do Frontier Models Know When They Can't Answer?

I built a benchmark that tests something most QA evaluations miss: **can a model tell when a question is unanswerable from the given evidence?**

## The Problem

Frontier models score well on table-based QA, but that only tests one direction. BoundaryBench tests both:
- Can the model answer when the answer exists? (determinate)
- Can the model recognize when no unique answer is possible? (underdetermined)

## How It Works

Two-stage design:
1. Force the model to give its best answer
2. Ask it to judge: was that answer uniquely justified?

This avoids collapsing into simple instruction-following. The model must self-evaluate.

## Key Results (200 items, 4 models)

| Model | Overall | False Certainty Rate |
|-------|---------|---------------------|
| Claude Sonnet 4.6 | 0.88 | — |
| Claude Sonnet 4 | 0.85 | — |
| Gemini 2.5 Flash | 0.83 | 0.343 |
| Gemini 2.5 Pro | 0.68 | — |

## The Most Interesting Finding

In 32 out of 99 underdetermined items, the model's **answer text explicitly acknowledges the problem** ("data not available", "cannot be determined"), yet the **boundary judgment still says `determinate` with confidence 1.00**.

This object-level / meta-level mismatch is invisible to accuracy-only benchmarks.

## Prompt Robustness

Tested 3 prompt variants. False certainty rate = 0.343 across all three. Std = 0.000. The signal is completely stable.

## Try It

Benchmark link: https://www.kaggle.com/benchmarks/s0occz/boundarybench

Feedback and upvotes welcome!
