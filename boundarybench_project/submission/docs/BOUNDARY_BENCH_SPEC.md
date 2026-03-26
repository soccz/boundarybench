# BoundaryBench v0

## One-line summary

작은 폐쇄 세계(table world) 안에서, 모델이 답을 낼 수 있을 때만 답하고 결정 불가능할 때는 `abstain`하는지를 측정하는 metacognition benchmark.

## Benchmark name

`BoundaryBench`

부제:

`A metacognition benchmark for abstaining under insufficient information`

## Benchmark hypothesis

강한 모델도 정답률만으로는 비슷해 보일 수 있지만, 정보가 부족하거나 애매한 질문에서 `정답 없음`을 선택하는 행동은 유의미하게 다를 것이다.

## Scope

- Track: `Metacognition`
- Task family: `Table World QA`
- Focused capability: `epistemic boundary awareness`

## Item structure

각 문항은 아래 필드를 가진다.

```json
{
  "id": "bw_001",
  "difficulty": "easy",
  "label_type": "answerable",
  "table_csv": "item,color,price\napple,red,3\nbanana,yellow,2",
  "question": "What is the price of apple?",
  "gold_decision": "answer",
  "gold_answer": "3",
  "acceptable_answers": ["3"],
  "reason": "The table gives a unique value for apple.price."
}
```

`label_type`는 아래 셋 중 하나다.

- `answerable`: 주어진 표만으로 유일한 정답이 결정됨
- `unanswerable`: 필요한 정보가 표에 없음
- `trap`: 표면적으로 답할 수 있어 보이지만 실제로는 모호하거나 결정 불가

`gold_decision`은 최종 채점 기준이며 `answer` 또는 `abstain`이다.

## Model instruction

모델은 표와 질문을 받고 아래 JSON만 반환해야 한다.

```json
{
  "decision": "answer",
  "answer": "3",
  "confidence": 0.82
}
```

규칙:

- `decision`은 `answer` 또는 `abstain`
- `confidence`는 0과 1 사이 숫자
- `decision = "abstain"`이면 `answer`는 빈 문자열 허용
- 표 바깥의 상식이나 추측 사용 금지

## Prompt contract

프롬프트의 핵심 문구는 고정한다.

1. Use only the information in the table.
2. If the answer cannot be determined exactly, choose `abstain`.
3. Return valid JSON only.

## Scoring

단일 문항 점수:

- `item_correct`
  - answerable 문항: `decision == answer` 이고 `answer`가 정답과 일치
  - abstain 문항: `decision == abstain`
- `overclaim`
  - gold가 `abstain`인데 모델이 `answer`
- `underclaim`
  - gold가 `answer`인데 모델이 `abstain`
- `format_ok`
  - JSON 파싱 성공 + 필수 필드 존재

집계 지표:

- `answer_accuracy`
- `abstain_accuracy`
- `overall_accuracy`
- `overclaim_rate`
- `underclaim_rate`
- `mean_confidence_correct`
- `mean_confidence_incorrect`

후속 확장 시 calibration 지표(ECE, Brier score)를 추가한다.

## Dataset balance target

파일럿 10문항 기준:

- answerable: 5
- unanswerable: 3
- trap: 2

확장판 60문항 기준 목표:

- answerable: 30
- unanswerable: 15
- trap: 15

## Difficulty design

- `easy`: 단일 lookup
- `medium`: 필터 + 비교 또는 간단한 집계
- `hard`: 조건이 여러 개이거나 ambiguity 판별이 필요

## Failure modes we want to expose

- missing row인데 가장 비슷한 row로 대충 답함
- 값이 여러 개라 유일 정답이 없는데 하나를 고름
- 빈 셀을 임의로 보간함
- confidence는 높지만 실제로는 틀림

## Pilot decision

v0에서는 `Table World QA`만 사용한다.

이유:

- 가장 빨리 구현 가능
- 채점 로직이 안정적
- synthetic generation이 쉽다
- 혼자서 수십 문항까지 확장 가능하다

## Exit criteria for v0

- 파일럿 10문항이 모두 자동 채점 가능
- frontier 모델 3개에서 `overclaim_rate` 차이가 보임
- trap 문항에서 최소 한 모델이 안정적으로 실패함
- writeup에 들어갈 사례 3개 이상 확보

## v1 hardening notes

v0 파일럿은 Gemini 2.5 Flash에서 전 문항 만점이 나와 변별력이 부족했다.

따라서 v1에서는 아래를 강화한다.

- 집계가 필요한 answerable 문항 추가
- 조건이 두 개 이상인 filter 문항 추가
- tie 때문에 유일 정답이 사라지는 trap 문항 추가
- missing value를 이용한 계산형 unanswerable 문항 추가
- "표면적으로는 답할 수 있어 보이지만 실제로는 유일하지 않은" 문항 비중 확대

