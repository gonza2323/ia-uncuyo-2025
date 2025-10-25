import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import ast

df = pd.read_csv("results/tp5-Nreinas.csv")

os.makedirs("plots", exist_ok=True)
os.makedirs("results", exist_ok=True)

algorithm_order = ["Random", "HC", "SA", "GA", "CSP-BT", "CSP-FC"]

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

# Guardar tablas a .md
win_table.to_markdown("results/table_win_rate.md")
h_table.to_markdown("results/table_H.md")
time_table.to_markdown("results/table_time.md")
states_table.to_markdown("results/table_states.md")


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
