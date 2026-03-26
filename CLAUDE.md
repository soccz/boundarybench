# BoundaryBench — 로컬 프로젝트 지침

## 대회 기본 정보

- 대회명: Kaggle `Measuring AGI - Cognition and Values` (hosted by Google LLC / DeepMind)
- 시작: 2026-03-17 / **마감: 2026-04-16 23:59 UTC** (약 27일 남음)
- 심사 기간: 2026-04-17 ~ 2026-05-31
- 투표 마감: 2026-05-22
- 결과 발표: 2026-06-01 (예정)
- 데이터셋: 없음 — 직접 제작 필수
- **제출은 1팀 1회만 허용** (draft 상태 미제출은 무효)
- **Winner License: CC0** — 수상 시 코드 전체 오픈소스 공개 의무
- Kaggle quota: 가입 시 $50/일, $500/월 자동 지급 (소진 시 kaggle-benchmarks-agi-hackathon@google.com 요청)

## 상금 구조

- Grand Prize 4개 × $25,000 (전체 트랙 통합)
- Track Prize: Metacognition $10,000 × 2 (1위, 2위)

## 필수 제출물 (빠지면 무효)

1. **Kaggle Writeup** — Track: `Metacognition` 선택 필수, 1,500 words 이하
2. **Kaggle Benchmark 링크** — Writeup의 Attachments > Project Links에 추가 (private → 마감 후 자동 공개)
3. **Cover image** — 없으면 Submit 버튼 비활성화

선택 제출물:
- Public Notebook (코드)
- Media Gallery (이미지/영상)

## 평가 배점

| 항목 | 비중 | 설명 |
|------|------|------|
| Dataset quality & task construction | **50%** | 정답 명확성, 표본 크기, 코드 품질, 입출력 검증 |
| Writeup quality | 20% | 문제 정의 → 구현 → 데이터 → 결과 → 인사이트 |
| Discriminatory power | **15%** | 모델 간 성능 차이가 뚜렷해야 함 (0%도 100%도 무의미) |
| Community upvotes | 15% | Benchmark 투표 수 (Writeup 투표 아님) |

## 프로젝트 방향

- **Track**: Metacognition
- **Benchmark 이름**: BoundaryBench
- **측정 능력**: epistemic boundary awareness — 모델이 문제가 유일하게 결정 가능한지 아는지
- **핵심 주장**: frontier model은 determinate 문제를 잘 풀어도, underdetermined 문제에서 false certainty를 보인다
- **설계**: two-stage (강제 답변 → boundary judgment) — 단순 instruction compliance가 아닌 self-evaluation 측정

## 현재 실험 결과 (최신 기준)

| 모델 | Overall | Answer acc | Boundary acc | False certainty |
|------|---------|------------|--------------|-----------------|
| Gemini 2.5 Flash (50문항) | 0.840 | 1.000 | 0.840 | **0.333** |
| Claude Sonnet 4 (50문항) | 0.760 | 0.962 | 0.780 | **0.458** |
| GPT-4o | — | — | — | 503 unavailable |

핵심 메시지: `Frontier models can answer determinate questions well while still overcommitting on whether an answer is uniquely justified.`

## 파일 구조

```
kaggle/
├── CLAUDE.md                          ← 이 파일
├── AGENTS.md                          ← 이전 로컬 지침 (참조용)
├── MEMORY.md                          ← 실험 이력
├── data/
│   ├── table_world_pilot.jsonl        ← 10문항 파일럿
│   ├── table_world_v2_24.jsonl        ← 24문항
│   └── (50문항은 single_cell 내장)
├── src/
│   ├── table_world_core.py            ← prompt/scoring 코어
│   └── boundarybench_task.py          ← Kaggle SDK task wrapper
├── boundarybench_project/
│   └── submission/                    ← 제출 자산 정리본
│       └── docs/
│           ├── FINAL_WRITEUP.md       ← writeup 초안
│           ├── RESULTS_SUMMARY.md
│           └── SUBMISSION_CHECKLIST.md
└── kaggle_boundarybench_v2_50_single_cell.py  ← Kaggle 복붙용 메인 스크립트
```

## 목표: Grand Prize 경쟁력

Track Prize($10,000)를 기본으로, Grand Prize($25,000) 노린다.
핵심 차별화: **failure type별 false certainty pattern + object/meta-level 불일치 사례** — 이건 단순 accuracy benchmark가 절대 보여줄 수 없는 것.

## 실행 계획 (Phase별)

### Phase 1 — 기반 완성 (2026-03-20~23)
- [x] Kaggle Benchmark 생성 + 링크 확보 → https://www.kaggle.com/benchmarks/s0occz/boundarybench
- [ ] GPT-4o quota 이메일 요청 또는 오픈소스 모델 대체 결정
- [ ] cover image 준비

### Phase 2 — Dataset 200문항으로 확장 (2026-03-24~04-03)

목표 구성:
```
determinate:    100문항
  single lookup:      30
  filter+compare:     40
  aggregation:        30

underdetermined: 100문항
  missing_value:      20
  no_satisfying_row:  20
  tie/non-unique:     20
  ordering_ambiguity: 20
  incomplete_agg:     20
```

- failure type별 false certainty rate 비교가 통계적으로 의미 있어짐
- 이게 writeup의 핵심 차별화 근거

### Phase 3 — 모델 4개 이상으로 확장 (2026-04-04~10)

목표:
- Gemini 2.5 Flash ✅
- Claude Sonnet 4 ✅
- GPT-4o (재시도)
- Llama 3 또는 Gemini 2.5 Pro 추가

gradient of performance → discriminatory power 15% 최대화

**추가 검증 (Grand Prize 수준):**
- 프롬프트 문구 변형 시 signal 유지 여부 (robustness test) — 아무도 안 할 것

### Phase 4 — Writeup + Community (2026-04-11~14)

Writeup 핵심 포인트:
1. failure type별 false certainty pattern 분석
2. object-level vs meta-level 불일치 사례 (이미 확보)
3. benchmark robustness 검증 결과

Community upvotes:
- Kaggle Discussion에 benchmark 소개 글 게시
- false certainty 사례를 구체적 예시로 시각화

### Phase 5 — 버퍼 + 최종 제출 (2026-04-15~16)
- 최종 점검, submit

## Writeup 규정 템플릿

```
### Project Name
### Your Team
### Problem Statement
### Task & benchmark construction
### Dataset
### Technical details
### Results, insights, and conclusions
### Organizational affiliations
### References & citations
```

## 규정상 주의사항

- **CC0 라이선스 의무**: 수상 시 전체 코드를 CC0로 공개해야 함 → 지금부터 외부 데이터/라이브러리 라이선스 확인 필요
- **데이터 보안**: Competition Data (여기선 자체 제작 데이터)를 미참가자에게 공유 금지
- 외부 데이터 사용 가능하나 모든 참가자가 동등하게 접근 가능한 것만 허용
- 수상 통보 후 **1주일 이내** 수락 응답 필요
- 수상 서류 **2주 이내** 제출 필요

## Scope 제약 (변경 불가)

- 트랙 추가 금지 — Metacognition 단일 트랙 유지
- 사람 손평가 benchmark 금지
- 라이선스 불분명 외부 데이터 금지
- 특정 모델 점수 올리기 위한 prompt 튜닝 금지
- 목표는 "모델 점수 향상"이 아니라 "모델 간 행동 차이 포착"

## Verification 기준

- JSONL 파싱 성공 필수
- scoring 로직: answerable/abstain 케이스 모두 샘플 검증 후 보고
- 코드 변경 후 `python3 -m py_compile`로 문법 확인
