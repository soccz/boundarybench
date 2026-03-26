failure_family_map = {
    "bwv2_006": "no_satisfying_row",
    "bwv2_007": "missing_value",
    "bwv2_009": "tie_non_unique_optimum",
    "bwv2_010": "ordering_ambiguity",
    "bwv2_011": "tie_non_unique_optimum",
    "bwv2_012": "tie_non_unique_optimum",
    "bwv2_016": "tie_non_unique_optimum",
    "bwv2_017": "incomplete_aggregate",
    "bwv2_018": "tie_non_unique_optimum",
    "bwv2_020": "tie_non_unique_optimum",
    "bwv2_022": "missing_value",
    "bwv2_024": "tie_non_unique_optimum",
}

item_id_col = "result.id" if "result.id" in merged.columns else "id"
reason_col = "result.reason" if "result.reason" in merged.columns else "reason"
merged["failure_family"] = merged[item_id_col].map(failure_family_map).fillna("determinate")


# Cell A: 전체 요약
overall_summary = pd.DataFrame(
    [
        {
            "n_items": len(merged),
            "overall_accuracy": float(merged["result.final_correct"].mean()),
            "answer_accuracy": float(
                merged.loc[
                    merged["result.gold_decision"] == "answer",
                    "result.final_correct",
                ].mean()
            ),
            "boundary_accuracy": float(merged["result.boundary_correct"].mean()),
            "false_certainty_rate": float(
                merged.loc[
                    merged["result.gold_decision"] == "abstain",
                    "result.false_certainty",
                ].mean()
            ),
            "missed_certainty_rate": float(
                merged.loc[
                    merged["result.gold_decision"] == "answer",
                    "result.missed_certainty",
                ].mean()
            ),
        }
    ]
)

display(overall_summary)


# Cell B: label_type별 요약
summary_by_label = (
    merged.groupby("label_type", dropna=False)
    .agg(
        n=("id", "count"),
        final_accuracy=("result.final_correct", "mean"),
        boundary_accuracy=("result.boundary_correct", "mean"),
        false_certainty_rate=("result.false_certainty", "mean"),
        mean_answer_confidence=("result.answer_confidence", "mean"),
        mean_boundary_confidence=("result.boundary_confidence", "mean"),
    )
    .reset_index()
)

display(summary_by_label)


# Cell C: failure family별 요약
summary_by_family = (
    merged.loc[merged["failure_family"] != "determinate"]
    .groupby("failure_family", dropna=False)
    .agg(
        n=("id", "count"),
        final_accuracy=("result.final_correct", "mean"),
        boundary_accuracy=("result.boundary_correct", "mean"),
        false_certainty_rate=("result.false_certainty", "mean"),
        mean_answer_confidence=("result.answer_confidence", "mean"),
        mean_boundary_confidence=("result.boundary_confidence", "mean"),
    )
    .reset_index()
    .sort_values(by=["false_certainty_rate", "n"], ascending=[False, False])
)

display(summary_by_family)


# Cell D: false certainty 사례
false_certainty_cases = merged.loc[
    merged["result.false_certainty"],
    [
        item_id_col,
        "failure_family",
        "difficulty",
        "label_type",
        "question",
        "result.forced_answer",
        "result.answer_confidence",
        "result.boundary_decision",
        "result.boundary_confidence",
        reason_col,
    ],
].sort_values(
    by=["failure_family", "result.boundary_confidence", "result.answer_confidence"],
    ascending=[True, False, False],
)

display(false_certainty_cases)


# Cell E: determinate answer misses
answer_miss_cases = merged.loc[
    (merged["result.gold_decision"] == "answer") & (~merged["result.answer_correct"]),
    [
        item_id_col,
        "difficulty",
        "label_type",
        "question",
        "result.forced_answer",
        "result.answer_confidence",
        "result.boundary_decision",
        "result.boundary_confidence",
        reason_col,
    ],
].sort_values(by=["difficulty", item_id_col])

display(answer_miss_cases)


# Cell F: writeup용 문장
print(
    "On the 24-item set, the model maintains strong performance on determinate items "
    "while still showing false certainty on underdetermined cases."
)
print(
    f"False certainty appears in {false_certainty_cases.shape[0]} of "
    f"{int((merged['result.gold_decision'] == 'abstain').sum())} underdetermined items."
)
