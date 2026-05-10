# Documentación de `train.py`

[README](../README.md) · [Environment](environment.md) · [Agent](agent.md) · [Train](train.md) · [Run](run.md) · [Game](game.md)

## ¿Qué hace este archivo?

`train.py` ejecuta el proceso de entrenamiento del agente de aprendizaje por refuerzo usando **Q-Learning**.

Su responsabilidad principal es:
- Crear el entorno `door_key_ball_environment`.
- Crear el agente `q_learning_agent`.
- Lanzar la exploración/entrenamiento por un número de episodios.
- Mostrar un resumen final de resultados.

---

## Estructura principal

### Función `train(episodes=5000)`

Esta función:
1. Instancia el entorno.
2. Instancia el agente con ese entorno.
3. Ejecuta `agent.explore(episodes)`.
4. Imprime métricas agregadas del entrenamiento.

El método `explore` retorna tres valores:
- `t`: episodios que terminaron en estado terminal.
- `nt`: episodios que no terminaron en estado terminal.
- `s`: suma de pasos en episodios terminales.

Con eso, `train.py` reporta:
- Total de episodios.
- Cuántos terminaron correctamente.
- Cuántos no terminaron.
- Promedio de pasos en los episodios terminales (`s / t` si `t > 0`).

---

## Punto de entrada

Cuando se ejecuta directamente, llama:

`train()`

por lo tanto usa **5000 episodios** por defecto.

---

## ¿Cómo se usa?

Desde la carpeta `app_proyecto_apr`:

```bash
python train.py
```

Si quieres otro número de episodios, puedes editar el valor por defecto o invocar `train(...)` desde otro script.

---

## Rol dentro del proyecto

`train.py` es el script de **aprendizaje**:
- Genera conocimiento en la Q-table.
- Prepara al agente para ejecución en `game.py` (visual) o `run.py` (consola).

---

[README](../README.md) · [Environment](environment.md) · [Agent](agent.md) · [Train](train.md) · [Run](run.md) · [Game](game.md)

[⬅ Volver al README](../README.md)