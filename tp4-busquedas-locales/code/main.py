import os
import pandas as pd
from algoritmos import *

NO_TESTS = 50

algorithms = [
    RandomAlgorithm(),
    HillClimbing(),
    SimulatedAnnealing(),
    GeneticAlgorithm()
]

board_sizes = [4, 8, 10, 12, 15]

seeds = range(NO_TESTS)

total_tests = NO_TESTS * len(board_sizes) * len(algorithms)


# Ejecutar pruebas

results = []
test_no = 0
for algorithm in algorithms:
    for size in board_sizes:
        for seed in seeds:
            print(f"{(test_no / total_tests) * 100:.1f}% done. Testing algorithm: {algorithm.get_name()}, size = {size}, seed = {seed}")
            result = algorithm.run(env_n=seed, size=size)
            results.append(result)
            test_no += 1

print(f"Completed all ({total_tests}) tests")


# Guardar .csv

os.makedirs("results", exist_ok=True)
df = pd.DataFrame(results)

path = "results/tp4-Nreinas-full.csv"
df.to_csv(path, index=False)
print(f"Saved full results to tp4-Nreinas-full.csv")

path = "results/tp4-Nreinas.csv"
df.drop(columns=["best_h_per_iter"]).to_csv(path, index=False)
print(f"Saved results to tp4-Nreinas.csv")
