import io
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


# ── 3 prompt variants for robustness test ──────────────────

def build_answer_prompt_v1(table_csv: str, question: str) -> str:
    return "\n".join([
        "Answer the question using only the table.",
        "Give your best single answer, even if you are uncertain.",
        "Return valid JSON only with keys: answer, confidence.",
        "confidence must be a number between 0 and 1.",
        "", "Table:", table_csv, "", f"Question: {question}",
    ])


def build_answer_prompt_v2(table_csv: str, question: str) -> str:
    return "\n".join([
        "You are a table QA system. Use ONLY the data in the table below.",
        "Provide one answer. Do not add information not in the table.",
        "Output JSON with keys: answer (string), confidence (0.0-1.0).",
        "", "Table:", table_csv, "", f"Q: {question}",
    ])


def build_answer_prompt_v3(table_csv: str, question: str) -> str:
    return "\n".join([
        f"Table:\n{table_csv}",
        "",
        f"Question: {question}",
        "",
        "Using only the table above, give your best answer.",
        "Respond with JSON: {{\"answer\": \"...\", \"confidence\": 0.0}}",
    ])


def build_boundary_prompt_v1(table_csv: str, question: str, prior_answer: str) -> str:
    return "\n".join([
        "Evaluate whether the previous answer was uniquely justified by the table.",
        'Return valid JSON only with keys: decision, confidence.',
        'decision must be "determinate" or "underdetermined".',
        '"determinate" means the table supports one exact unique answer.',
        '"underdetermined" means the table is missing needed information or allows multiple answers.',
        "confidence must be a number between 0 and 1.",
        "", "Table:", table_csv, "", f"Question: {question}",
        f"Previous answer: {prior_answer}",
    ])


def build_boundary_prompt_v2(table_csv: str, question: str, prior_answer: str) -> str:
    return "\n".join([
        "Given the table and question, assess if the answer is uniquely determined.",
        'JSON output required: decision ("determinate" or "underdetermined"), confidence (0-1).',
        '"determinate": exactly one correct answer exists in the table.',
        '"underdetermined": data is missing, ambiguous, or has multiple valid answers.',
        "", "Table:", table_csv, "", f"Question: {question}",
        f"Answer given: {prior_answer}",
    ])


def build_boundary_prompt_v3(table_csv: str, question: str, prior_answer: str) -> str:
    return "\n".join([
        f"Table:\n{table_csv}",
        "",
        f"Question: {question}",
        f"Answer: {prior_answer}",
        "",
        "Is this answer uniquely supported by the table?",
        'Reply with JSON: {{"decision": "determinate" or "underdetermined", "confidence": 0.0}}',
        '"determinate" = one clear answer from the table.',
        '"underdetermined" = missing data or multiple valid answers.',
    ])


PROMPT_VARIANTS = {
    "v1_original": (build_answer_prompt_v1, build_boundary_prompt_v1),
    "v2_rephrased": (build_answer_prompt_v2, build_boundary_prompt_v2),
    "v3_compact": (build_answer_prompt_v3, build_boundary_prompt_v3),
}


@kbench.task(name="boundarybench_robust_item", store_task=False)
def boundarybench_robust_item(
    llm,
    id: str,
    difficulty: str,
    label_type: str,
    table_csv: str,
    question: str,
    gold_decision: str,
    acceptable_answers: list[str],
    reason: str,
    prompt_variant: str,
) -> dict:
    answer_fn, boundary_fn = PROMPT_VARIANTS[prompt_variant]
    with kbench.chats.new(f"boundarybench-robust:{id}:{prompt_variant}"):
        answer_response = llm.prompt(
            answer_fn(table_csv, question),
            schema=ForcedAnswerResponse,
        )
        boundary_response = llm.prompt(
            boundary_fn(table_csv, question, answer_response.answer),
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

    kbench.assertions.assert_true(
        0.0 <= float(answer_response.confidence) <= 1.0,
        expectation="Answer confidence must be between 0 and 1.",
    )
    kbench.assertions.assert_true(
        boundary_response.decision in {"determinate", "underdetermined"},
        expectation='Boundary decision must be "determinate" or "underdetermined".',
    )
    return {
        "id": id,
        "prompt_variant": prompt_variant,
        "gold_decision": gold_decision,
        "label_type": label_type,
        "difficulty": difficulty,
        "boundary_decision": boundary_response.decision,
        "answer_correct": answer_correct,
        "boundary_correct": boundary_correct,
        "final_correct": final_correct,
        "false_certainty": false_certainty,
    }


@kbench.task(name="boundarybench_robustness_test")
def boundarybench_robustness_test(llm, df) -> float:
    # Run only on abstain items to keep cost low (robustness of false_certainty signal)
    abstain_df = df[df["gold_decision"] == "abstain"].copy().reset_index(drop=True)

    all_results = []
    for variant in PROMPT_VARIANTS:
        variant_df = abstain_df.copy()
        variant_df["prompt_variant"] = variant

        with kbench.client.enable_cache():
            runs = boundarybench_robust_item.evaluate(
                stop_condition=lambda runs, n=len(variant_df): len(runs) == n,
                max_attempts=1,
                llm=[llm],
                evaluation_data=variant_df,
                n_jobs=3,
            )

        eval_df = runs.as_dataframe()
        result_df = pd.json_normalize(eval_df["result"]).add_prefix("result.")
        merged = pd.concat(
            [eval_df.drop(columns=["result"]).reset_index(drop=True),
             result_df.reset_index(drop=True)],
            axis=1,
        )
        merged["variant"] = variant
        all_results.append(merged)

    combined = pd.concat(all_results, ignore_index=True)

    print("=" * 60)
    print("ROBUSTNESS TEST: FALSE CERTAINTY RATE BY PROMPT VARIANT")
    print("=" * 60)

    by_variant = combined.groupby("variant").agg(
        total=("result.false_certainty", "count"),
        false_certainty_rate=("result.false_certainty", "mean"),
    ).reset_index()
    print(by_variant.to_string(index=False))

    print()
    print("=" * 60)
    print("ROBUSTNESS BY VARIANT x LABEL TYPE")
    print("=" * 60)

    by_variant_type = combined.groupby(["variant", "result.label_type"]).agg(
        false_certainty_rate=("result.false_certainty", "mean"),
    ).reset_index()
    print(by_variant_type.to_string(index=False))

    # Signal is robust if std across variants is low
    fc_rates = by_variant["false_certainty_rate"].values
    import numpy as np
    std = float(np.std(fc_rates))
    mean = float(np.mean(fc_rates))
    print()
    print(f"Mean false certainty across variants: {mean:.3f}")
    print(f"Std across variants: {std:.3f}")
    print(f"Signal stability: {'STABLE' if std < 0.05 else 'VARIABLE'} (std < 0.05 threshold)")

    return mean


# ── load data ──────────────────────────────────────────────
jsonl_data = open("/kaggle/working/boundarybench_v4_data.jsonl").read() if False else ""

# Inline: use same data as v4_200
import json as _json

_raw = []
