# Results Summary

## Final Experimental Snapshot

### Gemini 2.5 Flash

- Items: `50`
- Overall accuracy: `0.840`
- Answer accuracy: `1.000`
- Boundary accuracy: `0.840`
- False certainty rate: `0.333`
- Missed certainty rate: `0.000`

### Claude Sonnet 4

- Items: `50`
- Overall accuracy: `0.760`
- Answer accuracy: `0.962`
- Boundary accuracy: `0.780`
- False certainty rate: `0.458`
- Missed certainty rate: `0.000`

### GPT-4o

- Not evaluated successfully
- Kaggle runtime returned `503 model unavailable` on all attempts
- Availability probe also failed early:
  - successful probe rows: `0 / 5`
  - consecutive 503 threshold hit: `True`

## Key Interpretation

- 두 모델 모두 determinate 문제는 강하다.
- 차이는 `boundary_accuracy`와 `false_certainty_rate`에서 더 분명하다.
- 즉 raw answer generation보다 `answerability self-evaluation`에서 더 큰 모델 차이가 나타난다.

## Main Claim

BoundaryBench suggests that frontier models can solve determinate structured problems while still overcommitting on whether the available evidence uniquely supports an answer.

## Best Failure Modes To Highlight

- missing value인데도 `determinate`
- no satisfying row인데도 `determinate`
- tie / non-unique optimum인데도 `determinate`
- answer text는 ambiguity를 인정하지만, structured boundary decision은 `determinate`
