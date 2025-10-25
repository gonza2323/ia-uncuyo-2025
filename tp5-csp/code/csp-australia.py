import pandas as pd
from copy import deepcopy
from collections import deque

# --- Datos iniciales ---
variables = ["WA", "NT", "SA", "Q", "NSW", "V", "T"]
colors = {"r", "g", "b"}

# Vecinos
neighbors = {
    "WA": ["NT", "SA"],
    "NT": ["WA", "SA", "Q"],
    "SA": ["WA", "NT", "Q", "NSW", "V"],
    "Q": ["NT", "SA", "NSW"],
    "NSW": ["Q", "SA", "V"],
    "V": ["SA", "NSW"],
    "T": []
}

# Dominios iniciales
domains = {v: set(colors) for v in variables}
domains["WA"] = {"r"}   # Asignado
domains["V"]  = {"b"}   # Asignado

# Cola inicial: solo arcos conectados a WA y V (dirigidos hacia ellas)
queue = deque([
    ("NT", "WA"), ("SA", "WA"),
    ("SA", "V"), ("NSW", "V")
])

def revise(domains, Xi, Xj):
    removed = set()
    for x in set(domains[Xi]):
        if not any(x != y for y in domains[Xj]):
            domains[Xi].remove(x)
            removed.add(x)
    return removed

log = []
iteration = 1

while queue:
    Xi, Xj = queue.popleft()
    state_before = deepcopy(domains)
    queue_before = list(queue)

    removed = revise(domains, Xi, Xj)
    if removed:
        result = f"Eliminado {removed} de {Xi}"
        # Si el dominio queda vacío -> inconsistencia
        if not domains[Xi]:
            result += " → Dominio vacío (inconsistencia)"
            log.append({
                "Iter": iteration, "Arco": f"({Xi},{Xj})",
                "Cola antes": queue_before,
                **{v: state_before[v] for v in variables},
                "Resultado": result
            })
            break
        # Agregar arcos (Xk, Xi) para todos los vecinos distintos de Xj
        for Xk in neighbors[Xi]:
            if Xk != Xj:
                queue.append((Xk, Xi))
    else:
        result = "Sin cambios"

    log.append({
        "Iter": iteration, "Arco": f"({Xi},{Xj})",
        "Cola antes": queue_before,
        **{v: state_before[v] for v in variables},
        "Resultado": result
    })
    iteration += 1

# --- Convertir a DataFrame y mostrar como tabla markdown ---
df = pd.DataFrame(log)
print(df.to_markdown(index=False))
