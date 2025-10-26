# ============================================================
# Pipeline completo para Kaggle - Arbolado Mendoza
# ============================================================

import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import os

# Crear carpetas si no existen
os.makedirs("data", exist_ok=True)
os.makedirs("output", exist_ok=True)

# ============================================================
# 1. Cargar datos
# ============================================================
train = pd.read_csv("data/arbolado-mza-dataset.csv")
test = pd.read_csv("data/arbolado-mza-dataset-test.csv")
test_ids = test["id"].copy()

# ============================================================
# 2. Preprocesamiento y feature engineering
# ============================================================

# Columnas irrelevantes
drop_cols = ["id", "ultima_modificacion", "nombre_seccion"]
train = train.drop(columns=drop_cols)
test = test.drop(columns=drop_cols)

# ------------------------
# Mapear altura y diametro_tronco a valores numéricos
# ------------------------
altura_map = {
    "Muy bajo (1 - 2 mts)": 1.5,
    "Bajo (2 - 4 mts)": 3,
    "Medio (4 - 8 mts)": 6,
    "Alto (> 8 mts)": 9
}
train["altura"] = train["altura"].map(altura_map)
test["altura"] = test["altura"].map(altura_map)

diam_map = {
    "Muy bajo (< 20 cm)": 10,
    "Bajo (20 - 40 cm)": 30,
    "Medio (40 - 60 cm)": 50,
    "Alto (> 60 cm)": 70
}
train["diametro_tronco"] = train["diametro_tronco"].map(diam_map)
test["diametro_tronco"] = test["diametro_tronco"].map(diam_map)

# ------------------------
# Codificar variables categóricas restantes
# ------------------------
cat_cols = ["especie", "seccion"]
for col in cat_cols:
    le = LabelEncoder()
    train[col] = le.fit_transform(train[col].astype(str))
    # manejar categorías nuevas en test
    test[col] = test[col].map(lambda x: x if x in le.classes_ else "NA")
    le_classes = np.append(le.classes_, "NA")
    le.classes_ = le_classes
    test[col] = le.transform(test[col].astype(str))

# ------------------------
# Features adicionales
# ------------------------
# Ejemplos simples que pueden mejorar XGBoost:
train["circ_altura_ratio"] = train["circ_tronco_cm"] / (train["altura"] + 0.01)
test["circ_altura_ratio"] = test["circ_tronco_cm"] / (test["altura"] + 0.01)

train["diam_circ_ratio"] = train["diametro_tronco"] / (train["circ_tronco_cm"] + 0.01)
test["diam_circ_ratio"] = test["diametro_tronco"] / (test["circ_tronco_cm"] + 0.01)

# ============================================================
# 3. Separar características y variable objetivo
# ============================================================
y = train["inclinacion_peligrosa"]
X = train.drop(columns=["inclinacion_peligrosa"])

# ============================================================
# 4. K-Fold Stratified CV
# ============================================================
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
auc_scores = []

for fold, (train_idx, val_idx) in enumerate(kf.split(X, y), 1):
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
    
    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=(y_train==0).sum()/(y_train==1).sum(),
        eval_metric="auc",
        random_state=42,
    )
    
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    y_pred_prob = model.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, y_pred_prob)
    auc_scores.append(auc)
    print(f"Fold {fold} AUC: {auc:.4f}")

print(f"\nMean AUC: {np.mean(auc_scores):.4f} ± {np.std(auc_scores):.4f}")

# ============================================================
# 5. Entrenar modelo final sobre todo el train set
# ============================================================
final_model = xgb.XGBClassifier(
    n_estimators=500,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=(y==0).sum()/(y==1).sum(),
    eval_metric="auc",
    random_state=42,
)

final_model.fit(X, y)

# ============================================================
# 6. Predicciones sobre test.csv
# ============================================================
test_pred_prob = final_model.predict_proba(test)[:, 1]
# Threshold óptimo para AUC suele estar alrededor de 0.5
test_pred_class = (test_pred_prob >= 0.5).astype(int)

submission = pd.DataFrame({
    "ID": test_ids,
    "inclinacion_peligrosa": test_pred_class
})

submission.to_csv("output/submission.csv", index=False)
print("\nArchivo de submission generado en 'output/submission.csv'")