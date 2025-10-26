# Trabajo Práctico 7B: Machine Learning


## Parte 2


### Preprocesamiento

* Eliminación de variables irrelevantes

    * Columnas eliminadas: id, ultima_modificacion, nombre_seccion.

    * Estas columnas no aportan información predictiva sobre la inclinación peligrosa.

* Mapeo de variables categóricas ordinales a numéricas

    * altura: convertida de categorías (Muy bajo (1-2 mts), Bajo (2-4 mts), etc.) a valores numéricos aproximados (1.5, 3, 6, 9).

    * diametro_tronco: convertida de categorías (Muy bajo (<20 cm), Bajo (20-40 cm), etc.) a valores numéricos (10, 30, 50, 70).

* Codificación de variables categóricas nominales

    * especie y sección fueron transformadas con LabelEncoder para que XGBoost pueda interpretarlas.

* Creación de features derivadas

    * circ_altura_ratio = circ_tronco_cm / altura → relación entre grosor y altura.

    * diam_circ_ratio = diametro_tronco / circ_tronco_cm → relación diámetro/circunferencia.


### Resultados sobre el conjunto de validación

Se realizó validación cruzada estratificada de 5 folds sobre el set de entrenamiento.

Métricas obtenidas (AUC por fold):

| Fold | AUC    |
| ---- | ------ |
| 1    | 0.7863 |
| 2    | 0.7726 |
| 3    | 0.7670 |
| 4    | 0.7766 |
| 5    | 0.7711 |

AUC promedio: 0.7747 ± 0.0065


### Resultados obtenidos en Kaggle

Se obtuvo un AUC en Kaggle de 0.70950, casi 7 puntos menos que en la validación interna. Esto puede deberse a diferencias entre los datasets de test y entrenamiento, o a limitaciones del modelo utilizado.

### Descripción detallada del algoritmo propuesto

Se utilizó XGBoost (XGBClassifier) para clasificación binaria de la variable inclinacion_peligrosa.

XGBoost es un algoritmo basado en gradient boosting sobre árboles de decisión, eficiente para datasets con características mixtas (numéricas y categóricas) y capaz de capturar relaciones no lineales.

Se incorporaron relaciones entre variables (circ_altura_ratio, diam_circ_ratio) para mejorar la capacidad predictiva del modelo.

Parámetroso utilizados:

```
n_estimators = 500

max_depth = 5

learning_rate = 0.05

subsample = 0.8, colsample_bytree = 0.8 (para regularización y evitar overfitting)

scale_pos_weight ajustado según el desequilibrio de clases (proporción 0/1).
```
