import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

os.makedirs("plots", exist_ok=True)

train_df = pd.read_csv("data/arbolado-mendoza-dataset-train.csv")


# 2. a) Distribución de la clase inclinacion_peligrosa

abs_counts = train_df["inclinacion_peligrosa"].value_counts().sort_index()
rel_counts = train_df["inclinacion_peligrosa"].value_counts(normalize=True).sort_index()

print("Distribución de 'inclinacion_peligrosa':")
print("Frecuencia absoluta:")
print(abs_counts)
print("\nFrecuencia relativa:")
print(rel_counts.round(4))
print("\n-----------------------------\n")

# Frecuencia absoluta
plt.figure(figsize=(6,4))
sns.countplot(data=train_df, x="inclinacion_peligrosa")
plt.title("Distribución de la variable 'inclinacion_peligrosa'")
plt.xlabel("inclinacion_peligrosa")
plt.ylabel("Frecuencia")
plt.tight_layout()
plt.savefig("plots/distribucion_inclinacion_peligrosa_absoluta.png")
plt.close()

# Frecuencia relativa
plt.figure(figsize=(6,4))
(train_df["inclinacion_peligrosa"]
 .value_counts(normalize=True)
 .sort_index()
 .plot(kind="bar"))
plt.title("Distribución relativa de 'inclinacion_peligrosa'")
plt.xlabel("inclinacion_peligrosa")
plt.ylabel("Proporción")
plt.tight_layout()
plt.savefig("plots/distribucion_inclinacion_peligrosa_relativa.png")
plt.close()


# 2. b) Secciones más peligrosas

# Frecuencia absoluta inclinaciones peligrosas
seccion_abs = train_df.groupby("seccion")["inclinacion_peligrosa"].sum().sort_values(ascending=False)
seccion_abs.plot(kind="bar", figsize=(10,5))
plt.title("Frecuencia absoluta de árboles peligrosos por sección")
plt.xlabel("Sección")
plt.ylabel("Cantidad de árboles peligrosos")
plt.tight_layout()
plt.savefig("plots/seccion_peligrosa_absoluta.png")
plt.close()

# Frecuencia relativa inclinaciones peligrosas
seccion_rel = train_df.groupby("seccion")["inclinacion_peligrosa"].mean().sort_values(ascending=False)
seccion_rel.plot(kind="bar", figsize=(10,5))
plt.title("Proporción de árboles peligrosos por sección")
plt.xlabel("Sección")
plt.ylabel("Proporción de árboles peligrosos")
plt.tight_layout()
plt.savefig("plots/seccion_peligrosa_relativa.png")
plt.close()


# 2. c) Especies más peligrosas

top_species = train_df["especie"].value_counts().head(10).index
subset = train_df[train_df["especie"].isin(top_species)]

# Frecuencia relativa
especie_rel = subset.groupby("especie")["inclinacion_peligrosa"].mean().sort_values(ascending=False)
especie_rel.plot(kind="bar", figsize=(12,6))
plt.title("Proporción de árboles peligrosos por especie (top 10)")
plt.xlabel("Especie")
plt.ylabel("Proporción de árboles peligrosos")
plt.tight_layout()
plt.savefig("plots/especie_peligrosa_relativa.png")
plt.close()
