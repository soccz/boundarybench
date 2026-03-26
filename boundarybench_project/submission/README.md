# BoundaryBench Submission Pack

## What This Folder Is

이 폴더는 Kaggle 제출 직전 기준의 `BoundaryBench` 최종 자산만 모아둔 폴더다.

핵심 원칙:

- 중간 실험 파일은 제외
- 최종 benchmark 실행 파일, 결과 요약, writeup 초안, 체크리스트만 포함

## Current Benchmark Status

Track:

- `Metacognition`

Core capability:

- `underdetermination detection`

Core message:

`Frontier models can answer determinate questions well while still overcommitting on whether an answer is uniquely justified.`

## Current Results

### Gemini 2.5 Flash on 50 items

- Overall accuracy: `0.840`
- Answer accuracy: `1.000`
- Boundary accuracy: `0.840`
- False certainty rate: `0.333`
- Missed certainty rate: `0.000`

### Claude Sonnet 4 on 50 items

- Overall accuracy: `0.760`
- Answer accuracy: `0.962`
- Boundary accuracy: `0.780`
- False certainty rate: `0.458`
- Missed certainty rate: `0.000`

### GPT-4o

- Kaggle runtime returned `503 model unavailable`
- excluded from current comparative interpretation

## Folder Guide

- `docs/FINAL_WRITEUP.md`
  - Kaggle writeup 제출 초안
- `docs/SUBMISSION_METADATA.md`
  - 제목, 부제, cover text, 핵심 포지셔닝 문구
- `docs/FAILURE_CASES.md`
  - 대표 실패 사례 3개와 writeup용 문단
- `docs/RESULTS_SUMMARY.md`
  - 최종 핵심 결과와 해석
- `docs/SUBMISSION_CHECKLIST.md`
  - 제출 직전 체크리스트
- `scripts/boundarybench_v2_50_single_cell.py`
  - Kaggle benchmark용 메인 실행 셀
- `scripts/boundarybench_v2_50_claude_manual.py`
  - Claude 50문항 수동 실행 셀
- `scripts/boundarybench_v2_50_gpt4o_manual.py`
  - GPT-4o 기존 50문항 수동 실행 셀
- `scripts/boundarybench_v2_50_gpt4o_smoke_1.py`
  - GPT-4o 1문항 스모크 테스트
- `scripts/boundarybench_v2_50_gpt4o_smoke_5.py`
  - GPT-4o 5문항 샘플 테스트
- `scripts/boundarybench_v2_50_gpt4o_availability_probe.py`
  - GPT-4o 가용성만 빠르게 확인하는 조기 중단 probe
- `scripts/boundarybench_v2_50_gpt4o_backoff_manual.py`
  - GPT-4o 50문항 백오프 재시도 셀
- `scripts/boundarybench_v2_50_gpt4o_backoff_standalone.py`
  - GPT-4o 단독 복붙용 50문항 백오프 실행 셀
- `data/table_world_v2_50.jsonl`
  - 50문항 데이터셋

## Recommended Next Action

1. GPT-4o는 먼저 `gpt4o_availability_probe`로 붙는지 확인
2. 붙으면 이미 `v2_50` 메인 셀을 돌린 경우 `smoke_1 -> smoke_5 -> backoff_manual`
3. 단독 복붙이 필요하면 `gpt4o_backoff_standalone`
4. Kaggle benchmark 최종 저장
5. writeup에 benchmark 링크 연결
6. 대표 실패 사례 3~5개 삽입
7. `docs/FINAL_WRITEUP.md` 내용을 Kaggle writeup에 반영
8. 제출 전 checklist 점검
