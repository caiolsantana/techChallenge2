"""Synthetic scenario generator for the VRP (Fase 2).

Produces a `Depot`, a list of `DeliveryPoint` and a `Vehicle` fleet — the exact three
arguments `src.ga_vrp.ga.run_ga()` expects — from a small, parametrizable `ScenarioConfig`
(loadable from YAML/JSON) instead of the hardcoded `_demo_scenario()` used during Fase 1.

Coordinates are random points inside a São Paulo-scale lat/lon bounding box (see
`SAO_PAULO_BBOX`), not real geocoded addresses — enough for a synthetic, reproducible
benchmark, consistent with the plane-distance approximation already used in `geo.py`.
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path

from ..ga_vrp.models import Depot, DeliveryPoint, Priority, Vehicle

# Rough bounding box for the São Paulo metropolitan area.
SAO_PAULO_BBOX = {
    "lat_min": -23.68,
    "lat_max": -23.40,
    "lon_min": -46.75,
    "lon_max": -46.40,
}
SAO_PAULO_DEPOT = {"lat": -23.5505, "lon": -46.6333}  # Praça da Sé (city center)


@dataclass
class ScenarioConfig:
    seed: int = 42
    n_points: int = 30
    critical_ratio: float = 0.3  # fraction of delivery points marked CRITICAL
    demand_min: float = 1.0
    demand_max: float = 5.0
    n_vehicles: int = 4
    # Left as None, capacity/range are auto-sized from n_points/n_vehicles/demand (see
    # `_resolve_vehicle_bounds`) so the fleet stays feasible regardless of scenario size.
    # Set explicitly (e.g. in a Fase 5 experiment config) to force a tighter/looser fleet.
    vehicle_capacity_min: float | None = None
    vehicle_capacity_max: float | None = None
    vehicle_range_min: float | None = None
    vehicle_range_max: float | None = None
    bbox: dict = field(default_factory=lambda: dict(SAO_PAULO_BBOX))
    depot_lat: float = SAO_PAULO_DEPOT["lat"]
    depot_lon: float = SAO_PAULO_DEPOT["lon"]

    @classmethod
    def from_dict(cls, data: dict) -> "ScenarioConfig":
        known_fields = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known_fields})


@dataclass
class GeneratedScenario:
    depot: Depot
    delivery_points: list[DeliveryPoint]
    vehicles: list[Vehicle]


def load_config(path: str | Path) -> ScenarioConfig:
    path = Path(path)
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        data = json.loads(raw)
    else:
        import yaml

        data = yaml.safe_load(raw)
    return ScenarioConfig.from_dict(data or {})


def generate_scenario(config: ScenarioConfig | None = None) -> GeneratedScenario:
    config = config or ScenarioConfig()
    rng = random.Random(config.seed)

    depot = Depot(lat=config.depot_lat, lon=config.depot_lon)
    delivery_points = [_random_delivery_point(rng, config, index) for index in range(config.n_points)]
    capacity_bounds, range_bounds = _resolve_vehicle_bounds(config)
    vehicles = [
        _random_vehicle(rng, index, capacity_bounds, range_bounds) for index in range(config.n_vehicles)
    ]

    return GeneratedScenario(depot=depot, delivery_points=delivery_points, vehicles=vehicles)


def _random_delivery_point(rng: random.Random, config: ScenarioConfig, index: int) -> DeliveryPoint:
    bbox = config.bbox
    priority = Priority.CRITICAL if rng.random() < config.critical_ratio else Priority.REGULAR
    return DeliveryPoint(
        id=f"dp{index + 1}",
        lat=rng.uniform(bbox["lat_min"], bbox["lat_max"]),
        lon=rng.uniform(bbox["lon_min"], bbox["lon_max"]),
        priority=priority,
        demand=round(rng.uniform(config.demand_min, config.demand_max), 2),
    )


def _resolve_vehicle_bounds(config: ScenarioConfig) -> tuple[tuple[float, float], tuple[float, float]]:
    """Fill in capacity/range bounds left as `None`, auto-sized from n_points/n_vehicles so the
    fleet can plausibly carry all demand and reach all points, regardless of scenario size.

    Capacity target: average demand per vehicle (total expected demand / n_vehicles) with a
    1.1x-1.6x margin, so the GA still has some slack to explore uneven splits.

    Range target: a vehicle visiting `n_points / n_vehicles` stops in a random order (the GA's
    giant-tour split is not nearest-neighbor-sorted) travels, on average, about half the bbox
    diagonal per hop; a 1.3x-2.0x margin keeps that feasible even for less efficient splits.
    """
    bbox = config.bbox
    bbox_diagonal = ((bbox["lat_max"] - bbox["lat_min"]) ** 2 + (bbox["lon_max"] - bbox["lon_min"]) ** 2) ** 0.5
    avg_demand = (config.demand_min + config.demand_max) / 2
    avg_points_per_vehicle = config.n_points / config.n_vehicles

    if config.vehicle_capacity_min is not None and config.vehicle_capacity_max is not None:
        capacity_bounds = (config.vehicle_capacity_min, config.vehicle_capacity_max)
    else:
        per_vehicle_demand = avg_demand * avg_points_per_vehicle
        capacity_bounds = (per_vehicle_demand * 1.1, per_vehicle_demand * 1.6)

    if config.vehicle_range_min is not None and config.vehicle_range_max is not None:
        range_bounds = (config.vehicle_range_min, config.vehicle_range_max)
    else:
        expected_route_distance = (avg_points_per_vehicle + 1) * 0.5 * bbox_diagonal
        range_bounds = (expected_route_distance * 1.3, expected_route_distance * 2.0)

    return capacity_bounds, range_bounds


def _random_vehicle(
    rng: random.Random,
    index: int,
    capacity_bounds: tuple[float, float],
    range_bounds: tuple[float, float],
) -> Vehicle:
    return Vehicle(
        id=f"v{index + 1}",
        capacity=round(rng.uniform(*capacity_bounds), 2),
        max_range=round(rng.uniform(*range_bounds), 4),
    )


def scenario_to_dict(scenario: GeneratedScenario) -> dict:
    return {
        "depot": asdict(scenario.depot),
        "delivery_points": [
            {**asdict(point), "priority": point.priority.value} for point in scenario.delivery_points
        ],
        "vehicles": [asdict(vehicle) for vehicle in scenario.vehicles],
    }


def save_scenario(scenario: GeneratedScenario, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(scenario_to_dict(scenario), indent=2, ensure_ascii=False), encoding="utf-8")


def load_scenario(path: str | Path) -> GeneratedScenario:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    depot = Depot(**data["depot"])
    delivery_points = [
        DeliveryPoint(**{**point, "priority": Priority(point["priority"])}) for point in data["delivery_points"]
    ]
    vehicles = [Vehicle(**vehicle) for vehicle in data["vehicles"]]
    return GeneratedScenario(depot=depot, delivery_points=delivery_points, vehicles=vehicles)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a synthetic São Paulo-scale VRP scenario.")
    parser.add_argument(
        "--config",
        default="data/config/scenario_default.yaml",
        help="Path to a YAML/JSON scenario config (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        default="data/scenarios/sp_default.json",
        help="Path to write the generated scenario as JSON (default: %(default)s)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    config = load_config(args.config) if Path(args.config).exists() else ScenarioConfig()
    scenario = generate_scenario(config)
    save_scenario(scenario, args.output)

    n_critical = sum(1 for p in scenario.delivery_points if p.priority == Priority.CRITICAL)
    print(f"Generated {len(scenario.delivery_points)} delivery points ({n_critical} CRITICAL) "
          f"and {len(scenario.vehicles)} vehicles.")
    print(f"Depot: ({scenario.depot.lat:.4f}, {scenario.depot.lon:.4f})")
    for vehicle in scenario.vehicles:
        print(f"  {vehicle.id}: capacity={vehicle.capacity}, max_range={vehicle.max_range:.2f}")
    print(f"Saved scenario to {args.output}")
