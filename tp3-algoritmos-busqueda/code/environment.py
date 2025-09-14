from generate_random_map_custom import *
from algoritmos import Grid, AStar


def map_has_solution(grid: Grid):
    solver = AStar()
    result = solver.run(grid)
    return result['solution_found']


def generate_random_maps(no_tests, env_size, frozen_p, initial_seed):
    environments = []
    seed = initial_seed
    for _ in range(no_tests):
        env = generate_random_map_custom(env_size, frozen_p, seed)
        grid = Grid(env)
        seed += 1
        while not map_has_solution(grid):
            print(f'Map with seed {seed} is unsolvable, retrying...')
            env = generate_random_map_custom(env_size, frozen_p, seed)
            grid = Grid(env)
            seed += 1
        environments.append(env)
        
    return environments
