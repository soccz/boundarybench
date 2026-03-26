# Analysis Next Steps

## Current Signal

Gemini 2.5 Flash on v2:

- Overall accuracy: `0.833`
- Answer accuracy: `1.000`
- Boundary accuracy: `0.833`
- False certainty rate: `0.333`
- Missed certainty rate: `0.000`

Claude Sonnet 4 on v2:

- Overall accuracy: `0.750`
- Answer accuracy: `1.000`
- Boundary accuracy: `0.750`
- False certainty rate: `0.500`
- Missed certainty rate: `0.000`

Gemini 2.5 Flash on v2.24:

- Overall accuracy: `0.833`
- Answer accuracy: `0.917`
- Boundary accuracy: `0.875`
- False certainty rate: `0.250`
- Missed certainty rate: `0.000`

Gemini 2.5 Flash on v2.50:

- Overall accuracy: `0.840`
- Answer accuracy: `1.000`
- Boundary accuracy: `0.840`
- False certainty rate: `0.333`
- Missed certainty rate: `0.000`

Claude Sonnet 4 on v2.50:

- Overall accuracy: `0.760`
- Answer accuracy: `0.962`
- Boundary accuracy: `0.780`
- False certainty rate: `0.458`
- Missed certainty rate: `0.000`

현재 가장 중요한 해석은:

- determinate 문제는 맞춘다
- 그러나 underdetermined 문제의 일부를 `determinate`로 과신한다

## Immediate Analysis

노트북에서 아래 순서로 본다.

1. `label_type`별 성능 요약
2. `false certainty`가 난 문항 ID 확인
3. tie / ordering ambiguity / missing value 중 어디에서 많이 틀리는지 분류

복붙용 셀은 `kaggle_boundarybench_v2_followup_cells.py`에 있다.

## Multi-model Evaluation

공식 user guide 기준으로, 여러 모델 평가는 Task Detail Page의 `Evaluate More Models` 버튼으로 수행할 수 있다.

수동 코드 실험도 가능하되, 최종 대회 흐름은 GUI 기반 비교가 더 안전하다.

현재 상태:

- Gemini, Claude 결과 확보
- GPT-4o는 `503 model unavailable`로 재시도 필요
- Gemini 24문항 확장 결과 확보
- Gemini 50문항 확장 결과 확보
- Claude 50문항 확장 결과 확보

## Decision Rule

- 다른 frontier 모델에서도 `false certainty` 차이가 보이면 현재 방향 유지
- Gemini만 유독 약하고 다른 모델은 모두 비슷하면 문항 세트를 더 날카롭게 조정
- 프롬프트 문구가 조금만 바뀌어도 신호가 무너지면 metacognition validity를 다시 검토

현재는 첫 번째 조건을 만족했으므로, 당장은 현재 방향을 유지한다.

다음 우선순위:

1. 50문항 버전에서 Gemini/Claude false certainty 사례 비교
2. writeup 초안 작성
3. 가능하면 GPT-4o 재시도

복붙용 분석 셀:

- `kaggle_boundarybench_v2_24_followup_cells.py`
