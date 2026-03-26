# Submission Checklist

## Benchmark

- [ ] Kaggle notebook의 최종 task가 `boundarybench_table_world_item_v2_50`로 선택되어 있는가
- [ ] benchmark/task가 정상 저장되는가
- [ ] benchmark 링크를 writeup에 attachment로 추가했는가

## Writeup

- [ ] track이 `Metacognition`으로 설정되었는가
- [ ] 제목과 부제가 정리되었는가
- [ ] 1,500 words 이하인가
- [ ] 핵심 결과 수치가 최신 값과 일치하는가
- [ ] 대표 failure case 3~5개를 넣었는가
- [ ] organizational affiliation이 없으면 명시했는가

## Evidence

- [ ] Gemini 50문항 결과 반영
- [ ] Claude 50문항 결과 반영
- [ ] GPT-4o는 먼저 `availability_probe`로 runtime 가용성을 확인했는가
- [ ] 붙는 경우에만 `smoke_1 -> smoke_5 -> backoff_manual` 순서로 재시도했는가
- [ ] GPT-4o가 계속 실패하면 503 availability limitation을 투명하게 적었는가

## Positioning

- [ ] 이 benchmark가 단순 QA accuracy가 아니라 metacognitive boundary signal을 본다고 설명했는가
- [ ] `false_certainty_rate`가 핵심 지표임을 명확히 적었는가
- [ ] determinate vs underdetermined distinction이 분명한가

## Final

- [ ] cover image 준비
- [ ] benchmark 링크 최종 확인
- [ ] writeup submit 직전 오탈자 검토
