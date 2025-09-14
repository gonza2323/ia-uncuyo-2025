import algoritmos
from environment import *
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import gymnasium as gym
import os


# --- CONFIGURACIÓN ---
NO_TESTS = 100
ENV_SIZE = 100
FROZEN_PROB = 0.92
MAX_ACTIONS = 1000
SEED = 42
SHOW_VISUALIZATION = False

ACTION_MAP = {
    (0, 1): 2,  # derecha
    (-1, 0): 3, # arriba
    (0, -1): 0, # izquierda
    (1, 0): 1  # abajo
}


# --- DEFINICIONES DE COSTO Y HEURÍSTICAS ---
def cost_fn_scenario_1(_):
    return 1

def cost_fn_scenario_2(move):
    return 1 if move.y == 0 else 10

def heuristic_selector(cost_fn):
    if cost_fn == cost_fn_scenario_1:
        return lambda pos1, pos2: pos1.manhattan_distance(pos2)
    elif cost_fn == cost_fn_scenario_2:
        return lambda pos1, pos2: abs(pos1.y - pos2.y) * 10 + abs(pos1.x - pos2.x)
    else:
        return lambda pos1, pos2: pos1.manhattan_distance(pos2)


# --- LISTAS DE ESCENARIOS Y ALGORITMOS ---
scenarios = [
    {'number': 1, 'cost_fn': cost_fn_scenario_1},
    {'number': 2, 'cost_fn': cost_fn_scenario_2},
]

algorithms = [
    algoritmos.RandomSearch(),
    algoritmos.BFS(),
    algoritmos.DFS(),
    algoritmos.DFS("DLS-50", depth_limit=50),
    algoritmos.DFS("DLS-75", depth_limit=75),
    algoritmos.DFS("DLS-100", depth_limit=100),
    algoritmos.UCS(),
    algoritmos.AStar(heuristic_selector=heuristic_selector)
]


# --- GENERACIÓN Y GUARDADO DE ENTORNOS ---
print("Generando entornos...")
environments = generate_random_maps(NO_TESTS, ENV_SIZE, FROZEN_PROB, SEED)
environment_grids = [Grid(env) for env in environments]

env_data = [{'env_n': i + 1, 'grid': str(env)} for i, env in enumerate(environment_grids)]
pd.DataFrame(env_data).to_csv('environments.csv', index=False)
print(f"{len(environment_grids)} entornos guardados en 'environments.csv'")


# --- EJECUCIÓN PRINCIPAL ---
results_list = []

def main():
    print("\nIniciando evaluación de algoritmos...")
    total_runs = len(algorithms) * len(environment_grids) * len(scenarios)
    current_run = 0

    for algo in algorithms:
        for i, env in enumerate(environment_grids):
            gym_env = None
            if (SHOW_VISUALIZATION):
                gym_env = gym.make(
                        'FrozenLake-v1',
                        desc=environments[i],
                        render_mode='human' if SHOW_VISUALIZATION else None,
                        is_slippery=False
                    )

            for scenario in scenarios:
                current_run += 1
                print(f"  Ejecutando ({current_run}/{total_runs}): Algoritmo='{algo._name}', Entorno={i+1}, Escenario={scenario['number']}")
                
                # Ejecutamos el algoritmo y guardamos los resultados
                result = algo.run(env, scenario['cost_fn'], MAX_ACTIONS)
                result['env_n'] = i + 1
                result['scenario_n'] = scenario['number']
                results_list.append(result)

                # Mostramos la simulación si está activada la opción
                if SHOW_VISUALIZATION and result['solution_found'] and result['actions']:
                    print(f" Mostrando visualización para el algoritmo {algo._name} en el entorno {i+1}, escenario {scenario['number']}...")
                    
                    gym_env.reset()
                    gym_env.render()
                    
                    for action in result['actions']:
                        gym_action = ACTION_MAP.get((action.y, action.x))
                        if gym_action is not None:
                            gym_env.step(gym_action)
                            gym_env.render()
                    
            if (SHOW_VISUALIZATION):
                gym_env.close()
    
    print("\nEvaluación completada.")
    print(f"Se realizaron {len(algorithms)} x {len(environment_grids)} x {len(scenarios)} = {total_runs} pruebas")


