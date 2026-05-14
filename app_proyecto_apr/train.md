# Documentación de `train.py`

[README](../README.md)

## ¿Qué hace este archivo?

`train.py` ejecuta el proceso de entrenamiento del agente de aprendizaje por refuerzo usando **Q-Learning**.

Su responsabilidad principal es:
- Crear el entorno `door_key_ball_environment`.
- Crear el agente `q_learning_agent`.
- Lanzar la exploración/entrenamiento por un número de episodios.
- Mostrar un resumen final de resultados.
- Guardar la Q-table entrenada.
- Generar gráficas de apoyo si existen los datos de historial.

---

## Estructura principal

### Función `train(episodes=500)`

Esta función:
1. Instancia el entorno.
2. Instancia el agente con ese entorno.
3. Ejecuta `agent.explore(episodes, track=True)` para registrar métricas por episodio.
4. Imprime métricas agregadas del entrenamiento.
5. Guarda `q_table.csv`.
6. Genera gráficas en `experiment_results/` si encuentra los archivos de entrada.

El método `explore` retorna cinco valores:
- `t`: episodios que terminaron en estado terminal.
- `nt`: episodios que no terminaron en estado terminal.
- `s`: suma de pasos de todos los episodios.
- `max_steps`: máximo de pasos en episodios terminales.
- `min_steps`: mínimo de pasos en episodios terminales.

Cuando `track=True`, también se espera que el agente registre un historial de entrenamiento compatible con `experiment_results/training_history.csv`.

Con eso, `train.py` reporta:
- Total de episodios.
- Cuántos terminaron correctamente.
- Cuántos no terminaron.
- Promedio de pasos por episodio (`s / episodes` si `episodes > 0`).
- Máximo y mínimo de pasos en episodios terminales.

Además, el script intenta generar:
- `learning_curve.png`: curva de recompensa original y suavizada con `smooth()`.
- `qtable_heatmap_states_actions.png`: mapa de calor de la Q-table filtrando estados con valores distintos de cero.

---

## Punto de entrada

Cuando se ejecuta directamente, llama:

`train()`

por lo tanto usa **500 episodios** por defecto.

---

## ¿Cómo se usa?

Desde la carpeta `app_proyecto_apr`:

```bash
python train.py
```

Si quieres otro número de episodios, puedes editar el valor por defecto o invocar `train(...)` desde otro script.

### Funciones auxiliares

#### `smooth(x, window=50)`

Aplica un promedio móvil sobre una secuencia para suavizar la curva de aprendizaje antes de graficarla.

#### `plot_learning_curve(history_csv, out_dir, window=50)`

Lee `training_history.csv` y crea `learning_curve.png` con la recompensa original y la versión suavizada.

#### `plot_q_heatmap(q_csv, out_dir)`

Carga `q_table.csv` y genera `qtable_heatmap_states_actions.png` con los estados que tienen valores Q distintos de cero.

---

## Rol dentro del proyecto

`train.py` es el script de **aprendizaje**:
- Genera conocimiento en la Q-table.
- Registra historial de entrenamiento.
- Visualiza la evolución del aprendizaje con gráficas.
- Prepara al agente para ejecución en `game.py` (visual) o `run.py` (consola).

[Environment](environment.md) · [Agent](agent.md) · [Train](train.md) · [Run](run.md) · [Game](game.md) · [Experiment](experiment.md) · [Diagramas](diagramas.md)

[⬅ Volver al README](../README.md)