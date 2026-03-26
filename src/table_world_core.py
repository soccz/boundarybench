import json
from typing import Any


SYSTEM_INSTRUCTION = """You are answering questions about a closed-world table.
Use only the information in the table.
If the answer cannot be determined exactly and uniquely from the table, choose "abstain".
Return valid JSON only with keys: decision, answer, confidence.
decision must be "answer" or "abstain".
confidence must be a number between 0 and 1.
If decision is "abstain", answer should be an empty string."""


def build_prompt(item: dict[str, Any]) -> str:
    return (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"Table:\n{item['table_csv']}\n\n"
        f"Question: {item['question']}"
    )


def parse_model_response(text: str) -> dict[str, Any]:
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("response must decode to a JSON object")

    decision = data.get("decision")
    answer = data.get("answer", "")
    confidence = data.get("confidence")

    if decision not in {"answer", "abstain"}:
        raise ValueError("decision must be 'answer' or 'abstain'")
    if not isinstance(answer, str):
        raise ValueError("answer must be a string")
    if not isinstance(confidence, (int, float)):
        raise ValueError("confidence must be numeric")
    if not 0.0 <= float(confidence) <= 1.0:
        raise ValueError("confidence must be between 0 and 1")

    return {
        "decision": decision,
        "answer": answer.strip(),
        "confidence": float(confidence),
    }


def normalize_answer(text: str) -> str:
    return " ".join(text.strip().lower().split())


def score_parsed_response(item: dict[str, Any], parsed: dict[str, Any]) -> dict[str, Any]:
    result = {
        "format_ok": False,
        "item_correct": False,
        "overclaim": False,
        "underclaim": False,
        "correct_answer": False,
        "decision": None,
        "answer": "",
        "confidence": None,
        "error": "",
    }

    result["format_ok"] = True
    result["decision"] = parsed["decision"]
    result["answer"] = parsed["answer"]
    result["confidence"] = parsed["confidence"]

    gold_decision = item["gold_decision"]
    acceptable = {normalize_answer(x) for x in item.get("acceptable_answers", [])}

    if gold_decision == "answer":
        answer_is_correct = normalize_answer(parsed["answer"]) in acceptable
        result["correct_answer"] = answer_is_correct
        result["underclaim"] = parsed["decision"] == "abstain"
        result["item_correct"] = parsed["decision"] == "answer" and answer_is_correct
    else:
        result["overclaim"] = parsed["decision"] == "answer"
        result["item_correct"] = parsed["decision"] == "abstain"

    return result


def score_item(item: dict[str, Any], response_text: str) -> dict[str, Any]:
    try:
        parsed = parse_model_response(response_text)
    except Exception as exc:
        return {
            "format_ok": False,
            "item_correct": False,
            "overclaim": False,
            "underclaim": False,
            "correct_answer": False,
            "decision": None,
            "answer": "",
            "confidence": None,
            "error": str(exc),
        }

    return score_parsed_response(item, parsed)


def summarize_item_results(results: list[dict[str, Any]]) -> dict[str, float]:
    if not results:
        return {
            "n_items": 0.0,
            "overall_accuracy": 0.0,
            "answer_accuracy": 0.0,
            "abstain_accuracy": 0.0,
            "overclaim_rate": 0.0,
            "underclaim_rate": 0.0,
            "format_success_rate": 0.0,
        }

    answerable = [r for r in results if r.get("gold_decision") == "answer"]
    abstain_items = [r for r in results if r.get("gold_decision") == "abstain"]

    def mean(values: list[bool]) -> float:
        return sum(bool(v) for v in values) / len(values) if values else 0.0

    return {
        "n_items": float(len(results)),
        "overall_accuracy": mean([r["item_correct"] for r in results]),
        "answer_accuracy": mean([r["item_correct"] for r in answerable]),
        "abstain_accuracy": mean([r["item_correct"] for r in abstain_items]),
        "overclaim_rate": mean([r["overclaim"] for r in abstain_items]),
        "underclaim_rate": mean([r["underclaim"] for r in answerable]),
        "format_success_rate": mean([r["format_ok"] for r in results]),
    }
