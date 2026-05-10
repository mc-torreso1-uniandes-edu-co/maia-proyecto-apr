# Explicación de `agent.py`

## Propósito

El archivo `agent.py` implementa el agente de aprendizaje por refuerzo del proyecto. Su función principal es aprender una política útil mediante **Q-learning** para interactuar con el entorno definido en `environment.py`.

## Clase principal

### `q_learning_agent`

Esta clase encapsula toda la lógica del agente.

#### Responsabilidades

- Construir el mapeo entre estados y acciones.
- Mantener la **Q-table**.
- Elegir acciones con estrategia **epsilon-greedy**.
- Actualizar valores Q a partir de recompensas.
- Guardar y cargar la Q-table en formato CSV.
- Entrenar al agente por episodios.
- Ejecutar una demostración paso a paso.

## Atributos principales

- `env`: instancia del entorno.
- `alpha`: tasa de aprendizaje.
- `gamma`: factor de descuento.
- `epsilon`: probabilidad de exploración.
- `epsilon_min`: valor mínimo de exploración.
- `epsilon_decay`: factor de reducción de `epsilon`.
- `states`: lista de estados válidos del entorno.
- `actions`: lista de acciones permitidas.
- `state_to_idx`: diccionario para convertir estados a índices.
- `action_to_idx`: diccionario para convertir acciones a índices.
- `q_table`: matriz con los valores Q.

## Métodos principales

### `__init__(env, alpha, gamma, epsilon, epsilon_min, epsilon_decay)`

Inicializa el agente y crea la Q-table llena de ceros.

### `choose_action(state)`

Selecciona una acción usando **epsilon-greedy**:

- con probabilidad `epsilon`, explora con una acción aleatoria;
- en caso contrario, elige la mejor acción conocida.

### `best_action(state)`

Devuelve la mejor acción según la Q-table. Además, evita seleccionar acciones que no cambien el estado.

### `update_values(state, action, reward, next_state)`

Actualiza la Q-table usando la regla clásica de Q-learning:

$$
Q(s,a) \leftarrow (1-\alpha)Q(s,a) + \alpha\left(r + \gamma \max_{a'} Q(s',a')\right)
$$

### `step(action)`

Ejecuta una acción en el entorno actual y devuelve:

- nuevo estado,
- recompensa,
- indicador de finalización,
- información adicional del paso.

### `decay_epsilon()`

Disminuye gradualmente `epsilon` para que el agente explore menos con el tiempo.

### `save_q_table(path="q_table.csv")`

Guarda la Q-table en un archivo CSV.

### `load_q_table(path="q_table.csv")`

Carga la Q-table desde un CSV. Soporta más de un formato histórico de archivo.

### `explore(episodes)`

Entrena al agente durante varios episodios. En cada episodio:

1. reinicia el entorno,
2. selecciona acciones,
3. actualiza la Q-table,
4. reduce `epsilon`,
5. guarda el resultado final.

### `explode(render_func=None, step_delay=1.0)`

Ejecuta una demostración del agente paso a paso. Puede usar una función externa para mostrar el estado en consola o en otra interfaz.

## Flujo general del agente

1. Se crea el entorno.
2. Se inicializa el agente con las acciones y estados válidos.
3. El agente explora el entorno durante el entrenamiento.
4. La Q-table se actualiza con la experiencia acumulada.
5. Luego la Q-table se guarda para reutilizarla.
6. En ejecución, el agente carga la Q-table y actúa con la mejor política aprendida.

## Relación con otros archivos

- `environment.py`: define el mundo y las reglas.
- `train.py`: entrena al agente y guarda la Q-table.
- `run.py`: ejecuta una demostración en consola.
- `game.py`: usa el agente en una interfaz gráfica con Pygame.

## Observación importante

El archivo contiene una estrategia útil para aprendizaje por refuerzo, pero su desempeño depende de:

- la calidad del entorno,
- la cantidad de episodios de entrenamiento,
- el valor de `epsilon_decay`,
- y la correcta definición de recompensas.

## Resumen

`agent.py` es el núcleo del aprendizaje del proyecto. Su clase `q_learning_agent` aprende qué hacer en cada estado del entorno y luego usa ese conocimiento para actuar de forma cada vez más eficiente.