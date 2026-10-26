"""CLI: collect real LLM responses and create a review record."""

from __future__ import annotations

import argparse
import random

from ..data.scenario import load_scenario
from ..ga_vrp.ga import GAConfig, run_ga
from .evaluation import collect_responses, save_evaluation
from .providers import make_provider


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect three LLM answers for manual quality review")
    parser.add_argument("--scenario", default="data/scenarios/sp_default.json")
    parser.add_argument("--output", default="results/llm-evaluation.json")
    parser.add_argument("--provider", choices=("auto", "groq", "ollama"), default="auto")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    from dotenv import load_dotenv

    load_dotenv()
    random.seed(args.seed)
    scenario = load_scenario(args.scenario)
    result = run_ga(scenario.delivery_points, scenario.vehicles, scenario.depot, GAConfig())
    record = collect_responses(result.best_solution, make_provider(args.provider))
    print(save_evaluation(record, args.output))


if __name__ == "__main__":
    main()
