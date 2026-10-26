"""Ground all three LLM tasks in the decoded solution's actual data."""

from __future__ import annotations

import json

from ..ga_vrp.models import Solution

SYSTEM_PROMPT = (
    "Você é um assistente de logística hospitalar. Responda em português usando somente os dados "
    "fornecidos. Não invente endereço, horário, tempo de viagem, economia, quilômetros ou estado "
    "do trânsito. As distâncias estão em unidades de coordenada, não em quilômetros. Se faltarem "
    "dados para uma resposta, diga claramente o que falta. Não omita entregas não roteadas."
)


def solution_context(solution: Solution, baseline_distance: float | None = None) -> str:
    data = {
        "distance_unit": "unidades de coordenada (distância euclidiana em lat/lon)",
        "total_distance": round(solution.total_distance, 6),
        "routes": [
            {
                "vehicle_id": route.vehicle.id,
                "capacity": route.vehicle.capacity,
                "load": route.load,
                "max_range": route.vehicle.max_range,
                "distance": round(route.distance, 6),
                "stops": [
                    {
                        "order": index,
                        "id": point.id,
                        "priority": point.priority.value,
                        "demand": point.demand,
                        "lat": point.lat,
                        "lon": point.lon,
                    }
                    for index, point in enumerate(route.points, 1)
                ],
            }
            for route in solution.routes
        ],
        "unrouted_point_ids": [point.id for point in solution.unrouted_points],
    }
    if baseline_distance is not None:
        data["baseline_distance"] = round(baseline_distance, 6)
    return json.dumps(data, ensure_ascii=False, indent=2)


def build_messages(
    task: str,
    solution: Solution,
    question: str | None = None,
    baseline_distance: float | None = None,
) -> list[dict[str, str]]:
    if task == "instructions":
        instruction = (
            "Gere instruções de entrega por veículo, na ordem exata das paradas. "
            "Destaque as entregas críticas e os pontos sem rota."
        )
    elif task == "report":
        instruction = (
            "Gere um relatório operacional com número de rotas, paradas, carga e distância total. "
            "Compare com o baseline apenas se ele estiver presente e houver cobertura equivalente. "
            "Informe os pontos não roteados."
        )
    elif task == "ask":
        if not question or not question.strip():
            raise ValueError("A nonempty question is required for task 'ask'")
        instruction = f"Responda à pergunta: {question.strip()}"
    else:
        raise ValueError(f"Unknown task: {task}")
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Dados reais da solução:\n{solution_context(solution, baseline_distance)}\n\n{instruction}"},
    ]
