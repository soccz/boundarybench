# Cell A: v2 결과 요약표
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


# Cell B: false certainty가 난 문항만 보기
false_certainty_cases = merged.loc[
    merged["result.false_certainty"],
    [
        "id",
        "difficulty",
        "label_type",
        "question",
        "result.forced_answer",
        "result.answer_confidence",
        "result.boundary_decision",
        "result.boundary_confidence",
        "result.reason",
    ],
].sort_values(
    by=["result.boundary_confidence", "result.answer_confidence"],
    ascending=False,
)

display(false_certainty_cases)


# Cell C: 모든 실패 사례 보기
failure_cases = merged.loc[
    ~merged["result.final_correct"],
    [
        "id",
        "difficulty",
        "label_type",
        "question",
        "result.forced_answer",
        "result.answer_correct",
        "result.boundary_decision",
        "result.boundary_correct",
        "result.false_certainty",
        "result.missed_certainty",
        "result.answer_confidence",
        "result.boundary_confidence",
        "result.reason",
    ],
].sort_values(by=["difficulty", "id"])

display(failure_cases)


# Cell D: writeup에 바로 넣을 수 있는 한 줄 요약
print(
    "Gemini 2.5 Flash shows perfect answer accuracy on determinate questions, "
    f"but marks {false_certainty_cases.shape[0]} underdetermined cases as determinate."
)


# Cell E: 여러 모델 평가 준비
# 공식 user guide 기준으로, 실제 다중 모델 평가는 Task Detail Page의
# 'Evaluate More Models' 버튼으로도 수행할 수 있다.
# 수동으로 로드해서 시험해보려면 아래 형태를 쓴다.
#
# from kaggle_benchmarks.kaggle import models
# candidate_models = [
#     models.load_model(model_name="google/gemini-2.5-flash"),
#     models.load_model(model_name="openai/gpt-4o"),
#     models.load_model(model_name="anthropic/claude-sonnet-4"),
# ]
#
# with kbench.client.enable_cache():
#     multi_runs = boundarybench_table_world_item_v2.evaluate(
#         stop_condition=lambda runs: len(runs) == boundary_df.shape[0] * len(candidate_models),
#         max_attempts=1,
#         llm=candidate_models,
#         evaluation_data=boundary_df,
#         n_jobs=3,
#     )
#
# multi_eval_df = multi_runs.as_dataframe()
# multi_result_df = pd.json_normalize(multi_eval_df["result"]).add_prefix("result.")
# multi_merged = pd.concat(
#     [
#         multi_eval_df.drop(columns=["result"]).reset_index(drop=True),
#         multi_result_df.reset_index(drop=True),
#     ],
#     axis=1,
# )
#
# display(
#     multi_merged.groupby("llm.name", dropna=False).agg(
#         final_accuracy=("result.final_correct", "mean"),
#         answer_accuracy=("result.answer_correct", "mean"),
#         boundary_accuracy=("result.boundary_correct", "mean"),
#         false_certainty_rate=("result.false_certainty", "mean"),
#         missed_certainty_rate=("result.missed_certainty", "mean"),
#     ).reset_index()
# )
