BoundaryBench: Models know they don't know, but report certainty anyway

I built a benchmark that tests something most QA evaluations miss: can a model tell when a question is unanswerable from the given evidence?

## The Problem

Frontier models score well on table-based QA, but that only tests one direction. BoundaryBench tests both:
- Can the model answer when the answer exists?
- Can the model recognize when no unique answer is possible?

## How It Works

Two-stage design:
1. Force the model to give its best answer
2. Ask it to judge: was that answer uniquely justified?

This avoids collapsing into simple instruction-following. The model must self-evaluate.

## Key Results (500 items, 5 models)

| Model | Overall |
|-------|---------|
| Qwen 3 235B | 0.85 |
| Claude Sonnet 4.6 | 0.83 |
| Claude Sonnet 4 | 0.81 |
| Gemini 2.5 Flash | 0.79 |
| Gemini 2.5 Pro | 0.65 |

## The Most Interesting Finding

False certainty follows a steep hierarchy across failure types:
- **No satisfying row: 94%** — models almost never detect absent information
- **Missing value: 70%** — blank cells are usually ignored
- **Tie: 12%** — models recognize tied values well
- **Ordering ambiguity: 12%** — multi-criteria ambiguity is well detected

Models handle ambiguity well but fail catastrophically at absence detection.

## Object-Meta Mismatch

In 41.6% of underdetermined items, the model's answer text explicitly says "data not available" or "cannot be determined" — then the boundary judgment says "determinate" with confidence 1.00.

The model knows it doesn't know, but reports certainty anyway.

## Prompt Robustness

Tested 3 prompt variants. False certainty rate identical across all three (std = 0.000).

## Try It

Benchmark: https://www.kaggle.com/benchmarks/s0occz/boundarybench

Feedback and upvotes welcome!
