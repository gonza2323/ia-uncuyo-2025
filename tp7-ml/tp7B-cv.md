# Trabajo Práctico 7B: Machine Learning


## Parte 1


### 7. Implementar la técnica de validación cruzada (k−folds Cross validation):

#### a) Crear una función de nombre create_folds() que reciba como parámetro un dataframe y la cantidad de folds y devuelva una lista de R con la siguiente estructura: `list(Fold1=c(...), Fold2=c(...), ..., Fold10=c(...))`, donde `Fold1` contenga los índices del dataframe que fueron seleccionados para el primer fold, `Fold2` para el segundo, y así con los demás.

```r
create_folds <- function(df, k=10, seed=42) {
  set.seed(seed)
  n <- nrow(df)
  indices <- sample(1:n)  # mezcla aleatoria
  folds <- split(indices, cut(seq_along(indices), breaks=k, labels=FALSE))
  names(folds) <- paste0("Fold", 1:k)
  return(folds)
}
```


#### b) Crear una función de nombre `cross_validation()` que reciba como parámetro un dataframe y un número de folds y entrene un modelo de árbol de decisión (utilizar el paquete rpart) para cada uno de los posibles conjuntos de entrenamiento y calcule las m´etricas Accuracy, Precision, Sensitivity, Specificity para cada uno de los posibles conjuntos de tests. Devolver media y desviación estándar.

```r
cross_validation <- function(df, k=10, seed=42) {
  folds <- create_folds(df, k, seed)
  metrics_list <- list()
  
  factor_cols <- c("seccion", "especie")
  
  for(i in 1:k) {
    test_idx <- folds[[i]]
    train_idx <- setdiff(1:nrow(df), test_idx)
    
    train_fold <- df[train_idx, ]
    test_fold <- df[test_idx, ]
    
    train_fold$inclinacion_peligrosa <- as.factor(train_fold$inclinacion_peligrosa)
    test_fold$inclinacion_peligrosa <- as.factor(test_fold$inclinacion_peligrosa)
    
    # Alinear niveles de factores entre train y test
    for(col in factor_cols) {
      levels_train <- levels(as.factor(train_fold[[col]]))
      train_fold[[col]] <- factor(train_fold[[col]], levels=levels_train)
      test_fold[[col]] <- factor(test_fold[[col]], levels=levels_train)
    }
    
    # Definir fórmula
    train_formula <- formula(inclinacion_peligrosa ~ altura + circ_tronco_cm + lat + long + seccion + especie)
    
    # Entrenar árbol de decisión
    tree_model <- rpart(train_formula, data=train_fold)
    
    # Predecir sobre test
    predictions <- predict(tree_model, test_fold, type='class')
    predictions <- as.numeric(as.character(predictions))  # convertir a 0/1
    
    # Calcular métricas
    metrics <- confusion_metrics(actual=test_fold$inclinacion_peligrosa, predicted=predictions)
    metrics_list[[i]] <- metrics
  }
  
  # Convertir lista a dataframe
  metrics_df <- do.call(rbind, metrics_list)
  
  # Calcular media y desviación estándar por métrica
  mean_metrics <- colMeans(metrics_df, na.rm=TRUE)
  sd_metrics <- apply(metrics_df, 2, sd, na.rm=TRUE)
  
  return(list(metrics_by_fold=metrics_df, mean=mean_metrics, sd=sd_metrics))
}
```


**Media de métricas:**

| Accuracy  | Precision | Sensitivity | Specificity |
|-----------|-----------|-------------|-------------|
| 0.8876572 | NaN       | 0.0000000   | 1.0000000   |


**Desviación estándar de métricas:**

| Accuracy    | Precision | Sensitivity | Specificity |
|-------------|-----------|-------------|-------------|
| 0.005154521 | NA        | 0.000000000 | 0.000000000 |
