# Project Instructions

## Language

- 사용자 응답은 한국어로 짧고 직접적으로 작성한다.

## Project Goal

- 이 저장소의 목적은 Kaggle `Measuring AGI - Cognition and Values` 해커톤 제출물 준비다.
- 혼자 참가 기준으로, 구현 난이도 대비 수상 가능성이 높은 benchmark 1개를 완성하는 것이 목표다.

## Chosen Direction

- 기본 트랙은 `Metacognition`
- 핵심 능력은 `knowing when not to answer`
- 첫 구현 대상은 `Table World QA + abstain under missing information`

## Scope Control

- 여러 트랙을 동시에 진행하지 않는다.
- 사람 손평가가 필요한 benchmark는 만들지 않는다.
- 라이선스가 불분명한 외부 데이터는 쓰지 않는다.
- 현실 상식형 문제보다 synthetic closed-world 문제를 우선한다.

## Working Files

- 전략 문서: `PRIZE_STRATEGY.md`
- 상세 명세: `BOUNDARY_BENCH_SPEC.md`
- 파일럿 데이터: `data/table_world_pilot.jsonl`
- 코어 로직: `src/table_world_core.py`

## Verification

- 문항 데이터는 JSONL 파싱이 반드시 성공해야 한다.
- scoring 로직은 answerable, abstain 케이스 둘 다 최소 샘플 검증 후 보고한다.
- Kaggle SDK 연결 후에는 frontier 모델 2~3개 파일럿 실행 결과를 남긴다.

## Decision Rule

- 방향성을 바꿔야 할 정도의 강한 근거가 없으면 현재 축을 유지한다.
- 새 아이디어가 생겨도 먼저 현재 benchmark의 discriminatory power를 확인한다.
