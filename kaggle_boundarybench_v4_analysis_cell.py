# ── BoundaryBench v4 Analysis Cell ──
# 이 셀을 v4_200 실행 완료 후 바로 이어서 실행하세요.
# merged DataFrame이 메모리에 있어야 합니다.

import pandas as pd

# ── 1. failure type별 false certainty rate ──
print("=" * 60)
print("FALSE CERTAINTY RATE BY FAILURE TYPE")
print("=" * 60)

abstain_df = merged[merged["result.gold_decision"] == "abstain"].copy()

if "result.label_type" in merged.columns:
    label_col = "result.label_type"
else:
    label_col = None

# label_type이 result에 없으면 boundary_df에서 join
if label_col is None:
    label_map = boundary_df.set_index("id")["label_type"].to_dict()
    abstain_df["label_type"] = abstain_df["result.id"].map(label_map)
    label_col = "label_type"

by_type = abstain_df.groupby(label_col).agg(
    total=("result.false_certainty", "count"),
    false_certainty_count=("result.false_certainty", "sum"),
    false_certainty_rate=("result.false_certainty", "mean"),
).reset_index()

print(by_type.to_string(index=False))

# ── 2. difficulty별 false certainty rate ──
print()
print("=" * 60)
print("FALSE CERTAINTY RATE BY DIFFICULTY")
print("=" * 60)

diff_map = boundary_df.set_index("id")["difficulty"].to_dict()
abstain_df["difficulty"] = abstain_df["result.id"].map(diff_map)

by_diff = abstain_df.groupby("difficulty").agg(
    total=("result.false_certainty", "count"),
    false_certainty_rate=("result.false_certainty", "mean"),
).reset_index()

print(by_diff.to_string(index=False))

# ── 3. object-level vs meta-level 불일치 케이스 ──
print()
print("=" * 60)
print("OBJECT-META MISMATCH CASES")
print("(answer text mentions uncertainty but boundary = determinate)")
print("=" * 60)

mismatch = merged[
    (merged["result.gold_decision"] == "abstain") &
    (merged["result.boundary_decision"] == "determinate")
][["result.id", "result.forced_answer", "result.boundary_decision", "result.boundary_confidence"]].copy()

# label_type 붙이기
mismatch["label_type"] = mismatch["result.id"].map(label_map)

print(f"Total false certainty cases: {len(mismatch)}")
print()
for _, row in mismatch.iterrows():
    print(f"[{row['result.id']}] ({row['label_type']})")
    print(f"  Answer: {row['result.forced_answer'][:120]}")
    print(f"  Boundary: {row['result.boundary_decision']} (conf={row['result.boundary_confidence']:.2f})")
    print()

# ── 4. 전체 요약 ──
print("=" * 60)
print("SUMMARY")
print("=" * 60)
total = len(merged)
answer_n = len(merged[merged["result.gold_decision"] == "answer"])
abstain_n = len(merged[merged["result.gold_decision"] == "abstain"])
print(f"Total items: {total} (answerable={answer_n}, abstain={abstain_n})")
print(f"Overall accuracy:       {float(merged['result.final_correct'].mean()):.3f}")
print(f"Answer accuracy:        {float(merged.loc[merged['result.gold_decision']=='answer', 'result.answer_correct'].mean()):.3f}")
print(f"Boundary accuracy:      {float(merged['result.boundary_correct'].mean()):.3f}")
print(f"False certainty rate:   {float(merged.loc[merged['result.gold_decision']=='abstain', 'result.false_certainty'].mean()):.3f}")
print(f"Missed certainty rate:  {float(merged.loc[merged['result.gold_decision']=='answer', 'result.missed_certainty'].mean()):.3f}")
