# Kaggle Discussion Post (복붙용)

**Title: Your model says "the data doesn't have this" -- then claims it's 100% certain. Here's proof.**

---

I built a benchmark called **BoundaryBench** for the Metacognition track that reveals a surprisingly consistent failure pattern in frontier LLMs.

**The setup is simple:**

Give a model a small table and a question. Sometimes the table has enough information to answer (determinate). Sometimes it doesn't -- a cell is missing, the needed column doesn't exist, or two rows tie for the answer (underdetermined).

The model goes through two stages:
1. **Give your best answer** (forced -- no "I don't know" allowed)
2. **Now judge:** was your answer uniquely supported by the table, or not?

**The headline result:**

When the table genuinely lacks the information needed to answer, Gemini 2.5 Flash says "this answer is uniquely justified" **96% of the time**. Across 4 models (Qwen 3 235B, Claude Sonnet 4.6, Claude Sonnet 4, and Gemini 2.5 Flash), every single one shows significant false certainty -- but the *pattern* of failure varies dramatically by failure type.

**The most striking finding:**

In 41.6% of underdetermined cases, the model's own answer text explicitly acknowledges the problem ("battery hours not available in the table") -- and then the structured boundary judgment contradicts it ("determinate, confidence 1.00"). The model identifies the problem in text, then ignores it in judgment.

**Why this matters beyond benchmarks:**

If you're building RAG systems, agents, or any pipeline where a model needs to say "I don't have enough information" -- this is the exact failure mode that causes silent overcommitment. The model can reason about absence but fails to act on that reasoning at the meta-level.

The benchmark uses 500 synthetic table-QA items across 6 failure families, with two-stage prompting to separate answer generation from metacognitive boundary judgment. Prompt robustness was validated across 3 prompt variants.

**False certainty rate by failure type:**

| Failure family | FC rate |
|---|---|
| no_satisfying_row (absent info) | 0.960 |
| missing_value (blank cell) | 0.700 |
| tie | 0.184 |
| incomplete_agg | 0.160 |
| criterion_underspecification | 0.062 |

The gradient from 96% to 6% tells you exactly where models fail -- and it's absence detection, not ambiguity detection, that breaks them.

I'd love feedback from the community -- especially if you run it on models I haven't tested yet.

**Benchmark link:** [BoundaryBench on Kaggle Benchmarks](https://www.kaggle.com/benchmarks/s0occz/boundarybench)
