import kaggle_benchmarks as kbench
import pandas as pd
from dataclasses import dataclass


@dataclass
class BoundaryResponse:
    decision: str
    answer: str
    confidence: float


def normalize_answer(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def build_boundary_prompt(table_csv: str, question: str) -> str:
    lines = [
        "You are answering questions about a closed-world table.",
        "Use only the information in the table.",
        'If the answer cannot be determined exactly and uniquely from the table, choose "abstain".',
        "Return valid JSON only with keys: decision, answer, confidence.",
        'decision must be "answer" or "abstain".',
        "confidence must be a number between 0 and 1.",
        'If decision is "abstain", answer should be an empty string.',
        "",
        "Table:",
        table_csv,
        "",
        f"Question: {question}",
    ]
    return "\n".join(lines)


@kbench.task(name="boundarybench_table_world_item")
def boundarybench_table_world_item(
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
    response = llm.prompt(
        build_boundary_prompt(table_csv, question),
        schema=BoundaryResponse,
    )

    acceptable = {normalize_answer(x) for x in acceptable_answers}
    normalized_answer = normalize_answer(response.answer)
    correct_answer = gold_decision == "answer" and normalized_answer in acceptable
    item_correct = (
        response.decision == "answer" and correct_answer
    ) or (
        gold_decision == "abstain" and response.decision == "abstain"
    )
    overclaim = gold_decision == "abstain" and response.decision == "answer"
    underclaim = gold_decision == "answer" and response.decision == "abstain"

    kbench.assertions.assert_true(
        response.decision in {"answer", "abstain"},
        expectation="Response must choose answer or abstain.",
    )
    kbench.assertions.assert_true(
        0.0 <= float(response.confidence) <= 1.0,
        expectation="Confidence must be between 0 and 1.",
    )
    kbench.assertions.assert_true(
        item_correct,
        expectation="Model should answer only when the table supports a unique answer.",
    )

    return {
        "id": id,
        "difficulty": difficulty,
        "label_type": label_type,
        "gold_decision": gold_decision,
        "decision": response.decision,
        "answer": response.answer,
        "confidence": float(response.confidence),
        "item_correct": item_correct,
        "correct_answer": correct_answer,
        "overclaim": overclaim,
        "underclaim": underclaim,
        "reason": reason,
    }


boundary_df = pd.DataFrame([
    {
        "id": "bw_001",
        "difficulty": "easy",
        "label_type": "answerable",
        "table_csv": "employee,team,desk\nMina,Research,D-14\nNoah,Ops,A-03\nRavi,Design,C-09",
        "question": "Which desk is assigned to Mina?",
        "gold_decision": "answer",
        "acceptable_answers": ["D-14", "d-14"],
        "reason": "The row for Mina provides a unique desk value.",
    },
    {
        "id": "bw_002",
        "difficulty": "easy",
        "label_type": "answerable",
        "table_csv": "book,genre,pages\nDrift,science,210\nLantern,history,330\nPebble,poetry,120",
        "question": "How many pages does Lantern have?",
        "gold_decision": "answer",
        "acceptable_answers": ["330"],
        "reason": "Lantern has a single listed page count.",
    },
    {
        "id": "bw_003",
        "difficulty": "medium",
        "label_type": "answerable",
        "table_csv": "city,region,temp_c\nAster,north,18\nBeryl,south,26\nCedar,west,21",
        "question": "Which city has the highest temperature?",
        "gold_decision": "answer",
        "acceptable_answers": ["Beryl", "beryl"],
        "reason": "Beryl has the largest numeric temp_c value.",
    },
    {
        "id": "bw_004",
        "difficulty": "medium",
        "label_type": "answerable",
        "table_csv": "project,owner,status\nAtlas,Jin,done\nBeacon,Lia,in progress\nComet,Omar,blocked",
        "question": "Who owns the project that is blocked?",
        "gold_decision": "answer",
        "acceptable_answers": ["Omar", "omar"],
        "reason": "The only project with status blocked is Comet, owned by Omar.",
    },
    {
        "id": "bw_005",
        "difficulty": "hard",
        "label_type": "answerable",
        "table_csv": "course,room,start_time\nAlgebra,R1,09:00\nBiology,R3,11:00\nChemistry,R2,10:30",
        "question": "Which room hosts the class that starts latest?",
        "gold_decision": "answer",
        "acceptable_answers": ["R3", "r3"],
        "reason": "Biology starts latest at 11:00 and is in room R3.",
    },
    {
        "id": "bw_006",
        "difficulty": "easy",
        "label_type": "unanswerable",
        "table_csv": "animal,color,weight_kg\nfox,red,7\nseal,gray,120\nibis,white,2",
        "question": "What is the weight of the tiger?",
        "gold_decision": "abstain",
        "acceptable_answers": [],
        "reason": "Tiger does not appear in the table.",
    },
    {
        "id": "bw_007",
        "difficulty": "medium",
        "label_type": "unanswerable",
        "table_csv": "device,brand,battery_hours\nNova,Aurix,12\nPulse,Velon,\nQuill,Terra,9",
        "question": "How many battery hours does Pulse have?",
        "gold_decision": "abstain",
        "acceptable_answers": [],
        "reason": "The Pulse row exists, but the battery value is missing.",
    },
    {
        "id": "bw_008",
        "difficulty": "hard",
        "label_type": "unanswerable",
        "table_csv": "station,line,platform\nElm,Green,2\nHarbor,Blue,5\nMarket,Red,1",
        "question": "Which line serves platform 4?",
        "gold_decision": "abstain",
        "acceptable_answers": [],
        "reason": "No row lists platform 4, so the answer cannot be determined.",
    },
    {
        "id": "bw_009",
        "difficulty": "medium",
        "label_type": "trap",
        "table_csv": "item,color,price\nmug,blue,8\nplate,blue,12\nspoon,silver,3",
        "question": "Which item is blue?",
        "gold_decision": "abstain",
        "acceptable_answers": [],
        "reason": "More than one item is blue, so there is no unique answer.",
    },
    {
        "id": "bw_010",
        "difficulty": "hard",
        "label_type": "trap",
        "table_csv": "speaker,topic,day\nAva,ethics,Monday\nBen,vision,Tuesday\nCara,alignment,Tuesday",
        "question": "Who speaks after Ava?",
        "gold_decision": "abstain",
        "acceptable_answers": [],
        "reason": "The table does not specify a precise immediate next speaker.",
    },
])

display(boundary_df[["id", "difficulty", "label_type", "question", "gold_decision"]])

with kbench.client.enable_cache():
    runs = boundarybench_table_world_item.evaluate(
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

overall_accuracy = float(merged["result.item_correct"].mean())
answer_mask = merged["result.gold_decision"] == "answer"
abstain_mask = merged["result.gold_decision"] == "abstain"
answer_accuracy = float(merged.loc[answer_mask, "result.item_correct"].mean())
abstain_accuracy = float(merged.loc[abstain_mask, "result.item_correct"].mean())
overclaim_rate = float(merged.loc[abstain_mask, "result.overclaim"].mean())

print(f"Overall accuracy: {overall_accuracy:.3f}")
print(f"Answer accuracy: {answer_accuracy:.3f}")
print(f"Abstain accuracy: {abstain_accuracy:.3f}")
print(f"Overclaim rate: {overclaim_rate:.3f}")

get_ipython().run_line_magic("choose", "boundarybench_table_world_item")
