"""Save the genetic algorithm's best fitness by generation as a PNG."""

from __future__ import annotations

from pathlib import Path


def save_convergence(history: list[float], output: str | Path) -> Path:
    if not history:
        raise ValueError("Fitness history is empty")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(9, 5))
    axis.plot(range(1, len(history) + 1), history, color="#1769aa", linewidth=2)
    axis.set(title="Convergência do algoritmo genético", xlabel="Geração", ylabel="Fitness (menor é melhor)")
    axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(output, dpi=160)
    plt.close(figure)
    return output
