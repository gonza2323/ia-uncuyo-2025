
# Trabajo Práctico 5: Satisfacción de restricciones

## Preguntas

### 1. Describir en detalle una formulación CSP para el Sudoku.

Una posible formulación es la siguiente.

**Variables:** Suponiendo que el Sudoku es de 9×9, tenemos 81 celdas. Cada celda es una variable $X_{i,j}$.

**Dominios:** Los dominios de estas variables son los enteros del 1 al 9. En las celdas con valores iniciales, su dominio se reduce a su valor inicial.

**Restricciones:**

1. Todas las variables en una misma fila (mismo $i$) deben tener valores distintos.

2. Todas las variables en una misma columna (mismo $j$) deben tener valores distintos.

3. Todas las variables en una misma caja de 3×3 (hay 9 cajas, una central y 8 en los bordes del Sudoku), deben tener valores distintos.

**Grafo de restricciones**

Estas variables y sus restricciones pueden representarse como un grafo de restricciones, donde las variables son nodos, y las restricciones aristas entre estos nodos.

La siguiente imagen muestra cómo serían las conexiones de un sólo nodo (no se pueden mostrar las de todos los nodos, ya que son demasiadas).

!["Grafo de restricciones del Sudoku (1 nodo)"](./images/sudoku.png)

Cada celda está conectada a todas las de su misma fila, misma columna, y misma caja (eliminando duplicados), dando un total de 20 conexiones por nodo, y un total de $81 \times 20 \div 2= 810$ aristas para todo el Sudoku.


### 2. Utilizar el algoritmo AC-3 para demostrar que la arco consistencia puede detectar la inconsistencia de la asignación parcial WA=red, V=blue para el problema de colorear el mapa de Australia.

!["Mapa de Australia y grafo de restricciones"](./images/australia.png)
(Figura 6.1 AIMA 3ra edicion)

Tenemos los arcos dirigidos (AC-3 trabaja con arcos dirigidos):


```
(WA,NT),(NT,WA), (WA,SA),(SA,WA),

(NT, Q),(Q, NT), (NT,SA),(SA,NT),

(Q,NSW),(NSW,Q), (Q, SA),(SA, Q),

(NSW,V),(V,NSW), (NSW,SA),(SA,NSW),

(V, SA),(SA, V),
```


En un primer momento, se asignan las variables WA y V.

$$D_{WA} = \{red\}$$
$$D_{V} = \{blue\}$$

Añadimos los arcos conectados a V y WA a la cola

```
Q = {(NT, WA), (SA, WA), (SA, V), (NSW, V)}
```

Ejecutamos el algoritmo

