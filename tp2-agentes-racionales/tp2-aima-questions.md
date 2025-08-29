# Trabajo Práctico 2
## Ejercicio 5 - Preguntas de AIMA

## 2.10 Consider a modified version of the vacuum environment in Exercise 2.8, in which the agent is penalized one point for each movement.

**a. Can a simple reflex agent be perfectly rational for this environment? Explain.**

No, ya que al no tener memoria ni percepción del entorno global, es incapaz de seguir la estrategia óptima para el problema, que sería pasar por todas las celdas sucias, en el orden que minimice la cantidad total de distancia recorrida.

**b. What about a reflex agent with state? Design such an agent.**

Tampoco puede ser perfectamente racional, aunque será capaz de seguir una mejor estrategia, ya que podría recordar las celdas por las que ya pasó, sin tener que revisarlas de nuevo, y podría determinar también el tamaño del entorno. Un ejemplo podría ser un agente que inicialmente se dirige a la posición (0,0). Una vez allí, cambia de estado (para lo que requiere memoria) y comienza un barrido de todo el mapa, yendo fila por fila, recorriendo las filas pares de izq a derecha, y las impares al revés. Repetiría muy pocas celdas, solo las que atravesó para llegar al origen, en primer lugar. Podría detectar los bordes de la grilla cuando ve que su posición no cambió respecto a la última (utilizando la memoria). En este caso, pasaría a la siguiente fila, y cambiaría de sentido de recorrido horizontal.

**c. How do your answers to a and b change if the agent’s percepts give it the clean/dirty status of every square in the environment?**

En ambos casos (con estado y sin), teniendo acceso a todo el estado del entorno, el agente puede seguir la estrategia más óptima para el problema, que es encontrar el camino más corto que empiece en su posición inicial y pase por todas las celdas sucias. Podría hacer esto con cualquier algoritmo (fuerza bruta o backtracking), y llegar a la solución óptima.

---

## 2.11 Consider a modified version of the vacuum environment in Exercise 2.8, in which the geography of the environment—its extent, boundaries, and obstacles—is unknown, as is the initial dirt configuration. (The agent can go Up and Down as well as Left and Right.)

**a. Can a simple reflex agent be perfectly rational for this environment? Explain.**

No, por la misma razón dada en la respuesta a la pregunta 2.10.a., pero en este caso el agente reflexivo simple estaría aún más limitado debido a la mayor complejidad de este entorno. No podrá identificar ni recordar donde se encuentran los obstáculos, o la forma geométrica del entorno.

**b. Can a simple reflex agent with a randomized agent function outperform a simple reflex agent?**

Sí, ya que por pura probabilidad, podría darse la solución óptima a la que llegaría un agente con acceso a todo el estado del entorno. En cambio, las reglas de un agente reflexivo simple, no serían nunca capaces de generar tal solución (ni por error), para la mayor parte de este tipo de entornos.

**c. Can you design an environment in which your randomized agent will perform poorly? Show your results.**

Lo pero para un agente aleatorio, sería cualquier distribución no uniforme de la suciedad. En particular, podríamos genere muchos obstáculos muy poco probables de atravesar, antes de llegar a las zonas de mayor suciedad, penalizando gravemente al agente aleatorio.

**d. Can a reflex agent with state outperform a simple reflex agent? Can you design a rational agent of this type?**

Sí, por lo mismo expresado en la respuesta a la pregunta 2.10.b. En este caso sería de mucha ayuda también, ya que permitiría reconocer y recordar las ubicaciones de los obstáculos, y la geometría del entorno, no solamente las celdas ya recorridas.