from kaggle_benchmarks.kaggle import models
import pandas as pd


model_names = [
    "google/gemini-2.5-flash",
    "openai/gpt-4o",
    "anthropic/claude-sonnet-4",
]

summary_rows = []
error_rows = []

for model_name in model_names:
    print(f"\n=== Running {model_name} ===")
    try:
        llm = models.load_model(model_name=model_name)

        with kbench.client.enable_cache():
            runs = boundarybench_table_world_item_v2.evaluate(
                stop_condition=lambda runs: len(runs) == boundary_df.shape[0],
                max_attempts=1,
                llm=[llm],
                evaluation_data=boundary_df,
                n_jobs=1,
            )

        eval_df = runs.as_dataframe()
        result_df = pd.json_normalize(eval_df["result"]).add_prefix("result.")
        merged_one = pd.concat(
            [
                eval_df.drop(columns=["result"]).reset_index(drop=True),
                result_df.reset_index(drop=True),
            ],
            axis=1,
        )

        answer_mask = merged_one["result.gold_decision"] == "answer"
        abstain_mask = merged_one["result.gold_decision"] == "abstain"

        summary_rows.append(
            {
                "model": model_name,
                "n": len(merged_one),
                "final_accuracy": float(merged_one["result.final_correct"].mean()),
                "answer_accuracy": float(
                    merged_one.loc[answer_mask, "result.final_correct"].mean()
                ),
                "boundary_accuracy": float(
                    merged_one["result.boundary_correct"].mean()
                ),
                "false_certainty_rate": float(
                    merged_one.loc[abstain_mask, "result.false_certainty"].mean()
                ),
                "missed_certainty_rate": float(
                    merged_one.loc[answer_mask, "result.missed_certainty"].mean()
                ),
            }
        )

    except Exception as e:
        error_rows.append(
            {
                "model": model_name,
                "error": str(e),
            }
        )

display(pd.DataFrame(summary_rows))
display(pd.DataFrame(error_rows))
