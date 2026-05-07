import csv
import ast

with open('q_table.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Estadísticas
print('=== ANÁLISIS DE LA Q-TABLE ===\n')
print(f'Total de estados: {len(rows)}\n')

# Tablero válido
print('Tablero: 4 filas (1-4) × 9 columnas (1-9) = 36 celdas')
print('Paredes en: (1,5), (2,5), (3,5) = 3 paredes')
print('Celdas válidas: 36 - 3 = 33 celdas')
print('Estados posibles: 33 celdas × 2³ (Llave, Bola, Puerta) = 33 × 8 = 264 ✓\n')

# Estados con todos ceros
action_cols = ['UP', 'DOWN', 'RIGHT', 'LEFT', 'PICK_OBJECT', 'OPEN_DOOR']
states_with_zeros = []

for row in rows:
    all_zero = all(float(row[col]) == 0 for col in action_cols)
    if all_zero:
        states_with_zeros.append(row)

print(f'Estados con TODOS ceros (nunca visitados): {len(states_with_zeros)} de {len(rows)} ({100*len(states_with_zeros)/len(rows):.1f}%)')
print(f'Estados con valores aprendidos: {len(rows) - len(states_with_zeros)} ({100*(1-len(states_with_zeros)/len(rows)):.1f}%)\n')

# Mostrar ejemplos de estados sin explorar
print('Ejemplos de estados NO explorados (todos ceros):')
for i in range(min(10, len(states_with_zeros))):
    print(f"  {states_with_zeros[i]['STATE']}")

if len(states_with_zeros) > 10:
    print('\n  ...\n')
    for i in range(max(10, len(states_with_zeros)-5), len(states_with_zeros)):
        print(f"  {states_with_zeros[i]['STATE']}")

# Análisis por celda
print('\n\n=== ANÁLISIS POR CELDA ===\n')

zeros_by_cell = {}
for row in states_with_zeros:
    state_str = row['STATE']
    state_tuple = ast.literal_eval(state_str)
    cell = (state_tuple[0], state_tuple[1])
    if cell not in zeros_by_cell:
        zeros_by_cell[cell] = 0
    zeros_by_cell[cell] += 1

print(f'Celdas con estados sin explorar: {len(zeros_by_cell)}')
print('Estados sin explorar por celda:')
for cell in sorted(zeros_by_cell.keys()):
    print(f"  Celda {cell}: {zeros_by_cell[cell]} estados con ceros")
