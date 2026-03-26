# BoundaryBench Project Bundle

## Purpose

이 폴더는 현재까지 만든 `BoundaryBench` 제출 자산을 한 곳에 모은 정리용 번들이다.

원본 파일은 상위 디렉터리에 그대로 두고, 이 폴더는 제출 준비와 writeup 작업을 쉽게 하기 위한 복제본 모음으로 사용한다.

## Current Status

현재 기준 핵심 결과:

- Gemini 2.5 Flash on 50 items
  - Overall accuracy: `0.840`
  - Answer accuracy: `1.000`
  - Boundary accuracy: `0.840`
  - False certainty rate: `0.333`
  - Missed certainty rate: `0.000`

- Claude Sonnet 4 on 50 items
  - Overall accuracy: `0.760`
  - Answer accuracy: `0.962`
  - Boundary accuracy: `0.780`
  - False certainty rate: `0.458`
  - Missed certainty rate: `0.000`

현재 메시지:

`Frontier models can answer determinate questions well while still overcommitting on whether an answer is uniquely justified.`

## Folder Layout

- `docs/`
  - 전략, 명세, findings, 다음 단계 문서
- `data/`
  - 파일럿/확장 데이터
- `scripts/`
  - Kaggle 복붙용 단일 셀 스크립트
- `notebooks/`
  - 참고용 Kaggle notebook 복사본
- `src/`
  - 로컬 helper / task wrapper 코드

## Recommended Starting Files

가장 먼저 볼 파일:

1. `submission/README.md`
2. `submission/docs/FINAL_WRITEUP.md`
3. `submission/docs/RESULTS_SUMMARY.md`
4. `submission/scripts/boundarybench_v2_50_single_cell.py`
5. `submission/scripts/boundarybench_v2_50_claude_manual.py`

## Next Priority

1. `GPT-4o` 50문항 재시도
2. writeup 초안 작성
3. 필요하면 80~100문항 확장
