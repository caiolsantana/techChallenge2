"""Collect the three LLM outputs for a documented, manual quality review."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ..ga_vrp.models import Solution
from .prompts import build_messages
from .providers import ChatProvider

CASES = (
    ("instructions", None),
    ("report", None),
    ("ask", "Quais são as entregas críticas e em que ordem serão atendidas?"),
)


def collect_responses(solution: Solution, provider: ChatProvider) -> dict:
    cases = []
    for task, question in CASES:
        messages = build_messages(task, solution, question)
        cases.append(
            {
                "task": task,
                "question": question,
                "response": provider.complete(messages),
                "ratings": {"factual_accuracy": None, "clarity": None, "usefulness": None},
                "review_notes": "",
            }
        )
    return {"created_at_utc": datetime.now(timezone.utc).isoformat(), "cases": cases}


def save_evaluation(record: dict, output: str | Path) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return output
