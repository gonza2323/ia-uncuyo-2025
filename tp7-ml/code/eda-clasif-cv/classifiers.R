library(dplyr)

# Crear carpetas
if(!dir.exists("data")) dir.create("data")
if(!dir.exists("plots")) dir.create("plots")

# Cargar dataset
val_df <- read.csv("data/arbolado-mendoza-dataset-validation.csv")


# 4) Clasificador aleatorio

random_classifier <- function(df) {
  df <- df %>% mutate(
    prediction_prob = runif(nrow(df)),
    prediction_class = ifelse(prediction_prob > 0.5, 1, 0)
  )
  return(df)
}

val_random <- random_classifier(val_df)

write.csv(val_random, "data/arbolado-mendoza-random.csv", row.names = FALSE)


# 5) Clasificador por clase mayoritaria

biggerclass_classifier <- function(df, target_col="inclinacion_peligrosa") {
  major_class <- as.numeric(names(which.max(table(df[[target_col]]))))
  df <- df %>% mutate(prediction_class = major_class)
  return(df)
}

val_bigger <- biggerclass_classifier(val_df, "inclinacion_peligrosa")
write.csv(val_bigger, "data/arbolado-mendoza-biggerclass.csv", row.names = FALSE)


# Función matriz de confusión

confusion_matrix <- function(df, target_col="inclinacion_peligrosa", pred_col="prediction_class") {
  TP <- sum(df[[target_col]] == 1 & df[[pred_col]] == 1)
  TN <- sum(df[[target_col]] == 0 & df[[pred_col]] == 0)
  FP <- sum(df[[target_col]] == 0 & df[[pred_col]] == 1)
  FN <- sum(df[[target_col]] == 1 & df[[pred_col]] == 0)
  matrix <- matrix(c(TP, FP, FN, TN), nrow=2, byrow=TRUE,
                   dimnames=list("Predicted"=c("1","0"), "Actual"=c("1","0")))
  return(list(matrix=matrix, TP=TP, TN=TN, FP=FP, FN=FN))
}


# Funciones de métricas

calculate_metrics <- function(TP, TN, FP, FN) {
  Accuracy <- (TP + TN) / (TP + TN + FP + FN)
  Precision <- ifelse((TP + FP) == 0, NA, TP / (TP + FP))
  Sensitivity <- ifelse((TP + FN) == 0, NA, TP / (TP + FN))  # Recall
  Specificity <- ifelse((TN + FP) == 0, NA, TN / (TN + FP))
  return(list(Accuracy=Accuracy, Precision=Precision, Sensitivity=Sensitivity, Specificity=Specificity))
}


# Métricas para clasificador aleatorio

cm_random <- confusion_matrix(val_random)
metrics_random <- calculate_metrics(cm_random$TP, cm_random$TN, cm_random$FP, cm_random$FN)

cat("\nMatriz de confusión del clasificador aleatorio:\n")
print(cm_random)

cat("\nMétricas del clasificador aleatorio:\n")
print(metrics_random)


# Métricas para clasificador clase mayoritaria

cm_bigger <- confusion_matrix(val_bigger)
metrics_bigger <- calculate_metrics(cm_bigger$TP, cm_bigger$TN, cm_bigger$FP, cm_bigger$FN)

cat("\nMatriz de confusión del clasificador por clase mayoritaria:\n")
print(cm_bigger)

cat("\nMétricas del clasificador por clase mayoritaria:\n")
print(metrics_bigger)
