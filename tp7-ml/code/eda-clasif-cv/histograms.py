import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

os.makedirs("plots", exist_ok=True)

train_df = pd.read_csv("data/arbolado-mendoza-dataset-train.csv")

bins_list = [10, 20, 30, 50]

# 3. a) Histograma de circ_tronco_cm
for bins in bins_list:
    plt.figure(figsize=(8,5))
    sns.histplot(train_df["circ_tronco_cm"].dropna(), bins=bins, kde=False)
    plt.title(f"Histograma de circ_tronco_cm ({bins} bins)")
    plt.xlabel("circ_tronco_cm")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.savefig(f"plots/hist_circ_tronco_cm_{bins}bins.png")
    plt.close()

# 3. b) Histograma circ_tronco_cm por inclinación peligrosa
for bins in bins_list:
    plt.figure(figsize=(8,5))
    sns.histplot(data=train_df, x="circ_tronco_cm", hue="inclinacion_peligrosa", bins=bins, kde=False)
    plt.title(f"Histograma de circ_tronco_cm por inclinacion_peligrosa ({bins} bins)")
    plt.xlabel("circ_tronco_cm")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.savefig(f"plots/hist_circ_tronco_cm_por_inclinacion_{bins}bins.png")
    plt.close()
