from gymnasium import wrappers
from gymnasium.envs.toy_text.frozen_lake import generate_random_map
from generate_random_map_custom import *


# 1. Instalar la biblioteca y crear el entorno por defecto:

import gymnasium as gym
env = gym.make('FrozenLake-v1', render_mode='human')


# 4. Modificar el entorno

# 4.a La función make tiene como argumento is_slippery. Si el mismo es
# True, entonces existe una probabilidad de que el agente se mueva en
# una dirección perpendicular a la deseada. Su valor por defecto es True.

# 4.b Generación de mapas

# Mapas precargados
env = gym.make('FrozenLake-v1', desc=None, map_name="4x4", render_mode='human')
    # tamaño: 4x4
    # cant. de agujeros: 4
    # pos. inicial: (0, 0)
    # pos. objetivo: (3, 3)

# Mapa a partir de una lista
desc=["SFFF", "FHFH", "FFFH", "HFFG"]
env = gym.make('FrozenLake-v1', desc=desc, render_mode='human')
    # tamaño: 4x4
    # cant. de agujeros: 4
    # pos. inicial: (0, 0)
    # pos. objetivo: (3, 3)

# Mapa a partir de una función aleatoria
env = gym.make('FrozenLake-v1', desc=generate_random_map(size=8), render_mode='human')
    # tamaño: 8x8
    # cant. de agujeros: variable, pero en promedio será (8x8-2)*(1-0.8) = 12,4
    # pos. inicial: (0, 0)
    # pos. objetivo: (3, 3)

# 4.c. Función generate_random_map_custom definida en generate_random_map_custom.py
desc = generate_random_map_custom(size=8, p=0.8, seed=42)
env = gym.make('FrozenLake-v1', desc=desc, render_mode='human')


# 5. Modificar la vida del agente

nuevo_limite = 10
env = wrappers.TimeLimit(env, nuevo_limite)


# 2. Obtener información del entorno:

print("Número de estados:", env.observation_space.n)
print("Número de acciones:", env.action_space.n)


# 3. Ejecutar un episodio básico

state = env.reset()
print("Posición inicial del agente:", state[0])
done = truncated = False
i=0
while not (done or truncated):
    action = env.action_space.sample()
    i+=1
    
    next_state, reward, done, truncated, _ = env.step(action)
    print(f"Acción: {action}, Nuevo estado: {next_state}, Recompensa: {reward}")
    if not reward == 1.0:
        print(f"¿Ganó? (encontró el objetivo): False")
        print(f"¿Perdió? (se cayó): {done}")
        print(f"¿Frenó? (alcanzó el máximo de pasos posible): {truncated}\n")
    else:
        print(f"¿Ganó? (encontró el objetivo): {done}")
    state = next_state
