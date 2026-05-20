# Documentación de `run.py`

[README](../README.md)

## ¿Qué hace este archivo?

`run.py` ejecuta una **demostración en consola** del agente ya entrenado.

Implementa:
- Un render ASCII del tablero (`render(state)`).
- Carga de Q-table (si existe).
- Ejecución del agente en modo explotación (`epsilon = 0`).

---

## Funciones principales

### `render(state)`

Construye una cuadrícula 4x9 con caracteres para mostrar el estado actual:
- `A`: agente.
- `K`: llave (o `*` si ya recogida).
- `B`: bola (o `*` si ya recogida).
- `D`: puerta cerrada.
- `O`: puerta abierta.
- `E`: salida.
- `#`: paredes.
- `.`: celdas vacías.

Sirve para visualizar el episodio sin interfaz gráfica.

### `run()`

1. Crea ambiente y agente.
2. Intenta cargar `q_table.csv`.
3. Si no existe, muestra advertencia.
4. Fuerza explotación (`agent.epsilon = 0`).
5. Ejecuta el episodio con `agent.explode(render_func=render, step_delay=3.0)`.

Al final imprime `¡Episodio terminado!`.

---

## Punto de entrada

Cuando se ejecuta directamente, llama:

`run()`

---

## ¿Cómo se usa?

Desde la carpeta `app_proyecto_apr`:

```bash
python run.py
```

Si no hay Q-table entrenada, primero ejecuta `python train.py`.

---

## Rol dentro del proyecto

`run.py` es útil para:
- Validación rápida del comportamiento del agente.
- Ambientes sin GUI.
- Depuración simple del flujo de estados y acciones en texto.

[Environment](environment.md) · [Agent](agent.md) · [Train](train.md) · [Run](run.md) · [Game](game.md) · [Experiment](experiment.md) · [Diagramas](diagramas.md)

[⬅ Volver al README](../README.md)