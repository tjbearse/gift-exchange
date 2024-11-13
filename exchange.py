from dataclasses import dataclass
from itertools import combinations
from ortools.linear_solver import pywraplp
import json


@dataclass
class ExchangeInfo:
    people: list[str]
    exclude: list[list[int]]  # list of groups by index
    # list of years, year is a list of giving pairs by index
    previous: list[list[tuple[int, int]]]


def main():
    exchange = loadExchange('config.json')
    # Data
    # giver, receiver
    costs = calcCosts(exchange.previous, len(
        exchange.people), exponentialPenalty)
    num_workers = len(costs)
    num_tasks = len(costs[0])
    assert (num_workers == num_tasks)

    # Solver
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        return

    # Variables
    # x[i, j] is an array of 0-1 variables, which will be 1
    # if worker i is assigned to task j.
    x = {}
    for i in range(num_workers):
        for j in range(num_tasks):
            x[i, j] = solver.IntVar(0, 1, "")

    # Constraints
    # Each worker is assigned to at most 1 task.
    for i in range(num_workers):
        solver.Add(solver.Sum([x[i, j] for j in range(num_tasks)]) <= 1)

    # Each task is assigned to exactly one worker.
    for j in range(num_tasks):
        solver.Add(solver.Sum([x[i, j] for i in range(num_workers)]) == 1)

    # No one can gift for themselves
    for i in range(num_workers):
        solver.Add(x[i, i] == 0)
    # No one can gift to their partner
    for group in exchange.exclude:
        for i, j in combinations(group, 2):
            solver.Add(x[i, j] == 0)
            solver.Add(x[j, i] == 0)

    # Objective
    objective_terms = []
    for i in range(num_workers):
        for j in range(num_tasks):
            objective_terms.append(costs[i][j] * x[i, j])
    solver.Minimize(solver.Sum(objective_terms))

    # Solve
    status = solver.Solve()

    # Print solution.
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f"Total cost = {solver.Objective().Value()}\n")
        nextExchangeConfig = {}
        for i in range(num_workers):
            for j in range(num_tasks):
                # Test if x[i,j] is 1 (with tolerance for floating point arithmetic).
                if x[i, j].solution_value() > 0.5:
                    nextExchangeConfig[exchange.people[i]] = exchange.people[j]
                    print(f"{exchange.people[i]} -> {exchange.people[j]}" +
                          f" (cost: {costs[i][j]})")
        print(nextExchangeConfig)
    else:
        print("No solution found.")


def linearPenalty(years, n):
    return n - years


def exponentialPenalty(years, n):
    return 2 ** (n - (years + 1))


def calcCosts(prev, n, penaltyFn):
    costs = [[0 for _ in range(n)] for __ in range(n)]
    # should this be limited to a full cycle of years?
    for yearNum, year in enumerate(reversed(prev)):
        penalty = penaltyFn(yearNum, len(prev))
        for (giver, receiver) in year:
            costs[giver][receiver] += penalty
    return costs


def loadExchange(fileName):
    with open('config.json', 'r') as f:
        data = json.load(f)
    people: list[str] = data['currentExchange']
    partners: list[list[str]] = data['exclusionGroups']
    previous: list[dict[str, str]] = data['previous']

    partnerIndexes = [
        list(map(people.index, filter(lambda p: p in people, group)))
        for group in partners
    ]
    previousIndexes = [
        [
            (people.index(a), people.index(b))
            for a, b in year.items()
            if a in people and b in people
        ]
        for year in previous
    ]
    return ExchangeInfo(people, partnerIndexes, previousIndexes)


if __name__ == "__main__":
    main()
