import kaggle_benchmarks as kbench
import pandas as pd
from dataclasses import dataclass


@dataclass
class ForcedAnswerResponse:
    answer: str
    confidence: float


@dataclass
class BoundaryDecision:
    decision: str
    confidence: float


def normalize_answer(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


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


@kbench.task(name="boundarybench_table_world_item_v2")
def boundarybench_table_world_item_v2(
    llm,
    id: str,
    difficulty: str,
    label_type: str,
    table_csv: str,
    question: str,
    gold_decision: str,
    acceptable_answers: list[str],
    reason: str,
) -> dict:
    with kbench.chats.new(f"boundarybench-v2:{id}"):
        answer_response = llm.prompt(
            build_answer_prompt(table_csv, question),
            schema=ForcedAnswerResponse,
        )
        boundary_response = llm.prompt(
            build_boundary_prompt(table_csv, question, answer_response.answer),
            schema=BoundaryDecision,
        )

    acceptable = {normalize_answer(x) for x in acceptable_answers}
    normalized_answer = normalize_answer(answer_response.answer)
    answer_correct = gold_decision == "answer" and normalized_answer in acceptable
    boundary_correct = (
        gold_decision == "answer" and boundary_response.decision == "determinate"
    ) or (
        gold_decision == "abstain" and boundary_response.decision == "underdetermined"
    )

    final_correct = (
        gold_decision == "answer" and answer_correct and boundary_correct
    ) or (
        gold_decision == "abstain" and boundary_correct
    )

    false_certainty = gold_decision == "abstain" and boundary_response.decision == "determinate"
    missed_certainty = gold_decision == "answer" and boundary_response.decision == "underdetermined"

    kbench.assertions.assert_true(
        0.0 <= float(answer_response.confidence) <= 1.0,
        expectation="Answer-stage confidence must be between 0 and 1.",
    )
    kbench.assertions.assert_true(
        boundary_response.decision in {"determinate", "underdetermined"},
        expectation='Boundary-stage decision must be "determinate" or "underdetermined".',
    )
    kbench.assertions.assert_true(
        0.0 <= float(boundary_response.confidence) <= 1.0,
        expectation="Boundary-stage confidence must be between 0 and 1.",
    )
    kbench.assertions.assert_true(
        final_correct,
        expectation="The model should answer correctly when possible and detect underdetermined cases when not.",
    )

    return {
        "id": id,
        "difficulty": difficulty,
        "label_type": label_type,
        "gold_decision": gold_decision,
        "forced_answer": answer_response.answer,
        "answer_confidence": float(answer_response.confidence),
        "boundary_decision": boundary_response.decision,
        "boundary_confidence": float(boundary_response.confidence),
        "answer_correct": answer_correct,
        "boundary_correct": boundary_correct,
        "final_correct": final_correct,
        "false_certainty": false_certainty,
        "missed_certainty": missed_certainty,
        "reason": reason,
    }


boundary_df = pd.DataFrame([
    {
        "id": "bwv1_001",
        "difficulty": "medium",
        "label_type": "answerable",
        "table_csv": "employee,team,shift,hours\nMina,Research,day,6\nNoah,Ops,night,9\nRavi,Design,day,8\nLia,Research,night,7",
        "question": "Which employee on the Research team works the night shift?",
        "gold_decision": "answer",
        "acceptable_answers": ["Lia", "lia"],
        "reason": "Only Lia satisfies both team=Research and shift=night.",
    },
    {
        "id": "bwv1_002",
        "difficulty": "hard",
        "label_type": "answerable",
        "table_csv": "item,category,stock\npen,office,14\ntape,office,9\nmug,kitchen,12\nplate,kitchen,7",
        "question": "What is the total stock of office items?",
        "gold_decision": "answer",
        "acceptable_answers": ["23"],
        "reason": "Office stock is 14 + 9 = 23.",
    },
    {
        "id": "bwv1_003",
        "difficulty": "hard",
        "label_type": "answerable",
        "table_csv": "city,region,temp_c,rain_mm\nAster,north,18,2\nBeryl,south,26,0\nCedar,west,21,5\nDune,south,24,1",
        "question": "Which city in the south region has the lower temperature?",
        "gold_decision": "answer",
        "acceptable_answers": ["Dune", "dune"],
        "reason": "The south-region cities are Beryl and Dune; Dune is lower.",
    },
    {
        "id": "bwv1_004",
        "difficulty": "hard",
        "label_type": "answerable",
        "table_csv": "project,owner,status,priority\nAtlas,Jin,done,2\nBeacon,Lia,in progress,1\nComet,Omar,blocked,3\nDelta,Mina,blocked,1",
        "question": "Which owner has the blocked project with the highest priority number?",
        "gold_decision": "answer",
        "acceptable_answers": ["Omar", "omar"],
        "reason": "Among blocked projects, Comet has the highest priority number.",
    },
    {
        "id": "bwv1_005",
        "difficulty": "hard",
        "label_type": "answerable",
        "table_csv": "course,room,start_time,instructor\nAlgebra,R1,09:00,Chen\nBiology,R3,11:00,Patel\nChemistry,R2,10:30,Garcia\nDrama,R4,11:30,Lopez",
        "question": "Which instructor teaches in the room with the latest start time?",
        "gold_decision": "answer",
        "acceptable_answers": ["Lopez", "lopez"],
        "reason": "Drama starts latest and is taught by Lopez.",
    },
    {
        "id": "bwv1_006",
        "difficulty": "medium",
        "label_type": "unanswerable",
        "table_csv": "animal,color,weight_kg\nfox,red,7\nseal,gray,120\nibis,white,2",
        "question": "Which animal weighs the most and is black?",
        "gold_decision": "abstain",
        "acceptable_answers": [],
        "reason": "No black animal appears in the table.",
    },
    {
        "id": "bwv1_007",
        "difficulty": "hard",
        "label_type": "unanswerable",
        "table_csv": "device,brand,battery_hours,price\nNova,Aurix,12,399\nPulse,Velon,,449\nQuill,Terra,9,299",
        "question": "What is the battery-hours-per-dollar ratio for Pulse?",
        "gold_decision": "abstain",
        "acceptable_answers": [],
        "reason": "Pulse is missing battery_hours, so the ratio cannot be computed.",
    },
    {
        "id": "bwv1_008",
        "difficulty": "hard",
        "label_type": "answerable",
        "table_csv": "station,line,platform,status\nElm,Green,2,open\nHarbor,Blue,5,open\nMarket,Red,1,closed\nUnion,Blue,5,maintenance",
        "question": "Which open station on platform 5 comes first alphabetically?",
        "gold_decision": "answer",
        "acceptable_answers": ["Harbor", "harbor"],
        "reason": "Only Harbor is both open and on platform 5.",
    },
    {
        "id": "bwv1_009",
        "difficulty": "hard",
        "label_type": "trap",
        "table_csv": "item,color,price\nmug,blue,8\nplate,blue,12\nbowl,blue,12\nspoon,silver,3",
        "question": "Which blue item is the most expensive?",
        "gold_decision": "abstain",
        "acceptable_answers": [],
        "reason": "Plate and bowl tie for the highest blue price.",
    },
    {
        "id": "bwv1_010",
        "difficulty": "hard",
        "label_type": "trap",
        "table_csv": "speaker,topic,day,slot\nAva,ethics,Monday,1\nBen,vision,Tuesday,1\nCara,alignment,Tuesday,1\nDrew,safety,Wednesday,2",
        "question": "Who speaks immediately after Ava?",
        "gold_decision": "abstain",
        "acceptable_answers": [],
        "reason": "The table does not define a unique immediate next speaker after Ava.",
    },
    {
        "id": "bwv1_011",
        "difficulty": "hard",
        "label_type": "trap",
        "table_csv": "student,club,points\nNia,robotics,12\nOwen,robotics,12\nPia,debate,15\nQuin,debate,9",
        "question": "Which robotics student has the highest points?",
        "gold_decision": "abstain",
        "acceptable_answers": [],
        "reason": "Nia and Owen tie for the highest robotics score.",
    },
    {
        "id": "bwv1_012",
        "difficulty": "hard",
        "label_type": "trap",
        "table_csv": "package,zone,weight_kg,carrier\nA1,north,4,Swift\nA2,north,4,Rapid\nB1,south,6,Swift\nB2,south,2,Rapid",
        "question": "Which carrier ships the lightest package in the north zone?",
        "gold_decision": "abstain",
        "acceptable_answers": [],
        "reason": "The two north-zone packages tie in weight, so there is no unique carrier answer.",
    },
])

display(boundary_df[["id", "difficulty", "label_type", "question", "gold_decision"]])

with kbench.client.enable_cache():
    runs = boundarybench_table_world_item_v2.evaluate(
        stop_condition=lambda runs: len(runs) == boundary_df.shape[0],
        max_attempts=1,
        llm=[kbench.llm],
        evaluation_data=boundary_df,
        n_jobs=3,
    )

eval_df = runs.as_dataframe()
result_df = pd.json_normalize(eval_df["result"]).add_prefix("result.")
merged = pd.concat(
    [
        eval_df.drop(columns=["result"]).reset_index(drop=True),
        result_df.reset_index(drop=True),
    ],
    axis=1,
)

overall_accuracy = float(merged["result.final_correct"].mean())
answer_mask = merged["result.gold_decision"] == "answer"
abstain_mask = merged["result.gold_decision"] == "abstain"
answer_accuracy = float(merged.loc[answer_mask, "result.final_correct"].mean())
boundary_accuracy = float(merged["result.boundary_correct"].mean())
false_certainty_rate = float(merged.loc[abstain_mask, "result.false_certainty"].mean())
missed_certainty_rate = float(merged.loc[answer_mask, "result.missed_certainty"].mean())

print(f"Overall accuracy: {overall_accuracy:.3f}")
print(f"Answer accuracy: {answer_accuracy:.3f}")
print(f"Boundary accuracy: {boundary_accuracy:.3f}")
print(f"False certainty rate: {false_certainty_rate:.3f}")
print(f"Missed certainty rate: {missed_certainty_rate:.3f}")

get_ipython().run_line_magic("choose", "boundarybench_table_world_item_v2")
