from __future__ import annotations

import argparse

from .runner import run_from_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare three GA configurations with nearest neighbor")
    parser.add_argument("--scenario", default="data/scenarios/sp_default.json")
    parser.add_argument("--output", default="results/experiments.json")
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 73, 101])
    args = parser.parse_args()
    report = run_from_file(args.scenario, args.output, tuple(args.seeds))
    print(f"Saved {len(report['runs'])} runs to {args.output} and its CSV companion")
    print(f"Baseline distance: {report['baseline']['distance']} coordinate units; "
          f"unrouted: {report['baseline']['unrouted_points']}")
    for run in report["runs"]:
        print(f"{run['experiment']} seed={run['seed']}: fitness={run['fitness']:.4f}, "
              f"distance={run['distance']:.4f}, unrouted={run['unrouted_points']}")


if __name__ == "__main__":
    main()
