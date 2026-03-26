import io
import time

import kaggle_benchmarks as kbench
import pandas as pd
from dataclasses import dataclass
from kaggle_benchmarks.kaggle import models


@dataclass
class ForcedAnswerResponse:
    answer: str
    confidence: float


@dataclass
class BoundaryDecision:
    decision: str
    confidence: float


def build_answer_prompt(table_csv: str, question: str) -> str:
    lines = [
        "Answer the question using only the table.",
        "Give your best single answer, even if you are uncertain.",
        "Return valid JSON only with keys: answer, confidence.",
        "confidence must be a number between 0 and 1.",
        "",
        "Table:",
        table_csv,
        "",
        f"Question: {question}",
    ]
    return "\n".join(lines)


def build_boundary_prompt(table_csv: str, question: str, prior_answer: str) -> str:
    lines = [
        "Evaluate whether the previous answer was uniquely justified by the table.",
        'Return valid JSON only with keys: decision, confidence.',
        'decision must be "determinate" or "underdetermined".',
        '"determinate" means the table supports one exact unique answer.',
        '"underdetermined" means the table is missing needed information or allows multiple answers.',
        "confidence must be a number between 0 and 1.",
        "",
        "Table:",
        table_csv,
        "",
        f"Question: {question}",
        f"Previous answer: {prior_answer}",
    ]
    return "\n".join(lines)


jsonl_data = """{"id":"bwv2_001","difficulty":"medium","label_type":"answerable","table_csv":"employee,team,shift,hours\\nMina,Research,day,6\\nNoah,Ops,night,9\\nRavi,Design,day,8\\nLia,Research,night,7","question":"Which employee on the Research team works the night shift?","gold_decision":"answer","acceptable_answers":["Lia","lia"],"reason":"Only Lia satisfies both team=Research and shift=night."}
{"id":"bwv2_006","difficulty":"medium","label_type":"unanswerable","table_csv":"animal,color,weight_kg\\nfox,red,7\\nseal,gray,120\\nibis,white,2","question":"Which animal weighs the most and is black?","gold_decision":"abstain","acceptable_answers":[],"reason":"No row satisfies color=black."}
{"id":"bwv2_007","difficulty":"hard","label_type":"unanswerable","table_csv":"device,price,battery_hours\\nNova,300,12\\nPulse,250,\\nQuill,180,9","question":"What is the battery-hours-per-dollar ratio for Pulse?","gold_decision":"abstain","acceptable_answers":[],"reason":"Pulse is missing battery_hours, so the ratio cannot be computed."}
{"id":"bwv2_020","difficulty":"hard","label_type":"trap","table_csv":"runner,lap_seconds\\nAri,61\\nBea,61\\nChen,64","question":"Which runner had the fastest lap overall?","gold_decision":"abstain","acceptable_answers":[],"reason":"Ari and Bea tie for the fastest lap."}
{"id":"bwv2_033","difficulty":"hard","label_type":"answerable","table_csv":"speaker,day,slot\\nIvy,Wednesday,1\\nJae,Wednesday,2\\nMina,Thursday,1","question":"Who speaks immediately after Ivy on Wednesday?","gold_decision":"answer","acceptable_answers":["Jae","jae"],"reason":"Jae is the next Wednesday slot after Ivy."}"""


probe_df = pd.read_json(io.StringIO(jsonl_data), lines=True)

MODEL_NAME = "openai/gpt-4o"
MAX_ATTEMPTS_PER_ITEM = 2
CONSECUTIVE_503_LIMIT = 3
SLEEP_SECONDS = 5

llm = models.load_model(model_name=MODEL_NAME)
rows = []
errors = []
consecutive_503 = 0

with kbench.client.enable_cache():
    for idx, row in probe_df.iterrows():
        item = row.to_dict()
        print(f"Probe {item['id']} ({idx + 1}/{len(probe_df)})")

        success = False
        last_error = None

        for attempt in range(1, MAX_ATTEMPTS_PER_ITEM + 1):
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

                rows.append(
                    {
                        "id": item["id"],
                        "forced_answer": answer_response.answer,
                        "answer_confidence": float(answer_response.confidence),
                        "boundary_decision": boundary_response.decision,
                        "boundary_confidence": float(boundary_response.confidence),
                    }
                )
                success = True
                consecutive_503 = 0
                break
            except Exception as e:
                last_error = str(e)
                print(last_error)
                if "503" in last_error and "model is currently unavailable" in last_error:
                    consecutive_503 += 1
                else:
                    consecutive_503 = 0
                if attempt < MAX_ATTEMPTS_PER_ITEM:
                    time.sleep(SLEEP_SECONDS)

            if consecutive_503 >= CONSECUTIVE_503_LIMIT:
                break

        if not success:
            errors.append({"id": item["id"], "error": last_error})

        if consecutive_503 >= CONSECUTIVE_503_LIMIT:
            print("Stopping early: repeated 503 responses indicate runtime availability failure.")
            break

probe_result_df = pd.DataFrame(rows)
error_df = pd.DataFrame(errors)

print(f"Successful probe rows: {len(probe_result_df)} / {len(probe_df)}")
print(f"Consecutive 503 threshold hit: {consecutive_503 >= CONSECUTIVE_503_LIMIT}")
display(probe_result_df)
display(error_df)