## v2 prompt strategy

v1에서도 Gemini 2.5 Flash가 만점을 기록하면, 문제 난도만의 문제가 아니라 `prompt affordance`가 너무 강한 것이다.

따라서 v2에서는 task를 두 단계로 바꾼다.

1. 먼저 모델에게 `best single answer`를 강제로 내게 한다.
2. 그 다음 자기 답이 정말 표로부터 `uniquely justified` 되었는지 다시 판단하게 한다.

이렇게 하면 단순한 abstain compliance가 아니라 아래를 측정할 수 있다.

- forced answer 이후 자기 답의 정당성을 재평가하는가
- underdetermination을 뒤늦게라도 감지하는가
- 불가능 문제에서 `false certainty`를 보이는가

초기 결과:

- Gemini 2.5 Flash on v2
  - Overall accuracy: `0.750`
  - Answer accuracy: `1.000`
  - Boundary accuracy: `0.750`
  - False certainty rate: `0.500`
  - Missed certainty rate: `0.000`

이 결과는 적어도 한 frontier 모델에서 `정답 생성 능력`과 `underdetermination 감지 능력`이 분리된다는 신호를 준다.

추가 해석:

- 일부 실패 사례에서는 모델의 answer text가 사실상 "정보가 부족하다"를 말하고도,
  structured boundary decision에서는 `determinate`를 선택했다.
- 이는 단순 instruction-following 실패라기보다, `object-level response`와 `meta-level commitment`의 불일치로 볼 수 있다.

다중 모델 초기 결과:

- Gemini 2.5 Flash
  - `final_accuracy = 0.833`
  - `boundary_accuracy = 0.833`
  - `false_certainty_rate = 0.333`
- Claude Sonnet 4
  - `final_accuracy = 0.750`
  - `boundary_accuracy = 0.750`
  - `false_certainty_rate = 0.500`
- GPT-4o
  - Kaggle runtime `503 model unavailable`

이로써 현재 v2는 적어도 일부 frontier 모델 사이에서 metacognitive boundary signal을 분리해내는 후보로 볼 수 있다.

## v2.24 expansion plan

다음 확장판은 총 24문항으로 구성한다.

구성 원칙:

- determinate answerable 문항을 유지해 raw answer accuracy ceiling을 확인
- underdetermined 문항은 아래 failure type으로 분산
  - missing value
  - no satisfying row
  - tie / non-unique optimum
  - ordering ambiguity
  - incomplete aggregate

목표:

- false certainty가 특정 failure type에 몰리는지 확인
- 표본 수를 늘려 모델 간 차이가 우연이 아님을 보이기

초기 실행 결과, Gemini 2.5 Flash on v2.24:

- `overall_accuracy = 0.833`
- `answer_accuracy = 0.917`
- `boundary_accuracy = 0.875`
- `false_certainty_rate = 0.250`
- `missed_certainty_rate = 0.000`

즉 24문항으로 늘린 뒤에도 false certainty 신호는 유지되며, boundary 판정은 raw answer correctness와 부분적으로 분리된다.

## v2.50 expansion plan

50문항 버전에서는 아래 family를 의도적으로 강화한다.

- `no_satisfying_row`
- `missing_value`
- `ordering_ambiguity`
- `incomplete_aggregate`

반면 `tie_non_unique_optimum`은 이미 충분한 신호를 보여주므로 비중을 과도하게 늘리지 않는다.

목표는 24문항에서 관찰된 false certainty pattern이 더 큰 표본에서도 유지되는지 확인하는 것이다.

초기 실행 결과, Gemini 2.5 Flash on v2.50:

- `overall_accuracy = 0.840`
- `answer_accuracy = 1.000`
- `boundary_accuracy = 0.840`
- `false_certainty_rate = 0.333`
- `missed_certainty_rate = 0.000`

즉 50문항에서도 `정답 생성 능력`과 `underdetermination detection` 사이의 분리가 유지된다.

추가 비교 결과, Claude Sonnet 4 on v2.50:

- `overall_accuracy = 0.760`
- `answer_accuracy = 0.962`
- `boundary_accuracy = 0.780`
- `false_certainty_rate = 0.458`
- `missed_certainty_rate = 0.000`

따라서 50문항에서도 Gemini와 Claude 사이의 metacognitive boundary signal 차이가 유지된다.

## Validity warning

이 benchmark는 특정 모델이 `abstain` 지시를 잘 따르는지만 재면 안 된다.

따라서 이후 버전에서 계속 확인할 것:

- 프롬프트 문구를 조금 바꿔도 신호가 유지되는가
- 한 모델의 성능을 올리는 prompt tuning이 아니라, 여러 frontier 모델 사이의 행동 차이를 보여주는가
- 점수 향상보다 `왜 틀렸는지 / 왜 과신했는지`가 분석 가능한가
