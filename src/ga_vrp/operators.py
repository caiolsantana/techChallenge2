"""Genetic operators for the VRP chromosome.

The chromosome is a "giant tour": a single permutation of every `DeliveryPoint`, with no
vehicle/route markers. `split.split_into_routes()` is what turns a chromosome into actual
vehicle routes — these operators only ever see/produce flat permutations, so they are a
direct, typed port of `base_code/genetic_algorithm.py` (`order_crossover`, `mutate`), adapted
from `Tuple[float, float]` city points to `DeliveryPoint`. The FIAP base_code/ files are left
untouched as a reference; this module is the VRP-adapted copy.
"""

from __future__ import annotations

import random

from .models import DeliveryPoint


def generate_random_population(
    delivery_points: list[DeliveryPoint], population_size: int
) -> list[list[DeliveryPoint]]:
   
    return [random.sample(delivery_points, len(delivery_points)) for _ in range(population_size)]


def order_crossover(
    parent1: list[DeliveryPoint], parent2: list[DeliveryPoint]
) -> list[DeliveryPoint]:
   
    length = len(parent1)
    start_index = random.randint(0, length - 1)
    end_index = random.randint(start_index + 1, length)

    child = parent1[start_index:end_index]

    remaining_positions = [i for i in range(length) if i < start_index or i >= end_index]
    remaining_genes = [gene for gene in parent2 if gene not in child]

    for position, gene in zip(remaining_positions, remaining_genes):
        child.insert(position, gene)

    return child


def swap_mutate(
    individual: list[DeliveryPoint], mutation_probability: float
) -> list[DeliveryPoint]:
   
    mutated = list(individual)

    if random.random() < mutation_probability and len(mutated) >= 2:
        index = random.randint(0, len(mutated) - 2)
        mutated[index], mutated[index + 1] = mutated[index + 1], mutated[index]

    return mutated


def inversion_mutate(
    individual: list[DeliveryPoint], mutation_probability: float
) -> list[DeliveryPoint]:
   
    mutated = list(individual)

    if random.random() < mutation_probability and len(mutated) >= 2:
        i, j = sorted(random.sample(range(len(mutated)), 2))
        mutated[i : j + 1] = reversed(mutated[i : j + 1])

    return mutated


def roulette_wheel_selection(
    population: list[list[DeliveryPoint]], fitness_values: list[float], k: int
) -> list[list[DeliveryPoint]]:
    
    weights = [1.0 / max(value, 1e-9) for value in fitness_values]
    return random.choices(population, weights=weights, k=k)
