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


def solution_context(
    solution: Solution, baseline_distance: float | None = None, detail: str = "full"
) -> str:
    critical_stops = [
        {"vehicle_id": route.vehicle.id, "order": index, "id": point.id}
        for route in solution.routes
        for index, point in enumerate(route.points, 1)
        if point.priority.value == "critical"
    ]
    if detail == "critical":
        return json.dumps({"critical_stops": critical_stops}, ensure_ascii=False, indent=2)

    data = {
        "distance_unit": "unidades de coordenada (distância euclidiana em lat/lon)",
        "total_distance": round(solution.total_distance, 6),
        "route_count": len(solution.routes),
        "total_stops": sum(len(route.points) for route in solution.routes),
        "total_load": round(sum(route.load for route in solution.routes), 2),
        "critical_stops": critical_stops,
        "routes": [
            {
                "vehicle_id": route.vehicle.id,
                "capacity": route.vehicle.capacity,
                "load": round(route.load, 2),
                "max_range": route.vehicle.max_range,
                "distance": round(route.distance, 6),
                "stop_count": len(route.points),
                **(
                    {
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
                        ]
                    }
                    if detail == "full"
                    else {}
                ),
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
            "Destaque as entregas críticas e os pontos sem rota. "
            "Copie os IDs, demandas e prioridades sem alterar os dados."
        )
        detail = "full"
    elif task == "report":
        instruction = (
            "Gere um relatório operacional usando os campos route_count, total_stops, "
            "total_load, total_distance e o stop_count de cada veículo exatamente como fornecidos. "
            "Não estime uma distribuição igual de paradas entre veículos. "
            "Compare com o baseline apenas se ele estiver presente e houver cobertura equivalente. "
            "Informe explicitamente a quantidade de pontos não roteados. "
            "Arredonde números para no máximo duas casas decimais, salvo distâncias."
        )
        detail = "summary"
    elif task == "ask":
        if not question or not question.strip():
            raise ValueError("A nonempty question is required for task 'ask'")
        is_critical_question = "crític" in question.casefold() or "critic" in question.casefold()
        detail = "critical" if is_critical_question else "full"
        instruction = f"Responda à pergunta: {question.strip()}"
        if is_critical_question:
            instruction += (
                " Use somente a lista critical_stops: informe todos os IDs, o veículo e a ordem "
                "de cada parada. Não inclua pontos regulares."
            )
    else:
        raise ValueError(f"Unknown task: {task}")
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Dados reais da solução:\n{solution_context(solution, baseline_distance, detail)}\n\n{instruction}"},
    ]
