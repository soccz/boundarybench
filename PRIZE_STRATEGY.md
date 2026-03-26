# Kaggle Measuring AGI Prize Strategy

## Goal

혼자 참가 기준으로, 구현 난이도 대비 수상 가능성이 가장 높은 방향으로 benchmark 1개를 완성한다.

우리는 큰 범위를 건드리지 않는다. 한 트랙, 한 능력, 작은 but defensible dataset, 자동 채점 가능한 task로 간다.

## Chosen Direction

- Track: `Metacognition`
- Primary capability: `knowing when not to answer`
- Core claim: 프론티어 모델은 정답률만 보면 비슷해 보여도, 정보가 부족한 상황에서 `모른다 / 답변 유보`를 선택하는 능력에서 큰 차이가 난다.

## Why This Direction

이 방향은 혼자 만들기 가장 유리하다.

- 채점이 명확하다: 정답이 있거나, 정보가 부족해 정답을 확정할 수 없거나 둘 중 하나다.
- 기존 지식 암기를 피하기 쉽다: synthetic closed-world task로 만들 수 있다.
- 모델 간 차이를 만들기 쉽다: 많은 모델이 불확실할 때도 억지로 답한다.
- writeup이 강해진다: "모델이 무엇을 아는가"보다 "모델이 무엇을 모른다는 걸 아는가"라는 메시지가 선명하다.
- 라이선스 리스크가 낮다: 직접 생성한 데이터 중심으로 가면 공개 및 CC0 대응이 쉽다.

## Benchmark Thesis

이 benchmark는 모델의 지식량이 아니라 `epistemic boundary awareness`를 측정한다.

정확히는 아래를 묻는다.

- 정보가 충분할 때는 정확히 답하는가
- 정보가 부족할 때는 추측하지 않고 `insufficient information`을 선택하는가
- 자신의 confidence가 실제 정답 가능성과 맞는가

## Benchmark Concept

작은 세계(closed world)를 제시하고 그 안에서만 답해야 하는 문제를 만든다.

예시 구조:

1. 짧은 사실 집합 제시
2. 질문 제시
3. 질문은 세 종류로 구성
   - answerable: 주어진 정보만으로 정답 가능
   - unanswerable: 정보 부족으로 정답 불가
   - trap: 표면적으로 그럴듯하지만 실제로는 확정 불가

모델은 아래 형식으로 답하게 만든다.

```json
{
  "decision": "answer" | "abstain",
  "answer": "...",
  "confidence": 0.00
}
```

## Dataset Design Principles

- 전부 우리가 직접 생성하거나, 공개 데이터에서 구조만 참고해 새로 만든다.
- 각 문항은 정답 근거를 코드로 재생성 가능해야 한다.
- 훈련 데이터 암기 영향이 적도록 현실 상식이 아니라 `로컬 규칙/테이블/미니월드` 기반으로 만든다.
- 문항마다 difficulty와 answerability를 명시한다.
- 너무 쉬운 문제와 너무 어려운 문제를 섞지 않고, 중간 난도를 충분히 확보한다.

## Proposed Task Families

우선 아래 셋 중 하나를 메인으로 삼고, 필요하면 두 개를 같은 benchmark로 묶는다.

### 1. Table World QA

작은 표를 주고 질문한다.

- answerable: 표에서 유일한 값이 결정됨
- unanswerable: 필요한 값이 빠져 있음
- trap: 비슷한 값이 있어 성급히 답하면 틀림

장점:

- 구현과 채점이 가장 쉽다
- 모델이 표면적 패턴에 끌려 추측하는지 보기 좋다

### 2. Rule World QA

짧은 규칙과 예시를 준 뒤 질문한다.

- answerable: 규칙 적용으로 정답 가능
- unanswerable: 필요한 전제가 없음
- trap: 규칙을 섣불리 일반화하면 틀림

장점:

- metacognition과 reasoning을 같이 보되, 측정 축은 여전히 "답변 유보"로 유지 가능

### 3. Multi-hop Fact World

인물, 일정, 물건, 장소 같은 관계형 사실을 준 뒤 질문한다.

- answerable: 2~3 hop 추론으로 정답 가능
- unanswerable: 연결 고리 하나가 빠져 있음
- trap: 흔한 추론 습관대로 가면 틀림

장점:

- frontier 모델 간 차이가 날 가능성이 높다
- writeup에서 failure mode 설명이 쉽다

## Recommended First Version

`Table World QA + abstain under missing information`

이유:

- 가장 빨리 파일럿을 만들 수 있다
- scoring이 단순하다
- 데이터 생성기를 만들기 쉽다
- 혼자서도 30~100문항까지 확장 가능하다

## Scoring

우리는 단순 accuracy 하나로 가지 않는다.

