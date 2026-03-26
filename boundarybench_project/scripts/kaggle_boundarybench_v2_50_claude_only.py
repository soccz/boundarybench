from kaggle_benchmarks.kaggle import models
import pandas as pd


llm = models.load_model(model_name="anthropic/claude-sonnet-4")

with kbench.client.enable_cache():
    runs = boundarybench_table_world_item_v2_50.evaluate(
        stop_condition=lambda runs: len(runs) == boundary_df.shape[0],
        max_attempts=1,
        llm=[llm],
        evaluation_data=boundary_df,
        n_jobs=1,
    )

eval_df = runs.as_dataframe()
result_df = pd.json_normalize(eval_df["result"]).add_prefix("result.")
merged_claude = pd.concat(
    [
        eval_df.drop(columns=["result"]).reset_index(drop=True),
        result_df.reset_index(drop=True),
    ],
    axis=1,
)

answer_mask = merged_claude["result.gold_decision"] == "answer"
abstain_mask = merged_claude["result.gold_decision"] == "abstain"

overall_accuracy = float(merged_claude["result.final_correct"].mean())
answer_accuracy = float(merged_claude.loc[answer_mask, "result.final_correct"].mean())
boundary_accuracy = float(merged_claude["result.boundary_correct"].mean())
false_certainty_rate = float(
    merged_claude.loc[abstain_mask, "result.false_certainty"].mean()
)
missed_certainty_rate = float(
    merged_claude.loc[answer_mask, "result.missed_certainty"].mean()
)

print(f"Overall accuracy: {overall_accuracy:.3f}")
print(f"Answer accuracy: {answer_accuracy:.3f}")
print(f"Boundary accuracy: {boundary_accuracy:.3f}")
print(f"False certainty rate: {false_certainty_rate:.3f}")
print(f"Missed certainty rate: {missed_certainty_rate:.3f}")
