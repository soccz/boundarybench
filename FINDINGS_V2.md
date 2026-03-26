# BoundaryBench v2 Findings

## Gemini 2.5 Flash

- Overall accuracy: `0.833`
- Answer accuracy on determinate items: `1.000`
- Boundary accuracy: `0.833`
- False certainty rate: `0.333`
- Missed certainty rate: `0.000`

## Gemini 2.5 Flash on 24-item v2.24

- Overall accuracy: `0.833`
- Answer accuracy on determinate items: `0.917`
- Boundary accuracy: `0.875`
- False certainty rate: `0.250`
- Missed certainty rate: `0.000`

## Gemini 2.5 Flash on 50-item v2.50

- Overall accuracy: `0.840`
- Answer accuracy on determinate items: `1.000`
- Boundary accuracy: `0.840`
- False certainty rate: `0.333`
- Missed certainty rate: `0.000`

## Claude Sonnet 4

- Overall accuracy: `0.750`
- Answer accuracy on determinate items: `1.000`
- Boundary accuracy: `0.750`
- False certainty rate: `0.500`
- Missed certainty rate: `0.000`

## Claude Sonnet 4 on 50-item v2.50

- Overall accuracy: `0.760`
- Answer accuracy on determinate items: `0.962`
- Boundary accuracy: `0.780`
- False certainty rate: `0.458`
- Missed certainty rate: `0.000`

## GPT-4o

- Kaggle runtime returned `503 model unavailable`
- 결과 해석 불가, 추후 재시도 필요
- 50-item v2.50 manual retry also failed on all 50 items with the same `503 model unavailable` response

## Main Interpretation

이 모델은 determinate 문제를 푸는 능력은 강하다.

하지만 underdetermined 문제를 감지하는 능력은 약하다. 특히 일부 문항에서는 답변 내용 자체는 사실상 `답 불가`를 인정하면서도, 구조화된 metacognitive decision에서는 `determinate`를 선택했다.

즉, 현재 보이는 핵심 실패는 단순 오답이 아니라 아래의 불일치다.

- object-level answer: 정보 부족을 언급함
- meta-level boundary judgment: 그래도 `determinate`라고 확신함

이건 writeup에서 매우 좋은 포인트다. 단순 accuracy benchmark가 아니라, `answer generation`과 `self-evaluation of answerability`가 분리될 수 있음을 보여준다.

## Observed Failure Types

현재 false certainty가 난 사례:

- missing numeric field로 계산 불가인데 `determinate`
- ordering ambiguity인데 `determinate`
- 조건을 만족하는 행이 없는데도 `determinate`

현재까지의 비교 결과:

- Gemini 2.5 Flash가 Claude Sonnet 4보다 `boundary_accuracy`가 높고 `false_certainty_rate`가 낮다.
- 두 모델 모두 determinate 문제 정답률은 `1.000`으로 동일하다.
- 따라서 현재 signal은 raw QA accuracy가 아니라 `underdetermination detection`에서 나온다.
- 24문항으로 늘린 뒤에도 Gemini에서 false certainty 신호가 유지되었다.
- 다만 determinate answerable에서 일부 answer miss가 생겨, raw answer accuracy와 boundary accuracy가 완전히 같은 것은 아님이 확인되었다.
- 50문항에서도 Gemini가 Claude보다 높은 `boundary_accuracy`와 낮은 `false_certainty_rate`를 보였다.
- 50문항으로 늘린 뒤에는 answer accuracy가 다시 `1.000`으로 올라갔고, false certainty signal도 `0.333`으로 유지되었다.

채점 메모:

- `bwv2_019`의 answer miss는 실제 reasoning failure라기보다 `"Meeting B"`를 허용하지 않은 acceptable answer set 때문에 생긴 artifact였다.
- 이 문항은 허용 답안을 넓혀 수정했다.

## Why This Matters

이 benchmark는 모델이 정답을 아는지보다, `문제가 유일하게 결정 가능한지`를 아는지를 측정한다.

따라서 이후 다중 모델 비교에서 볼 핵심 지표는:

- `false_certainty_rate`
- `boundary_accuracy`
- failure type별 분포

현재 제출 기준으로는 Gemini와 Claude 비교만으로도 충분한 metacognitive contrast가 확보되었다.
