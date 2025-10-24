import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import ast

df = pd.read_csv("results/tp4-Nreinas-full.csv")

os.makedirs("plots", exist_ok=True)
os.makedirs("results", exist_ok=True)

algorithm_order = ["random", "hill_climbing", "simulated_annealing", "genetic_algorithm"]

df["algorithm_name"] = pd.Categorical(df["algorithm_name"], categories=algorithm_order, ordered=True)


# 1. ESTADÍSTICAS POR ALGORITMO Y TAMAÑO DE TABLERO

grouped = df.groupby(["algorithm_name", "size"], observed=False)

summary = grouped.agg({
    "success": ["mean", "std"],
    "H": ["mean", "std"],
    "states": ["mean", "std"],
    "time": ["mean", "std"]
})

# Columnas
summary.columns = ["WinRate", "WinStd", "H_mean", "H_std", "States_mean", "States_std", "Time_mean", "Time_std"]
summary = summary.reset_index()

# Tablas para cada métrica
def format_mean_std(mean, std):
    return f"{mean:.3f} ± {std:.3f}"

def pivot_metric(mean_col, std_col):
    pivot_mean = summary.pivot(index="algorithm_name", columns="size", values=mean_col)
    pivot_std = summary.pivot(index="algorithm_name", columns="size", values=std_col)
    combined = pivot_mean.copy()
    for col in pivot_mean.columns:
        combined[col] = [format_mean_std(m, s) for m, s in zip(pivot_mean[col], pivot_std[col])]
    return combined

# Tablas
win_table = summary.pivot(index="algorithm_name", columns="size", values="WinRate") * 100
h_table = pivot_metric("H_mean", "H_std")
time_table = pivot_metric("Time_mean", "Time_std")
states_table = pivot_metric("States_mean", "States_std")

# Guardar tablas a .csv
win_table.to_csv("results/table_win_rate.csv")
h_table.to_csv("results/table_H.csv")
time_table.to_csv("results/table_time.csv")
states_table.to_csv("results/table_states.csv")


# BOXPLOTS

metrics_box = {"H": "H value", "time": "Execution time (s)", "states": "Explored states"}
metrics_bar = {"success": "Success (%)"}

# Boxplots
for metric, label in metrics_box.items():
    for size in df["size"].unique():
        subset = df[df["size"] == size].copy()
        plt.figure()
        subset.boxplot(column=metric, by="algorithm_name", grid=False)
        plt.title(f"{label} - Board size {size}")
        plt.suptitle("")
        plt.xlabel("Algorithm")
        plt.ylabel(label)
        plt.tight_layout()
        filename = f"plots/{metric}_size{size}.png"
        plt.savefig(filename)
        plt.close()

# Para la tasa de éxito, bar plots
for size in df["size"].unique():
    subset = df[df["size"] == size].copy()
    win_rates = []
    win_std = []
    for alg in algorithm_order:
        data = subset[subset["algorithm_name"] == alg]["success"]
        p = data.mean()
        std = data.std()  # sample std
        win_rates.append(p*100)
        win_std.append(std*100)
    
    plt.figure()
    plt.bar(algorithm_order, win_rates, yerr=win_std, capsize=5)
    plt.title(f"Win rate - Board size {size}")
    plt.ylabel("Win rate (%)")
    plt.xlabel("Algorithm")
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(f"plots/win_rate_size{size}.png")
    plt.close()


# CURVAS H()

sizes_for_ht = sorted(df["size"].unique())

for size in sizes_for_ht:
    plt.figure()
    for alg in algorithm_order:
        subset = df[(df["algorithm_name"] == alg) & (df["size"] == size)]
        curves = [ast.literal_eval(r) if isinstance(r, str) else r for r in subset["best_h_per_iter"]]
        curves = [c for c in curves if len(c) > 0]
        if not curves:
            continue
        
        max_len = max(len(c) for c in curves)
        arr = np.full((len(curves), max_len), np.nan)
        for i, c in enumerate(curves):
            arr[i, :len(c)] = c
        
        mean_curve = np.nanmean(arr, axis=0)
        std_curve = np.nanstd(arr, axis=0)
        
        plt.xscale("log")
        plt.plot(mean_curve, label=alg)
        plt.fill_between(range(max_len), mean_curve - std_curve, mean_curve + std_curve, alpha=0.2)
    
    plt.title(f"H(t) - Board size {size}")
    plt.xlabel("Iteration")
    plt.ylabel("H")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"plots/Ht_size{size}.png")
    plt.close()