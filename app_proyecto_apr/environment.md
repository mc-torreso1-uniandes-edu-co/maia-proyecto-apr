# Documentación de `environment.py`

[README](../README.md) · [Environment](environment.md) · [Agent](agent.md) · [Train](train.md) · [Run](run.md) · [Game](game.md)

## ¿Qué hace este archivo?

El archivo define la clase `door_key_ball_environment`, que implementa un entorno de **aprendizaje por refuerzo** para el problema de **puerta-llave-bola**.

Su objetivo es modelar:
- El tablero y sus restricciones.
- El estado del agente.
- Las acciones disponibles.
- Las recompensas por acción.
- La dinámica de transición entre estados.

Este entorno es el “mundo” sobre el cual entrenan o evalúan los agentes de RL del proyecto.

---

## Representación del estado

Cada estado se representa como:

`S = (R, C, KP, BP, DO)`

Donde:
- `R`: fila del agente.
- `C`: columna del agente.
- `KP`: si la llave fue recogida (`0` no, `1` sí).
- `BP`: si la bola fue recogida (`0` no, `1` sí).
- `DO`: si la puerta está abierta (`0` no, `1` sí).

Estado inicial por defecto:
- `(3, 1, 0, 0, 0)`

---

## Configuración del entorno

En `__init__` se definen:
- Límites del tablero (`board`).
- Paredes (`walls`).
- Posición de puerta (`door`), llave (`key`), bola (`ball`) y salida (`exit`).
- Estado inicial (`initial_state`).
- Límite de pasos por episodio (`max_steps`).
- Conjunto de acciones.
- Tabla de recompensas.

Además, separa columnas de habitación izquierda/derecha para asignar penalizaciones y recompensas de movimiento.

---

## Acciones disponibles

La clase define 6 acciones:
- `UP`
- `DOWN`
- `RIGHT`
- `LEFT`
- `PICK_OBJECT`
- `OPEN_DOOR`

### Reglas clave
- No se puede mover fuera del tablero.
- No se puede atravesar paredes.
- Desde la puerta cerrada, moverse a la derecha es inválido.
- `PICK_OBJECT` solo es válida:
  - En la llave, si aún no se recogió.
  - En la bola, solo si la llave ya fue recogida.
- `OPEN_DOOR` solo es válida en la puerta y si ya se tiene llave y bola.

---

## Recompensas

El entorno usa recompensas densas (positivas y negativas), por ejemplo:
- Recoger llave: `+3`
- Recoger bola: `+2`
- Abrir puerta: `+5`
- Llegar a la salida: `+15`
- Cruce correcto a la derecha con puerta abierta: `+1`
- Acción inválida (movimiento/abrir/recoger): penalización
- Movimientos válidos: pequeña penalización para incentivar eficiencia

Esto ayuda al agente a aprender secuencias útiles y evitar acciones sin progreso.

---

## Flujo principal de interacción

### `reset()`
Reinicia el entorno al estado inicial y contador de pasos en cero.

### `step_current(action)`
Aplica una acción al estado actual y retorna:
- `next_state`
- `reward`
- `done`
- info con número de paso

También termina el episodio si se alcanza `max_steps`.

### `do_action(state, action)`
Función núcleo de transición:
1. Evalúa acción.
2. Llama a subrutina correspondiente (`do_move`, `do_pick_object`, `do_open_door`).
3. Evalúa si el estado resultante es terminal.

---

## Funciones auxiliares importantes

- `in_board`: valida límites.
- `is_wall`, `is_door`, `is_exit`: validaciones espaciales.
- `is_terminal`: verifica si se llegó a la salida.
- `is_valid_agent_position`: valida si una celda es transitable.
- `get_possible_actions`: calcula acciones válidas desde un estado.
- `get_states`: genera el espacio de estados válido completo.
- `generate_transition_table`: crea una tabla de transición determinista (`S, A, NS, P, R, Terminal`) como `DataFrame`.
- `describe`: devuelve un resumen de la configuración.

---

## ¿Para qué sirve en el proyecto?

`environment.py` encapsula toda la lógica del problema MDP:
- Define el espacio de estados y acciones.
- Determina la función de recompensa.
- Controla la dinámica de transición.

Por eso, es la base para entrenar agentes (por ejemplo Q-learning), simular episodios y analizar comportamiento de política.

---

[README](../README.md) · [Environment](environment.md) · [Agent](agent.md) · [Train](train.md) · [Run](run.md) · [Game](game.md)

[⬅ Volver al README](../README.md)