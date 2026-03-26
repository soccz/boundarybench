from kaggle_benchmarks.kaggle import models
import pandas as pd
import time


required_names = [
    "kbench",
    "boundary_df",
    "build_answer_prompt",
    "build_boundary_prompt",
    "ForcedAnswerResponse",
    "BoundaryDecision",
    "normalize_answer",
]
missing_names = [name for name in required_names if name not in globals()]
if missing_names:
    missing_text = ", ".join(missing_names)
    raise RuntimeError(
        "Run boundarybench_v2_50_single_cell.py first in the same notebook. "
        f"Missing prerequisites: {missing_text}"
    )


MODEL_NAME = "openai/gpt-4o"
SAMPLE_IDS = [
    "bwv2_001",
    "bwv2_006",
    "bwv2_007",
    "bwv2_020",
    "bwv2_033",
]
MAX_ATTEMPTS = 3
SLEEP_SECONDS = 5


llm = models.load_model(model_name=MODEL_NAME)
sample_df = boundary_df.loc[boundary_df["id"].isin(SAMPLE_IDS)].copy()

rows = []
errors = []

with kbench.client.enable_cache():
    for idx, (_, source_row) in enumerate(sample_df.iterrows(), start=1):
        item = source_row.to_dict()
        print(f"Running {item['id']} ({idx}/{len(sample_df)})")

        success = False
        last_error = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                answer_response = llm.prompt(
                    build_answer_prompt(item["table_csv"], item["question"]),
                    schema=ForcedAnswerResponse,
                )
                boundary_response = llm.prompt(
                    build_boundary_prompt(
                        item["table_csv"],
                        item["question"],
                        answer_response.answer,
                    ),
                    schema=BoundaryDecision,
                )

                acceptable = {normalize_answer(x) for x in item["acceptable_answers"]}
                normalized_answer = normalize_answer(answer_response.answer)
                answer_correct = (
                    item["gold_decision"] == "answer"
                    and normalized_answer in acceptable
                )
                boundary_correct = (
                    item["gold_decision"] == "answer"
                    and boundary_response.decision == "determinate"
                ) or (
                    item["gold_decision"] == "abstain"
                    and boundary_response.decision == "underdetermined"
                )
                final_correct = (
                    item["gold_decision"] == "answer"
                    and answer_correct
                    and boundary_correct
                ) or (
                    item["gold_decision"] == "abstain"
                    and boundary_correct
                )
                false_certainty = (
                    item["gold_decision"] == "abstain"
                    and boundary_response.decision == "determinate"
                )
                missed_certainty = (
                    item["gold_decision"] == "answer"
                    and boundary_response.decision == "underdetermined"
                )

                rows.append(
                    {
                        "id": item["id"],
                        "label_type": item["label_type"],
                        "gold_decision": item["gold_decision"],
                        "forced_answer": answer_response.answer,
                        "answer_confidence": float(answer_response.confidence),
                        "boundary_decision": boundary_response.decision,
                        "boundary_confidence": float(boundary_response.confidence),
                        "answer_correct": answer_correct,
                        "boundary_correct": boundary_correct,
                        "final_correct": final_correct,
                        "false_certainty": false_certainty,
                        "missed_certainty": missed_certainty,
                    }
                )
                success = True
                break
            except Exception as e:
                last_error = str(e)
                print(last_error)
                if attempt < MAX_ATTEMPTS:
                    time.sleep(SLEEP_SECONDS)

        if not success:
            errors.append({"id": item["id"], "error": last_error})

sample_result_df = pd.DataFrame(rows)
error_df = pd.DataFrame(errors)

print(f"Completed rows: {len(sample_result_df)} / {len(sample_df)}")
display(sample_result_df)
display(error_df)
