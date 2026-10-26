"""Run an LLM task against a reproducible saved scenario."""

from __future__ import annotations

import argparse
import random

from ..data.scenario import load_scenario
from ..ga_vrp.ga import GAConfig, run_ga
from .prompts import build_messages
from .providers import make_provider


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask an LLM about optimized medical delivery routes")
    parser.add_argument("task", choices=("instructions", "report", "ask"))
    parser.add_argument("--question", help="Required for the ask task")
    parser.add_argument("--provider", choices=("auto", "groq", "ollama"), default="auto")
    parser.add_argument("--scenario", default="data/scenarios/sp_default.json")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    from dotenv import load_dotenv

    load_dotenv()
    random.seed(args.seed)
    scenario = load_scenario(args.scenario)
    result = run_ga(scenario.delivery_points, scenario.vehicles, scenario.depot, GAConfig())
    messages = build_messages(args.task, result.best_solution, args.question)
    print(make_provider(args.provider).complete(messages))


if __name__ == "__main__":
    main()
