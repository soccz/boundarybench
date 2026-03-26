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
MAX_ATTEMPTS = 4
BASE_SLEEP_SECONDS = 5


llm = models.load_model(model_name=MODEL_NAME)

rows = []
errors = []

with kbench.client.enable_cache():
    for idx, row in boundary_df.iterrows():
        item = row.to_dict()
        print(f"Running {item['id']} ({idx + 1}/{len(boundary_df)})")

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
                        "difficulty": item["difficulty"],
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
                        "reason": item["reason"],
                    }
                )
                success = True
                break
            except Exception as e:
                last_error = str(e)
                print(last_error)
                if attempt < MAX_ATTEMPTS:
                    sleep_for = BASE_SLEEP_SECONDS * (2 ** (attempt - 1))
                    print(f"Sleeping {sleep_for}s before retry")
                    time.sleep(sleep_for)

        if not success:
            errors.append({"id": item["id"], "error": last_error})

gpt4o_df = pd.DataFrame(rows)
error_df = pd.DataFrame(errors)

if not gpt4o_df.empty:
    answer_mask = gpt4o_df["gold_decision"] == "answer"
    abstain_mask = gpt4o_df["gold_decision"] == "abstain"

    overall_accuracy = float(gpt4o_df["final_correct"].mean())
    answer_accuracy = float(gpt4o_df.loc[answer_mask, "final_correct"].mean())
    boundary_accuracy = float(gpt4o_df["boundary_correct"].mean())
    false_certainty_rate = float(
        gpt4o_df.loc[abstain_mask, "false_certainty"].mean()
    )
    missed_certainty_rate = float(
        gpt4o_df.loc[answer_mask, "missed_certainty"].mean()
    )

    print(f"Completed rows: {len(gpt4o_df)} / {len(boundary_df)}")
    print(f"Overall accuracy: {overall_accuracy:.3f}")
    print(f"Answer accuracy: {answer_accuracy:.3f}")
    print(f"Boundary accuracy: {boundary_accuracy:.3f}")
    print(f"False certainty rate: {false_certainty_rate:.3f}")
    print(f"Missed certainty rate: {missed_certainty_rate:.3f}")
else:
    print(f"Completed rows: 0 / {len(boundary_df)}")
    print("No successful GPT-4o rows were completed.")

display(gpt4o_df)
display(error_df)
