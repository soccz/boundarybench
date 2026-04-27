# 10-Reviewer Feedback Summary & Actions Taken

## CRITICAL Issues (Fixed)

| Issue | Source | Fix |
|-------|--------|-----|
| 97/500 items had literal `\n` instead of real newlines in table_csv | 관계자1, 관계자4 | All 97 items normalized to real newlines |
| `ordering_ambiguity` taxonomy: 48/51 items were actually multi-criteria preference, not ordering | 관계자1, 평가원3 | Renamed to `criterion_underspecification`; 3 true ordering items remain |
| bwv2_013 "best sprint score" ambiguous column name | 관계자1, 평가원4 | Column renamed `score` -> `time_s`, question updated |
| Assertions fired AFTER scoring logic | 관계자4 | Reordered: defensive parsing -> assertions -> scoring |
| No academic references cited | 평가원1, 평가원5, 관계자2 | Added Kadavath et al., TruthfulQA, SelfAware, selective prediction |
| Writeup over-claimed: "completely prompt-invariant", "cannot be detected" | 관계자5, 평가원3 | All strong claims hedged with appropriate qualifiers |

## MAJOR Issues (Fixed)

| Issue | Source | Fix |
|-------|--------|-----|
| `normalize_answer` too weak for numeric variants | External analysis | Added `answer_matches()` with numeric fallback |
| `label_type` vs `failure_family` confusion in analysis output | External analysis | Removed label_type analysis, failure_family only |
| Missing Limitations section | 평가원1, 평가원2, 평가원3 | Added explicit limitations paragraph |
| Object-meta mismatch count = false certainty count without explanation | 관계자2 | Clarified in writeup with expanded examples |
| Writeup opening lacked hook | 관계자5, 평가원5 | Rewrote opening with concrete bwv2_006 example |
| Robustness statistics too simplistic | 관계자4 | Added per-item agreement rate metric |
| Word count risk | 관계자2 | Final: 1,494 words (under 1,500 limit) |

## Issues Acknowledged in Writeup (Not Code-Fixable)

| Issue | Source | Handling |
|-------|--------|----------|
| Surface-level shortcuts (3-row=abstain, "best"=abstain) | 평가원4 | Acknowledged in Limitations |
| No human baseline | 평가원1, 평가원2, 평가원3 | Acknowledged in Limitations |
| Structured JSON output constrains reasoning | 평가원2 | Acknowledged in Task Construction + Limitations |
| Stage 1 anchoring effect on Stage 2 | 평가원2, 평가원1 | Acknowledged in Limitations |
| n=50 per family limits power for small effects | 평가원1, 관계자3 | Hedged statistical claims ("30pp or more") |

## Issues YOU Must Address Manually (Can't Code-Fix)

| Priority | Issue | Action |
|----------|-------|--------|
| P0 | Benchmark Description is empty | Copy `BENCHMARK_DESCRIPTION.md` content to Kaggle page |
| P0 | Writeup needs updating on Kaggle | Copy `FINAL_WRITEUP.md` to Kaggle writeup page |
| P0 | Notebook code needs updating | Copy `kaggle_boundarybench_v7_final.py` to Kaggle notebook |
| P0 | Cover image required | Create and upload (Submit button won't work without it) |
| P1 | Discussion post for upvotes | Copy `DISCUSSION_POST.md` to Kaggle Discussion |
| P1 | Re-run notebook to get fresh results matching new code | Results numbers in writeup should match actual output |
| P2 | Add more models if quota allows | Llama 3 8B or Mistral 7B for floor baseline |
| P2 | Create bar chart visualization | FC rate by failure family -- for writeup media gallery |

## Reviewer Scores

| Reviewer | Role | Assessment |
|----------|------|------------|
| 관계자1 (Dataset Quality) | "Fundamentally sound. Critical CSV fix needed." |
| 관계자2 (Writeup Quality) | "14-15/20 current, 17-18/20 with fixes" |
| 관계자3 (Discriminatory Power) | "0.20 spread adequate but top cluster is compressed" |
| 관계자4 (Code Quality) | "No scoring logic bugs. CSV + assertion order need fix." |
| 관계자5 (Grand Prize) | "Grand Prize: 5/10. Track Prize: 7/10." |
| 평가원1 (ML Researcher) | "Almost workshop paper level. Missing CIs and related work." |
| 평가원2 (AI Safety) | "Measuring something real. Surface heuristic confound noted." |
| 평가원3 (Competitor) | "Background knowledge in no_satisfying_row is biggest attack" |
| 평가원4 (Data Quality) | "Data quality: 6.5/10. Surface shortcuts are the main concern." |
| 평가원5 (Community) | "Upvote likelihood: 6/10. Needs visuals + better hook." |
