# Representative Failure Cases

이 문서는 writeup에 바로 넣을 수 있는 대표 실패 사례를 정리한 것이다.

원칙:

- 실제 관찰된 사례만 사용
- 과도한 해석은 피함
- 현재 제출 메시지와 직접 연결되는 케이스만 남김

## Recommended 3 Cases

### 1. Missing Value Treated as Determinate

- Item ID: `bwv2_007`
- Failure family: `missing_value`
- Question: `What is the battery-hours-per-dollar ratio for Pulse?`
- Observed forced answer:
  `The battery hours for Pulse are not provided in the table, so the battery-hours-per-dollar ratio cannot be determined.`
- Observed boundary decision: `determinate`

Why this matters:

- 모델은 object-level answer에서는 정보 부족을 인정했다.
- 그런데 meta-level boundary judgment에서는 여전히 `determinate`를 선택했다.
- 즉, 정보 부족을 말로는 인식하면서도 최종 확신은 철회하지 못했다.

### 2. No Satisfying Row Treated as Determinate

- Item ID: `bwv2_006`
- Failure family: `no_satisfying_row`
- Question: `Which animal weighs the most and is black?`
- Observed forced answer:
  `No animal in the table is black.`
- Observed boundary decision: `determinate`

Why this matters:

- 조건을 만족하는 행이 없으면 질문은 underdetermined가 아니라 effectively unanswerable이다.
- 그런데 모델은 답변 내용에서는 그 사실을 드러내면서도 boundary label은 `determinate`로 유지했다.
- 이건 단순 오답보다 더 중요한 metacognitive failure다.

### 3. Non-Unique Optimum Treated as Determinate

- Item ID: `bwv2_020`
- Failure family: `tie_non_unique_optimum`
- Question: `Which runner had the fastest lap overall?`
- Observed forced answer: `Ari and Bea`
- Observed boundary decision: `determinate`

Why this matters:

- 모델은 실제로 tie를 감지했다.
- 하지만 tie를 감지한 뒤에도 문제를 `underdetermined`로 분류하지 않았다.
- 즉, non-unique optimum을 인식하는 것과 answerability boundary를 올바르게 판단하는 것은 별개의 능력임을 보여준다.

## Ready-To-Paste Writeup Paragraph

BoundaryBench reveals a failure mode that standard QA benchmarks would miss. In one missing-value item (`bwv2_007`), the model explicitly stated that the required field was absent, yet still labeled the problem `determinate`. In a no-satisfying-row item (`bwv2_006`), it correctly noted that no row matched the query condition, but again failed to withdraw certainty. In a tie case (`bwv2_020`), it even surfaced both tied candidates while still treating the question as uniquely answerable. These cases show that object-level reasoning and meta-level judgment can diverge in frontier models.

## Usage Note

- writeup에는 위 3개 중 2~3개만 넣어도 충분하다.
- 표보다 짧은 사례 설명 문단으로 넣는 편이 더 깔끔하다.
- 현재 제출 메시지와 가장 잘 맞는 조합은 `bwv2_007 + bwv2_006 + bwv2_020`이다.
