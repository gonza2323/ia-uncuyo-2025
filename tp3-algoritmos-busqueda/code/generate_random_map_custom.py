import random


# Exploración del entorno
# 4.c. Arme una nueva función generate_random_map_custom que permita definir el tamaño de
# la grilla, la probabilidad que una casilla sea de hielo, y ubique de forma aleatoria la posición
# inicial del agente y del objetivo (el entorno creado a partir de dicha función podría no tener
# solución).

def generate_random_map_custom(size=8, p=0.8, seed=None):
    rng = random.Random(seed)
    
    # generamos el mapa con la probabilidad especificada
    grid = []
    for _ in range(size):
        row = ['F' if rng.random() < p else 'H' for _ in range(size)]
        grid.append(row)
    
    # colocamos aleatoriamente la posición inicial y la del objetivo
    all_positions = [(i, j) for i in range(size) for j in range(size)]
    s_pos = rng.choice(all_positions)
    all_positions.remove(s_pos)
    g_pos = rng.choice(all_positions)
    
    grid[s_pos[0]][s_pos[1]] = 'S'
    grid[g_pos[0]][g_pos[1]] = 'G'
    
    return [''.join(row) for row in grid]