def format_mean_std(df_grouped, numeric_cols):
    formatted = pd.DataFrame(index=df_grouped.index.get_level_values('algorithm_name').unique())
    
    for metric in numeric_cols:
        mean_cols = df_grouped[(metric, 'mean')]
        std_cols = df_grouped[(metric, 'std')]

        for scenario in df_grouped.index.get_level_values('scenario_n').unique():
            mask = df_grouped.index.get_level_values('scenario_n') == scenario
            values = [f"{mean:.2f}±{std:.2f}" for mean, std in zip(mean_cols[mask], std_cols[mask])]
            formatted[(metric, f"scenario {scenario}")] = pd.Series(values, index=formatted.index)
    
    formatted.columns = pd.MultiIndex.from_tuples(formatted.columns)
    return formatted


def plot_boxplots(df, metrics_to_plot, file_suffix, label_suffix):
    sns.set_theme(style="whitegrid")
    for metric_col, title in metrics_to_plot.items():
        plt.figure(figsize=(16, 8))
        ax = sns.boxplot(
            data=df,
            x='algorithm_name',
            y=metric_col,
            hue='scenario_n',
            palette='Set2'
        )
        plt.title(f'Distribución de "{title}" por Algoritmo y Escenario ({label_suffix})', fontsize=16)
        plt.xlabel('Algoritmo', fontsize=12)
        plt.ylabel(title, fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        if df[metric_col].max() > 900:
            ax.set_yscale('log')
            plt.ylabel(f'{title} (escala logarítmica)', fontsize=12)

        os.makedirs("images", exist_ok=True)
        file_name = f"images/boxplot_{metric_col}_{file_suffix}.png"
        plt.savefig(file_name)
        print(f"  - Gráfico '{file_name}' guardado.")
        plt.close()


if __name__ == '__main__':
    main()

    # --- Data preparation ---
    results_df = pd.DataFrame(results_list)
    column_order = [
        'algorithm_name', 'env_n', 'scenario_n', 'states_n',
        'actions_count', 'actions_cost', 'time', 'solution_found'
    ]
    results_df = results_df[column_order]
    df_no_random = results_df[results_df['algorithm_name'] != 'Random']

    numeric_cols = ['states_n', 'actions_count', 'actions_cost', 'time']

    
    # --- Success-only stats ---
    successful_runs_df = df_no_random[df_no_random['solution_found']].copy()
    successful_runs_df[numeric_cols] = successful_runs_df[numeric_cols].apply(pd.to_numeric)
    stats_success = successful_runs_df.groupby(['algorithm_name', 'scenario_n'])[numeric_cols].agg(['mean', 'std'])
    stats_success.fillna(0, inplace=True)

    table_success = format_mean_std(stats_success, numeric_cols)
    print("\n--- Estadísticas de pruebas exitosas (mean±std) ---")
    print(table_success)

    
    # --- All-success stats (excluding Random) ---
    df_all_success = (
        df_no_random
        .groupby(['env_n', 'scenario_n'])['solution_found']
        .all()
        .reset_index()
    )
    df_all_success = df_no_random.merge(
        df_all_success[df_all_success['solution_found']], 
        on=['env_n', 'scenario_n']
    )

    print(f"\nUn total de {len(df_all_success)} pruebas fueron completadas por todos los algoritmos (excepto Random)")
    stats_all_success = df_all_success.groupby(['algorithm_name', 'scenario_n'])[numeric_cols].agg(['mean', 'std'])
    stats_all_success.fillna(0, inplace=True)

    table_all_success = format_mean_std(stats_all_success, numeric_cols)
    print("\n--- Estadísticas de pruebas completadas por todos los algoritmos (mean±std) ---")
    print(table_all_success)

    
    # --- GENERACIÓN DE GRÁFICOS ---

    print("\nGenerando gráficos...\n")

    metrics_to_plot = {
        'states_n': 'Cantidad de Estados Explorados',
        'actions_count': 'Cantidad de Acciones',
        'actions_cost': 'Costo Total de Acciones',
        'time': 'Tiempo Empleado (segundos)'
    }

    
    plot_boxplots(successful_runs_df, metrics_to_plot, "success_only", "solo pruebas exitosas")
    plot_boxplots(df_all_success, metrics_to_plot, "all_success", "solo pruebas completadas por todos los agentes")

    print("\nVisualizaciones guardadas correctamente.")