|   Iter | Arco     | Cola antes                                                                                                                                                              | WA    | NT              | SA              | Q               | NSW             | V     | T               | Resultado                                             |
|-------:|:---------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------|:----------------|:----------------|:----------------|:----------------|:------|:----------------|:------------------------------------------------------|
|      1 | (NT,WA)  | [('SA', 'WA'), ('SA', 'V'), ('NSW', 'V')]                                                                                                                               | {'r'} | {'b', 'g', 'r'} | {'b', 'g', 'r'} | {'b', 'g', 'r'} | {'b', 'g', 'r'} | {'b'} | {'b', 'g', 'r'} | Eliminado {'r'} de NT                                 |
|      2 | (SA,WA)  | [('SA', 'V'), ('NSW', 'V'), ('SA', 'NT'), ('Q', 'NT')]                                                                                                                  | {'r'} | {'b', 'g'}      | {'b', 'g', 'r'} | {'b', 'g', 'r'} | {'b', 'g', 'r'} | {'b'} | {'b', 'g', 'r'} | Eliminado {'r'} de SA                                 |
|      3 | (SA,V)   | [('NSW', 'V'), ('SA', 'NT'), ('Q', 'NT'), ('NT', 'SA'), ('Q', 'SA'), ('NSW', 'SA'), ('V', 'SA')]                                                                        | {'r'} | {'b', 'g'}      | {'b', 'g'}      | {'b', 'g', 'r'} | {'b', 'g', 'r'} | {'b'} | {'b', 'g', 'r'} | Eliminado {'b'} de SA                                 |
|      4 | (NSW,V)  | [('SA', 'NT'), ('Q', 'NT'), ('NT', 'SA'), ('Q', 'SA'), ('NSW', 'SA'), ('V', 'SA'), ('WA', 'SA'), ('NT', 'SA'), ('Q', 'SA'), ('NSW', 'SA')]                              | {'r'} | {'b', 'g'}      | {'g'}           | {'b', 'g', 'r'} | {'b', 'g', 'r'} | {'b'} | {'b', 'g', 'r'} | Eliminado {'b'} de NSW                                |
|      5 | (SA,NT)  | [('Q', 'NT'), ('NT', 'SA'), ('Q', 'SA'), ('NSW', 'SA'), ('V', 'SA'), ('WA', 'SA'), ('NT', 'SA'), ('Q', 'SA'), ('NSW', 'SA'), ('Q', 'NSW'), ('SA', 'NSW')]               | {'r'} | {'b', 'g'}      | {'g'}           | {'b', 'g', 'r'} | {'g', 'r'}      | {'b'} | {'b', 'g', 'r'} | Sin cambios                                           |
|      6 | (Q,NT)   | [('NT', 'SA'), ('Q', 'SA'), ('NSW', 'SA'), ('V', 'SA'), ('WA', 'SA'), ('NT', 'SA'), ('Q', 'SA'), ('NSW', 'SA'), ('Q', 'NSW'), ('SA', 'NSW')]                            | {'r'} | {'b', 'g'}      | {'g'}           | {'b', 'g', 'r'} | {'g', 'r'}      | {'b'} | {'b', 'g', 'r'} | Sin cambios                                           |
|      7 | (NT,SA)  | [('Q', 'SA'), ('NSW', 'SA'), ('V', 'SA'), ('WA', 'SA'), ('NT', 'SA'), ('Q', 'SA'), ('NSW', 'SA'), ('Q', 'NSW'), ('SA', 'NSW')]                                          | {'r'} | {'b', 'g'}      | {'g'}           | {'b', 'g', 'r'} | {'g', 'r'}      | {'b'} | {'b', 'g', 'r'} | Eliminado {'g'} de NT                                 |
|      8 | (Q,SA)   | [('NSW', 'SA'), ('V', 'SA'), ('WA', 'SA'), ('NT', 'SA'), ('Q', 'SA'), ('NSW', 'SA'), ('Q', 'NSW'), ('SA', 'NSW'), ('WA', 'NT'), ('Q', 'NT')]                            | {'r'} | {'b'}           | {'g'}           | {'b', 'g', 'r'} | {'g', 'r'}      | {'b'} | {'b', 'g', 'r'} | Eliminado {'g'} de Q                                  |
|      9 | (NSW,SA) | [('V', 'SA'), ('WA', 'SA'), ('NT', 'SA'), ('Q', 'SA'), ('NSW', 'SA'), ('Q', 'NSW'), ('SA', 'NSW'), ('WA', 'NT'), ('Q', 'NT'), ('NT', 'Q'), ('NSW', 'Q')]                | {'r'} | {'b'}           | {'g'}           | {'b', 'r'}      | {'g', 'r'}      | {'b'} | {'b', 'g', 'r'} | Eliminado {'g'} de NSW                                |
|     10 | (V,SA)   | [('WA', 'SA'), ('NT', 'SA'), ('Q', 'SA'), ('NSW', 'SA'), ('Q', 'NSW'), ('SA', 'NSW'), ('WA', 'NT'), ('Q', 'NT'), ('NT', 'Q'), ('NSW', 'Q'), ('Q', 'NSW'), ('V', 'NSW')] | {'r'} | {'b'}           | {'g'}           | {'b', 'r'}      | {'r'}           | {'b'} | {'b', 'g', 'r'} | Sin cambios                                           |
|     11 | (WA,SA)  | [('NT', 'SA'), ('Q', 'SA'), ('NSW', 'SA'), ('Q', 'NSW'), ('SA', 'NSW'), ('WA', 'NT'), ('Q', 'NT'), ('NT', 'Q'), ('NSW', 'Q'), ('Q', 'NSW'), ('V', 'NSW')]               | {'r'} | {'b'}           | {'g'}           | {'b', 'r'}      | {'r'}           | {'b'} | {'b', 'g', 'r'} | Sin cambios                                           |
|     12 | (NT,SA)  | [('Q', 'SA'), ('NSW', 'SA'), ('Q', 'NSW'), ('SA', 'NSW'), ('WA', 'NT'), ('Q', 'NT'), ('NT', 'Q'), ('NSW', 'Q'), ('Q', 'NSW'), ('V', 'NSW')]                             | {'r'} | {'b'}           | {'g'}           | {'b', 'r'}      | {'r'}           | {'b'} | {'b', 'g', 'r'} | Sin cambios                                           |
|     13 | (Q,SA)   | [('NSW', 'SA'), ('Q', 'NSW'), ('SA', 'NSW'), ('WA', 'NT'), ('Q', 'NT'), ('NT', 'Q'), ('NSW', 'Q'), ('Q', 'NSW'), ('V', 'NSW')]                                          | {'r'} | {'b'}           | {'g'}           | {'b', 'r'}      | {'r'}           | {'b'} | {'b', 'g', 'r'} | Sin cambios                                           |
|     14 | (NSW,SA) | [('Q', 'NSW'), ('SA', 'NSW'), ('WA', 'NT'), ('Q', 'NT'), ('NT', 'Q'), ('NSW', 'Q'), ('Q', 'NSW'), ('V', 'NSW')]                                                         | {'r'} | {'b'}           | {'g'}           | {'b', 'r'}      | {'r'}           | {'b'} | {'b', 'g', 'r'} | Sin cambios                                           |
|     15 | (Q,NSW)  | [('SA', 'NSW'), ('WA', 'NT'), ('Q', 'NT'), ('NT', 'Q'), ('NSW', 'Q'), ('Q', 'NSW'), ('V', 'NSW')]                                                                       | {'r'} | {'b'}           | {'g'}           | {'b', 'r'}      | {'r'}           | {'b'} | {'b', 'g', 'r'} | Eliminado {'r'} de Q                                  |
|     16 | (SA,NSW) | [('WA', 'NT'), ('Q', 'NT'), ('NT', 'Q'), ('NSW', 'Q'), ('Q', 'NSW'), ('V', 'NSW'), ('NT', 'Q'), ('SA', 'Q')]                                                            | {'r'} | {'b'}           | {'g'}           | {'b'}           | {'r'}           | {'b'} | {'b', 'g', 'r'} | Sin cambios                                           |
|     17 | (WA,NT)  | [('Q', 'NT'), ('NT', 'Q'), ('NSW', 'Q'), ('Q', 'NSW'), ('V', 'NSW'), ('NT', 'Q'), ('SA', 'Q')]                                                                          | {'r'} | {'b'}           | {'g'}           | {'b'}           | {'r'}           | {'b'} | {'b', 'g', 'r'} | Sin cambios                                           |
|     18 | (Q,NT)   | [('NT', 'Q'), ('NSW', 'Q'), ('Q', 'NSW'), ('V', 'NSW'), ('NT', 'Q'), ('SA', 'Q')]                                                                                       | {'r'} | {'b'}           | {'g'}           | {'b'}           | {'r'}           | {'b'} | {'b', 'g', 'r'} | Eliminado {'b'} de Q → Dominio vacío (inconsistencia) |


### 3. ¿Cuál es la complejidad en el peor caso cuando se ejecuta AC-3 en un árbol estructurado CSP? (i.e. cuando el grafo de restricciones forma un árbol: cualquiera dos variables están relacionadas por a lo sumo un camino).

En un árbol, existe un único camino entre cualquier par de vértices (no hay ciclos). Además, un árbol tiene n - 1 aristas, donde n es la cantidad de vértices.

Si comenzamos la revisión desde un nodo en particular, como no hay ciclos, nunca volveremos a revisar ese nodo. En el peor caso, revisaremos todos los arcos del árbol, lo cuál es $O(n)$, ya que v = n - 1.

En cada revisión de un arco, hay que revisar que para todos los elementos del dominio de un nodo existe uno en el otro nodo que cumpla la restricción. Entonces cada revisión tiene un costo de $O(d^2)$, donde d es el tamaño del dominio más grande del problema.

Entonces, la complejidad total es de $O(nd^2)$.
