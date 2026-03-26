# Kaggle Runbook

## Goal

Kaggle Benchmarks notebook에서 `BoundaryBench` 파일럿 10문항을 실제 모델에 돌리고 요약표를 얻는다.

## Files to copy into the notebook

- `src/table_world_core.py`
- `src/boundarybench_task.py`

## Data to make available

- `data/table_world_pilot.jsonl`

가장 단순한 방법은 이 JSONL 파일을 Kaggle Dataset으로 하나 올리거나, notebook 셀에서 직접 파일로 저장하는 것이다.

## Minimal notebook flow

```python
import pandas as pd
import kaggle_benchmarks as kbench
```

```python
# 위 두 파일의 내용을 notebook 셀에 복사하거나, notebook 환경에서 import 가능하게 둔다.
from boundarybench_task import load_table_world_data, evaluate_table_world, summarize_runs
```

```python
dataset = load_table_world_data("/kaggle/input/YOUR_DATASET_NAME/table_world_pilot.jsonl")
dataset.head()
```

```python
runs = evaluate_table_world(
    llm=[kbench.llm],
    evaluation_data=dataset,
)
summary = summarize_runs(runs)
summary
```

## Multi-model run

여러 모델 비교는 notebook에서 현재 접근 가능한 모델 객체를 리스트로 넘기면 된다.

```python
runs = evaluate_table_world(
    llm=[
        kbench.llm,
        # 여기에 추가 모델 객체를 넣는다.
    ],
    evaluation_data=dataset,
)
summary = summarize_runs(runs)
summary
```

## What to inspect first

- `overall_accuracy`
- `abstain_accuracy`
- `overclaim_rate`

좋은 신호는 `overall_accuracy`보다 `overclaim_rate`에서 모델 차이가 먼저 드러나는 것이다.

## Immediate next edits if results are weak

- 너무 쉬우면 `trap` 문항을 늘린다
- 모두 abstain만 잘하면 answerable 난도를 올린다
- 모두 비슷하면 ambiguity 판별 문항을 더 추가한다
