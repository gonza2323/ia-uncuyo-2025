import os
import pandas as pd


os.makedirs("data", exist_ok=True)

train_df = pd.read_csv("data/arbolado-mendoza-dataset-train.csv")


# 3. c) Crear variable categórica circ_tronco_cm_cat

quantiles = train_df["circ_tronco_cm"].quantile([0.25, 0.5, 0.75])
q1, q2, q3 = quantiles[0.25], quantiles[0.5], quantiles[0.75]

def categorizar_circ(valor):
    if pd.isna(valor):
        return None
    elif valor <= q1:
        return "bajo"
    elif valor <= q2:
        return "medio"
    elif valor <= q3:
        return "alto"
    else:
        return "muy alto"

train_df["circ_tronco_cm_cat"] = train_df["circ_tronco_cm"].apply(categorizar_circ)

# Guardar nuevo dataset
train_df.to_csv("data/arbolado-mendoza-dataset-circ_tronco_cm-train.csv", index=False)
