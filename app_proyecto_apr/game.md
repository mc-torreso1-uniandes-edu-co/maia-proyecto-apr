# Documentación de `game.py`

[README](../README.md)

## ¿Qué hace este archivo?

`game.py` implementa la aplicación visual del proyecto usando **Pygame**.

La clase `rl_game_app` permite:
- Cargar y ejecutar al agente entrenado.
- Visualizar el tablero y los objetos en tiempo real.
- Avanzar automáticamente según la política aprendida.
- Mostrar estado, acción y recompensa en un panel inferior.

---

## Clase principal: `rl_game_app`

### Inicialización (`__init__`)

Configura:
- Pygame y ventana principal.
- Entorno (`door_key_ball_environment`).
- Agente (`q_learning_agent`).
- Carga de `q_table.csv` (si existe).
- Parámetros visuales (tamaño de celdas, colores, fuentes, panel).

Si no encuentra Q-table, la app sigue funcionando pero muestra advertencia.

### Estado de simulación (`reset`)

Reinicia:
- estado del entorno,
- banderas de episodio,
- última acción/recompensa,
- acumulado de recompensa.

### Dibujo de escena

- `draw_grid()`: cuadrícula base.
- `draw_static()`: paredes, puerta, llave, bola y salida.
- `draw_agent()`: agente en su celda actual.
- `draw_panel()`: texto de estado, transición, acción, recompensa y mensajes de control.
- `render()`: refresco completo de pantalla.

### Avance de política (`step_forward`)

Realiza un paso automático:
1. El agente elige acción.
2. Se aplica en el entorno.
3. Se actualiza estado local y acumulado.
4. Se imprime traza en consola.

### Bucle principal (`run(step_interval=5.0)`)

Gestiona eventos de teclado y ejecución automática por intervalos.

Controles:
- `SPACE`: iniciar / pausar / reanudar / reiniciar (si terminó).
- `ESC`: salir.

---

## Punto de entrada

Cuando se ejecuta directamente:

1. Crea `rl_game_app()`.
2. Llama `app.run(step_interval=5.0)`.

---

## ¿Cómo se usa?

Desde la carpeta `app_proyecto_apr`:

```bash
python game.py
```

Recomendado: entrenar antes con `python train.py` para cargar una política útil.

---

## Rol dentro del proyecto

`game.py` es la interfaz de **demostración visual** del agente RL:
- facilita inspección cualitativa del comportamiento,
- permite observar decisiones paso a paso,
- ayuda en presentación y validación del aprendizaje.

[Environment](environment.md) · [Agent](agent.md) · [Train](train.md) · [Run](run.md) · [Game](game.md) · [Experiment](experiment.md) · [Diagramas](diagramas.md)

[⬅ Volver al README](../README.md)