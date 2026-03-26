# Project Memory

## Current State

- 대회 참가 및 Kaggle Benchmarks getting started notebook 실행 완료.
- 방향성은 `Metacognition / knowing when not to answer`로 고정.
- 전략 문서 `PRIZE_STRATEGY.md` 작성 완료.
- 상세 명세 `BOUNDARY_BENCH_SPEC.md` 작성 완료.
- 파일럿 데이터 `data/table_world_pilot.jsonl`에 10문항 작성 완료.
- 코어 prompt/scoring helper `src/table_world_core.py` 작성 완료.
- Kaggle SDK task wrapper `src/boundarybench_task.py` 작성 완료.
- Kaggle 실행 절차 `KAGGLE_RUNBOOK.md` 작성 완료.
- `kaggle-benchmarks-getting-started-notebook.ipynb`의 빈 셀 11, 12에 `BoundaryBench` 파일럿 코드 삽입 완료.
- v0, v1은 Gemini 2.5 Flash에서 전 문항 만점으로 변별력이 부족하다는 점 확인.
- 현재 핵심 리스크는 `benchmark`보다 `prompt compliance test`처럼 보일 수 있다는 점.
- 따라서 최적화 목표를 "모델 점수 향상"이 아니라 "모델 간 안정적인 행동 차이 포착"으로 유지해야 함.
- v2 two-stage design에서 Gemini 2.5 Flash 결과:
  - Overall accuracy `0.833`
  - Answer accuracy `1.000`
  - Boundary accuracy `0.833`
  - False certainty rate `0.333`
  - Missed certainty rate `0.000`
- 해석: 답은 맞출 수 있지만, underdetermined/trap 문항의 절반에서 `determinate`라고 잘못 확신함.
- 더 구체적으로는, 일부 사례에서 answer text는 정보 부족을 인정하면서도 boundary decision은 `determinate`라 답함.
- 이 불일치는 writeup의 핵심 메시지 후보임.
- Claude Sonnet 4 결과:
  - Overall accuracy `0.750`
  - Answer accuracy `1.000`
  - Boundary accuracy `0.750`
  - False certainty rate `0.500`
  - Missed certainty rate `0.000`
- GPT-4o는 Kaggle runtime에서 `503 model unavailable`, 추후 재시도 필요.
- 결론: 현재 v2는 최소 두 frontier 모델 사이에서 metacognitive boundary signal 차이를 보여준다.
- Gemini 24문항 확장판 결과:
  - Overall accuracy `0.833`
  - Answer accuracy `0.917`
  - Boundary accuracy `0.875`
  - False certainty rate `0.250`
  - Missed certainty rate `0.000`
- 해석: 표본을 늘린 뒤에도 signal이 유지된다. 다만 determinate 문제 일부에서 answer miss가 발생했으므로, 어떤 answerable 문항에서 틀렸는지 확인이 필요하다.
- `bwv2_019`은 `"Meeting B"` 허용 누락으로 생긴 채점 artifact였고, acceptable answer를 넓혀 수정했다.
- Gemini 50문항 확장판 결과:
  - Overall accuracy `0.840`
  - Answer accuracy `1.000`
  - Boundary accuracy `0.840`
  - False certainty rate `0.333`
  - Missed certainty rate `0.000`
- 해석: 50문항에서도 false certainty signal이 유지되므로, 현재 benchmark 축은 유지 가치가 높다.
- Claude 50문항 확장판 결과:
  - Overall accuracy `0.760`
  - Answer accuracy `0.962`
  - Boundary accuracy `0.780`
  - False certainty rate `0.458`
  - Missed certainty rate `0.000`
- 해석: 50문항에서도 Gemini가 Claude보다 underdetermination detection에서 더 강한 신호를 보인다.
- GPT-4o 50문항 manual retry 결과:
  - successful rows `0 / 50`
  - 모든 문항에서 `503 model unavailable`
- 해석: GPT-4o 부재는 benchmark 문제라기보다 Kaggle runtime availability 문제로 봐야 한다.

## Files Touched

- `AGENTS.md`
- `MEMORY.md`
- `PRIZE_STRATEGY.md`
- `BOUNDARY_BENCH_SPEC.md`
- `data/table_world_pilot.jsonl`
- `src/table_world_core.py`
- `src/boundarybench_task.py`
- `KAGGLE_RUNBOOK.md`
- `kaggle-benchmarks-getting-started-notebook.ipynb`

## Verification Done

- `python3 -c`로 JSONL 10문항 파싱 확인
- `python3 -c`로 `score_item`의 answerable / abstain 샘플 동작 확인
- `python3 -m py_compile`로 `src/table_world_core.py`, `src/boundarybench_task.py` 문법 확인
- `python3 -c`로 `summarize_item_results` 집계 동작 확인
- `python3 -c`로 `ipynb` 셀 11, 12 코드 삽입 여부 확인
- 결과 집계 시 중복 컬럼 충돌로 난 `Cannot index with multidimensional key` 오류를 prefix 방식으로 수정 완료

## Next Step

- pilot 10문항으로 GPT-4o, Gemini, Claude를 돌려 `overclaim_rate` 차이를 확인한다.
- trap 문항이 약하면 더 날카롭게 다시 쓴다.
- Kaggle notebook에서 `KAGGLE_RUNBOOK.md` 순서대로 첫 실행 결과를 얻는다.
- 노트북에서 셀 11, 12를 실행하고 `%choose boundarybench_table_world_score`가 적용됐는지 확인한다.
- v2 실행 후에도 만점이면 `relative confidence ranking` 같은 metacognition pivot을 검토한다.
- 현재 다음 우선순위는 false certainty가 난 구체적 문항 ID를 확인하고, 그 패턴이 tie/ordering ambiguity/missingness 중 어디에 몰리는지 분석하는 것.
- 노트북 후속 분석용 파일 `kaggle_boundarybench_v2_followup_cells.py` 작성 완료.
- 다음 단계 안내 문서 `ANALYSIS_NEXT_STEPS.md` 작성 완료.
- 다중 모델 비교용 셀 `kaggle_boundarybench_v2_multimodel_cell.py` 작성 완료.
- 현재 findings 요약 문서 `FINDINGS_V2.md` 작성 완료.
- 안전한 모델별 순차 실행 파일 `kaggle_boundarybench_v2_multimodel_safe.py`로 Gemini/Claude 결과 확보 완료.
- 24문항 확장판 데이터 `data/table_world_v2_24.jsonl` 작성 완료.
- Kaggle 복붙용 self-contained 확장판 `kaggle_boundarybench_v2_24_single_cell.py` 작성 완료.
- 24문항 후속 분석 셀 `kaggle_boundarybench_v2_24_followup_cells.py` 작성 완료.
- 50문항 확장판 `kaggle_boundarybench_v2_50_single_cell.py` 작성 완료.
- 제출 자산 정리 폴더 `boundarybench_project/` 생성 완료.
- 이 폴더에 docs/data/scripts/notebooks/src 기준으로 관련 파일 복사 완료.
- `boundarybench_project/submission/` 폴더 생성 완료.
- 최종 제출 기준 파일만 `submission/`에 재정리 완료:
  - final writeup
  - results summary
  - submission checklist
  - v2_50 main script
  - Claude/GPT-4o manual scripts
  - 50-item JSONL dataset

## Notes

- 혼자 참가하므로 scope를 늘리지 않는다.
- writeup 핵심 메시지는 "정답률이 아니라 epistemic boundary awareness를 본다"로 유지한다.
