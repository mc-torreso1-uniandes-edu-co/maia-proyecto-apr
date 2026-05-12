# Documentación de `agent.py`

[README](../README.md)
## ¿Qué hace este archivo?

`agent.py` define la clase `q_learning_agent`, que implementa un agente de **Q-Learning** para interactuar con el entorno `door_key_ball_environment`.

Su función principal es:
- Seleccionar acciones (exploración/explotación).
- Actualizar valores Q con la transición observada.
- Entrenar durante múltiples episodios.
- Guardar y cargar la Q-table.
- Ejecutar demostraciones paso a paso.

---

## Clase principal: `q_learning_agent`

### Inicialización (`__init__`)

Recibe:
- `env`: entorno RL.
- `alpha`: tasa de aprendizaje.
- `gamma`: factor de descuento.
- `epsilon`: exploración inicial.
- `epsilon_min`: límite mínimo de exploración.
- `epsilon_decay`: decaimiento de exploración.

Además:
- Obtiene el espacio de estados (`env.get_states()`).
- Obtiene las acciones (`env.actions`).
- Crea mapeos `state_to_idx` y `action_to_idx`.
- Inicializa `q_table` en ceros con forma `(num_estados, num_acciones)`.

---

## Selección de acciones

### `choose_action(state)`

Aplica política **ε-greedy**:
- Con probabilidad `epsilon`: elige acción aleatoria.
- En caso contrario: usa `best_action(state)`.

### `best_action(state)`

Ordena acciones por valor Q y evita, en lo posible, acciones que dejan al agente en el mismo estado.

Si todas dejan el estado igual, retorna la de mejor Q entre ellas.

---

## Aprendizaje

### `update_values(state, action, reward, next_state)`

Actualiza la Q-table con la regla clásica:

$$Q(s,a) \leftarrow (1-\alpha)Q(s,a) + \alpha\left[r + \gamma \max_{a'}Q(s',a')\right]$$

Donde:
- `s`: estado actual.
- `a`: acción ejecutada.
- `r`: recompensa inmediata.
- `s'`: siguiente estado.

### `decay_epsilon()`

Reduce gradualmente la exploración multiplicando por `epsilon_decay` mientras `epsilon > epsilon_min`.

---

## Interacción con el entorno

### `step(action)`

Ejecuta una acción sobre el estado actual del entorno, actualiza `env.current_state`, incrementa pasos y retorna:
- `next_state`
- `reward`
- `done`
- `info` con el paso actual

Respeta también el corte por `max_steps` del entorno.

---

## Entrenamiento completo

### `explore(episodes)`

Entrena al agente durante `episodes` episodios:
1. Reinicia entorno.
2. Repite ciclo de acción-transición-actualización hasta terminar.
3. Cuenta episodios terminales y no terminales.
4. Acumula pasos en episodios terminales.
5. Aplica decaimiento de `epsilon` al final de cada episodio.
6. Guarda la Q-table en `q_table.csv`.

Retorna:
- cantidad de episodios terminales,
- cantidad de episodios no terminales,
- suma de pasos en episodios terminales.

---

## Persistencia de la Q-table

### `save_q_table(path="q_table.csv")`

Guarda una tabla CSV con:
- columna `STATE` (tupla serializada),
- una columna por acción (`UP`, `DOWN`, `RIGHT`, etc.).

### `load_q_table(path="q_table.csv")`

Carga la Q-table soportando tres formatos:
1. Formato con columna `STATE`.
2. Formato con columnas separadas `R, C, KP, BP, DO`.
3. Formato matriz directa (fallback).

Esto da compatibilidad con versiones previas del proyecto.

---

## Modo demostración

### `explode(render_func=None, step_delay=1.0)`

Ejecuta un episodio usando la política actual, imprimiendo cada transición y opcionalmente llamando una función de render.

Útil para:
- depurar comportamiento del agente,
- visualizar evolución de estados,
- ejecutar demos en consola o con render personalizado.

---

## Rol dentro del proyecto

`agent.py` es el núcleo de aprendizaje del sistema:
- aprende la política a partir de recompensas,
- persiste el conocimiento en `q_table.csv`,
- alimenta tanto `run.py` (consola) como `game.py` (interfaz visual).

---

[README](../README.md) · [Environment](environment.md) · [Agent](agent.md) · [Train](train.md) · [Run](run.md) · [Game](game.md)

[⬅ Volver al README](../README.md)