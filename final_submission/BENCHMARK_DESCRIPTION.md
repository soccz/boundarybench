# Benchmark Page Description (Kaggle에 복붙)

**BoundaryBench** measures whether language models can distinguish questions that have one unique answer from questions that don't -- and whether they'll admit the difference.

Each item presents a small table and a question. Some questions are **determinate** (the table supports exactly one answer). Others are **underdetermined** (a value is missing, rows are tied, or needed information is absent). The model must first answer the question, then judge whether its answer was uniquely justified by the evidence.

Across 500 items and 4 tested models, frontier LLMs consistently show **false certainty** -- claiming an answer is uniquely supported even when the table lacks the needed information. The rate reaches 94% for absent-information cases. In over 40% of these failures, the model's own reasoning text correctly identifies the problem before the structured judgment overrides it.

BoundaryBench targets the **Metacognition** track by evaluating epistemic boundary awareness: not whether a model can answer, but whether it knows when an answer is uniquely justified. All items are synthetic, fully auditable, and organized into six failure families for diagnostic analysis.

Primary metric: false certainty rate on underdetermined items. Secondary metrics: answer accuracy, boundary accuracy, missed certainty rate.
