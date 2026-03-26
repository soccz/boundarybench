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
ITEM_ID = "bwv2_001"
MAX_ATTEMPTS = 3
SLEEP_SECONDS = 5


llm = models.load_model(model_name=MODEL_NAME)
item = boundary_df.loc[boundary_df["id"] == ITEM_ID].iloc[0].to_dict()

row = None
last_error = None

with kbench.client.enable_cache():
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"Attempt {attempt}/{MAX_ATTEMPTS} for {ITEM_ID}")
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

            row = {
                "id": item["id"],
                "question": item["question"],
                "gold_decision": item["gold_decision"],
                "forced_answer": answer_response.answer,
                "answer_confidence": float(answer_response.confidence),
                "boundary_decision": boundary_response.decision,
                "boundary_confidence": float(boundary_response.confidence),
                "answer_correct": answer_correct,
                "boundary_correct": boundary_correct,
                "final_correct": final_correct,
            }
            break
        except Exception as e:
            last_error = str(e)
            print(last_error)
            if attempt < MAX_ATTEMPTS:
                time.sleep(SLEEP_SECONDS)

if row is None:
    print("Smoke test failed.")
    print(last_error)
else:
    display(pd.DataFrame([row]))
