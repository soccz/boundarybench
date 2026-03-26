from kaggle_benchmarks.kaggle import models


candidate_models = [
    models.load_model(model_name="google/gemini-2.5-flash"),
    models.load_model(model_name="openai/gpt-4o"),
    models.load_model(model_name="anthropic/claude-sonnet-4"),
]

with kbench.client.enable_cache():
    multi_runs = boundarybench_table_world_item_v2.evaluate(
        stop_condition=lambda runs: len(runs) == boundary_df.shape[0] * len(candidate_models),
        max_attempts=1,
        llm=candidate_models,
        evaluation_data=boundary_df,
        n_jobs=3,
    )

multi_eval_df = multi_runs.as_dataframe()
multi_result_df = pd.json_normalize(multi_eval_df["result"]).add_prefix("result.")
multi_merged = pd.concat(
    [
        multi_eval_df.drop(columns=["result"]).reset_index(drop=True),
        multi_result_df.reset_index(drop=True),
    ],
    axis=1,
)

model_col = "llm.name" if "llm.name" in multi_merged.columns else "llm"

multi_summary = (
    multi_merged.groupby(model_col, dropna=False)
    .agg(
        n=("id", "count"),
        final_accuracy=("result.final_correct", "mean"),
        answer_accuracy=("result.answer_correct", "mean"),
        boundary_accuracy=("result.boundary_correct", "mean"),
        false_certainty_rate=("result.false_certainty", "mean"),
        missed_certainty_rate=("result.missed_certainty", "mean"),
        mean_answer_confidence=("result.answer_confidence", "mean"),
        mean_boundary_confidence=("result.boundary_confidence", "mean"),
    )
    .reset_index()
    .sort_values(by="false_certainty_rate", ascending=True)
)

display(multi_summary)


multi_false_certainty = multi_merged.loc[
    multi_merged["result.false_certainty"],
    [
        model_col,
        "id",
        "difficulty",
        "label_type",
        "question",
        "result.forced_answer",
        "result.answer_confidence",
        "result.boundary_decision",
        "result.boundary_confidence",
    ],
].sort_values(by=[model_col, "id"])

display(multi_false_certainty)