- Answer accuracy: answerable 문항에서 정답률
- Abstain accuracy: unanswerable 문항에서 abstain 비율
- Overclaim rate: unanswerable 문항에서 억지 답변한 비율
- Calibration: confidence와 실제 정답 여부의 정합성

최종 보고에서는 최소 아래를 제시한다.

- model별 accuracy
- model별 abstain quality
- model별 overclaim rate
- difficulty별 성능 변화

## What Would Make This Benchmark Valuable

좋은 benchmark의 기준은 아래다.

- GPT-4o, Gemini, Claude가 서로 비슷한 정답률을 보이더라도 abstain behavior에서 분명히 갈린다
- 단순 지식 부족이 아니라 `모르는 상황 인식 실패`를 드러낸다
- 기존 QA benchmark에서는 드러나지 않던 confabulation 패턴을 보여준다

중요:

- 특정 모델의 점수를 높이는 것이 목표가 아니다.
- 프롬프트를 세게 줘서 순응하게 만드는 것은 benchmark 품질을 높이지 않는다.
- 최종 제출물은 `instruction compliance`보다 `stable behavioral signal`을 보여줘야 한다.

## Scope Control

혼자 하므로 절대 하지 말 것:

- 여러 트랙 동시 공략
- 복잡한 UI나 시각화부터 만들기
- 사람 손평가가 필요한 benchmark
- 라이선스 불분명한 외부 데이터 사용
- 특정 모델 하나에 맞춘 프롬프트 튜닝 경쟁

현재까지의 경험적 판단:

- `v0`, `v1`은 너무 쉬워 benchmark 가치가 낮았다.
- `v2`의 two-stage design은 Gemini 2.5 Flash에서 `false certainty rate = 0.500`을 보여, 변별력 있는 방향일 가능성이 높다.
- 따라서 현재 우선순위는 모델 점수 최적화가 아니라, `어느 문항 유형에서 false certainty가 발생하는지`를 구조적으로 분석하는 것이다.

현재 strongest insight:

- frontier model은 determinate 문제를 잘 풀어도,
  underdetermined 문제에서 자기 답의 정당성을 과신할 수 있다.
- 특히 답변 내용과 메타판단이 서로 충돌하는 사례는 benchmark의 연구적 가치가 높다.

현재 empirical signal:

- Gemini 2.5 Flash: `boundary_accuracy 0.833`, `false_certainty_rate 0.333`
- Claude Sonnet 4: `boundary_accuracy 0.750`, `false_certainty_rate 0.500`
- Gemini 2.5 Flash on 24 items: `answer_accuracy 0.917`, `boundary_accuracy 0.875`, `false_certainty_rate 0.250`
- Gemini 2.5 Flash on 50 items: `answer_accuracy 1.000`, `boundary_accuracy 0.840`, `false_certainty_rate 0.333`
- Claude Sonnet 4 on 50 items: `answer_accuracy 0.962`, `boundary_accuracy 0.780`, `false_certainty_rate 0.458`

즉 적어도 두 frontier 모델 사이에서 메타인지 지표 차이가 관찰되었다.

표본을 24문항으로 늘린 뒤에도 signal이 유지되므로, 현재 설계는 우연한 소표본 결과일 가능성이 낮아졌다.
50문항에서도 같은 종류의 signal이 유지되므로, 현재 benchmark 방향은 유지 가치가 높다.

우리가 만들 것은 이것뿐이다.

- task 1~2개
- 문항 30개 파일럿
- 잘 되면 60~100개 확장
- benchmark 1개
- writeup 1개

## Immediate Plan

### Phase 1. Concept Lock

- benchmark 이름 임시 확정
- task family 하나 선택
- output schema 확정
- scoring 함수 정의

### Phase 2. Pilot Build

- 문항 10개 수작업 설계
- task 코드 작성
- frontier 모델 2~3개에 파일럿 실행
- 점수 차이와 이상 응답 확인

### Phase 3. Scale

- 생성 규칙 정제
- 문항 30개 이상으로 확장
- 난도 조정
- writeup용 예시 failure case 수집

### Phase 4. Submission

- benchmark 링크 정리
- writeup 작성
- benchmark 공개 후 커뮤니티 반응 확보

## Definition of Done

아래를 만족하면 제출 가능 상태다.

- answerable / unanswerable 구분이 명확하다
- 자동 채점만으로 점수 계산이 가능하다
- 최소 3개 모델에서 유의미한 성능 차이가 보인다
- writeup에서 "이 benchmark가 새롭게 보여주는 행동"을 한 문장으로 설명할 수 있다

## Next Decision

다음으로 바로 결정할 것은 하나다.

`Table World QA`, `Rule World QA`, `Multi-hop Fact World` 중 어느 task family로 파일럿을 시작할지 고른다.

현재 추천은 `Table World QA`다.
