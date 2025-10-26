# ============================================================
# Script completo: k-fold cross-validation con rpart
# ============================================================

library(dplyr)
library(rpart)

# Crear carpetas si no existen
if(!dir.exists("data")) dir.create("data")
if(!dir.exists("plots")) dir.create("plots")

# Cargar dataset de entrenamiento
train_df <- read.csv("data/arbolado-mendoza-dataset-train.csv")

# ============================================================
# Función para crear folds
# ============================================================

create_folds <- function(df, k=10, seed=42) {
  set.seed(seed)
  n <- nrow(df)
  indices <- sample(1:n)  # mezcla aleatoria
  folds <- split(indices, cut(seq_along(indices), breaks=k, labels=FALSE))
  names(folds) <- paste0("Fold", 1:k)
  return(folds)
}

# ============================================================
# Función para calcular métricas a partir de TP, TN, FP, FN
# ============================================================

confusion_metrics <- function(actual, predicted) {
  TP <- sum(actual == 1 & predicted == 1, na.rm=TRUE)
  TN <- sum(actual == 0 & predicted == 0, na.rm=TRUE)
  FP <- sum(actual == 0 & predicted == 1, na.rm=TRUE)
  FN <- sum(actual == 1 & predicted == 0, na.rm=TRUE)
  
  Accuracy <- (TP + TN) / (TP + TN + FP + FN)
  Precision <- ifelse((TP + FP)==0, NA, TP / (TP + FP))
  Sensitivity <- ifelse((TP + FN)==0, NA, TP / (TP + FN))
  Specificity <- ifelse((TN + FP)==0, NA, TN / (TN + FP))
  
  return(c(Accuracy=Accuracy, Precision=Precision, Sensitivity=Sensitivity, Specificity=Specificity))
}

# ============================================================
# Función de cross-validation
# ============================================================

cross_validation <- function(df, k=10, seed=42) {
  folds <- create_folds(df, k, seed)
  metrics_list <- list()
  
  factor_cols <- c("seccion", "especie")  # variables categóricas
  
  for(i in 1:k) {
    test_idx <- folds[[i]]
    train_idx <- setdiff(1:nrow(df), test_idx)
    
    train_fold <- df[train_idx, ]
    test_fold <- df[test_idx, ]
    
    # Convertir variable objetivo a factor
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

# ============================================================
# Ejecutar validación cruzada
# ============================================================

set.seed(123)  # reproducibilidad
cv_results <- cross_validation(train_df, k=10)

cat("\nMétricas por fold:\n")
print(cv_results$metrics_by_fold)

cat("\nMedia de métricas:\n")
print(cv_results$mean)

cat("\nDesviación estándar de métricas:\n")
print(cv_results$sd)
