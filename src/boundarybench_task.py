from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

import kaggle_benchmarks as kbench

from table_world_core import build_prompt, normalize_answer, score_parsed_response


DEFAULT_DATA_PATH = Path("/kaggle/input/boundarybench/table_world_pilot.jsonl")
LOCAL_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "table_world_pilot.jsonl"


@dataclass
class BoundaryResponse:
    decision: str
    answer: str
    confidence: float


def load_table_world_data(path: str | Path | None = None) -> pd.DataFrame:
    dataset_path = Path(path) if path is not None else DEFAULT_DATA_PATH
    if not dataset_path.exists():
        dataset_path = LOCAL_DATA_PATH
    return pd.read_json(dataset_path, lines=True)


@kbench.task(name="boundarybench_table_world_v0")
def boundarybench_table_world(
    llm,
    id: str,
    difficulty: str,
    label_type: str,
    table_csv: str,
    question: str,
    gold_decision: str,
    gold_answer: str,
    acceptable_answers: list[str],
    reason: str,
) -> dict[str, Any]:
    """Evaluates whether the model answers only when the table determines a unique answer."""
    item = {
        "id": id,
        "difficulty": difficulty,
        "label_type": label_type,
        "table_csv": table_csv,
        "question": question,
        "gold_decision": gold_decision,
        "gold_answer": gold_answer,
        "acceptable_answers": acceptable_answers,
        "reason": reason,
    }

    with kbench.chats.new(f"boundarybench:{id}"):
        response = llm.prompt(build_prompt(item), schema=BoundaryResponse)

    score = score_parsed_response(
        item,
        {
            "decision": response.decision,
            "answer": response.answer,
            "confidence": response.confidence,
        },
    )

    score.update(
        {
            "id": id,
            "difficulty": difficulty,
            "label_type": label_type,
            "gold_decision": gold_decision,
        }
    )

    acceptable = {normalize_answer(x) for x in acceptable_answers}
    normalized_answer = normalize_answer(response.answer)

    kbench.assertions.assert_true(
        response.decision in {"answer", "abstain"},
        expectation="Response must choose answer or abstain.",
    )
    kbench.assertions.assert_true(
        0.0 <= float(response.confidence) <= 1.0,
        expectation="Confidence must be between 0 and 1.",
    )
    kbench.assertions.assert_true(
        score["item_correct"],
        expectation="Model should make the correct answer-or-abstain decision.",
    )
    if gold_decision == "answer":
        kbench.assertions.assert_true(
            response.decision == "answer" and normalized_answer in acceptable,
            expectation="When answerable, the returned answer should match the unique gold value.",
        )
    else:
        kbench.assertions.assert_true(
            response.decision == "abstain",
            expectation="When information is insufficient, the model should abstain.",
        )

    return score


def evaluate_table_world(llm=None, evaluation_data: pd.DataFrame | None = None):
    if evaluation_data is None:
        evaluation_data = load_table_world_data()
    if llm is None:
        llm = [kbench.llm]
    elif not isinstance(llm, list):
        llm = [llm]
    return boundarybench_table_world.evaluate(
        llm=llm,
        evaluation_data=evaluation_data,
    )


def summarize_runs(runs) -> pd.DataFrame:
    frame = runs.as_dataframe()
    result_rows = pd.json_normalize(frame["result"]).add_prefix("result.")

    merged = pd.concat(
        [
            frame.drop(columns=["result"]).reset_index(drop=True),
            result_rows.reset_index(drop=True),
        ],
        axis=1,
    )

    group_cols = ["benchmark_model"]
    if "llm.name" in merged.columns:
        group_cols = ["llm.name"]
    elif "llm" in merged.columns:
        group_cols = ["llm"]
    elif "model" in merged.columns:
        group_cols = ["model"]
    else:
        merged["benchmark_model"] = "unknown_model"

    summary = (
        merged.groupby(group_cols, dropna=False)
        .agg(
            n_items=("result.id", "count"),
            overall_accuracy=("result.item_correct", "mean"),
            answer_accuracy=(
                "result.item_correct",
                lambda s: s[merged.loc[s.index, "result.gold_decision"] == "answer"].mean(),
            ),
            abstain_accuracy=(
                "result.item_correct",
                lambda s: s[merged.loc[s.index, "result.gold_decision"] == "abstain"].mean(),
            ),
            overclaim_rate=(
                "result.overclaim",
                lambda s: s[merged.loc[s.index, "result.gold_decision"] == "abstain"].mean(),
            ),
            underclaim_rate=(
                "result.underclaim",
                lambda s: s[merged.loc[s.index, "result.gold_decision"] == "answer"].mean(),
            ),
            mean_confidence=("result.confidence", "mean"),
        )
        .reset_index()
    )

    return summary.sort_values(by="overall_accuracy", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    dataset = load_table_world_data()
    runs = evaluate_table_world(evaluation_data=dataset)
    print(summarize_runs(runs))
