import os
import pandas as pd
from sklearn.model_selection import train_test_split

os.makedirs("data", exist_ok=True)

# 1. Dividir datos

data = pd.read_csv("data/arbolado-mendoza-dataset.csv")
train_df, val_df = train_test_split(data, test_size=0.2, random_state=42, shuffle=True)

train_df.to_csv("data/arbolado-mendoza-dataset-train.csv", index=False)
val_df.to_csv("data/arbolado-mendoza-dataset-validation.csv", index=False)
