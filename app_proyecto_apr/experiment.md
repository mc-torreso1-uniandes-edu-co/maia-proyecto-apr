# Documentación de `experiment.py`

[README](../README.md)

## ¿Qué hace este archivo?

`experiment.py` orquesta la ejecución de experimentos de entrenamiento y explotación del agente, genera un informe por experimento (TXT) y escribe un resumen comparativo final en `experiment_results/summary_experiments.txt`.

Su propósito es:
- Ejecutar una malla de experimentos variando parámetros (por ejemplo `alpha` y `episodios`).
- Generar un reporte por experimento con tablas ASCII de métricas de entrenamiento y explotación.
- Generar un resumen global para comparar resultados.

---

## Archivos de salida

- Carpeta: `experiment_results/`
- Por experimento: `reporte_alpha_<alpha>_episodios_<n>.txt`
- Resumen final: `experiment_results/summary_experiments.txt`

---

## Diagramas asociados

- Fuente Mermaid: [secuencia_experimentos.mmd](secuencia_experimentos.mmd)
- Imagen PNG: [secuencia_experimentos.png](secuencia_experimentos.png)

Tipo de diagrama: secuencia.

---

## Contrato clave: `agent.explore()`

`experiment.py` asume que el agente implementa `explore()` y retorna 5 valores en este orden:

1. `terminales` (int): episodios terminales.
2. `no_terminales` (int): episodios no terminales.
3. `sum_steps` (int): suma de pasos de todos los episodios.
4. `max_pasos_terminales` (int): máximo de pasos en episodios terminales.
5. `min_pasos_terminales` (int): mínimo de pasos en episodios terminales.

Nota: `prom_pasos_episodio` en reportes se calcula como `sum_steps / episodios`.

---

## Funciones principales

### `make_table(headers, rows)`

Genera una tabla ASCII a partir de `headers` (lista de strings) y `rows` (lista de listas).

### `summarize_q_table(agent)`

Calcula estadísticas resumen de la Q-table del agente para incluirlas en el informe.

### `run_exploitation(agent)`

Ejecuta la fase de explotación y devuelve métricas como estados visitados, reward por episodio y reward acumulada.

### `write_experiment_report(path, ...)`

Ensambla y escribe el informe TXT por experimento en `path` con secciones de entrenamiento, explotación y resumen de Q-table.

### `build_summary_row(params, metrics)`

Construye una fila del resumen global con campos como `alpha`, `episodios`, `terminales`, `no_terminales`, `prom_pasos_episodio`, `max_pasos_terminales` y `min_pasos_terminales`.

### `write_summary_txt(path, rows)`

Escribe `summary_experiments.txt` con el conjunto de filas agregadas.

### `run_grid_experiments(alphas, episodios_list)`

Recorre la malla de valores y ejecuta los experimentos. La lógica actual itera primero por `episodios` y luego por `alphas`.

---

## Formato y convenciones

- Encabezados y secciones de reportes: en minúsculas.
- Reward y reward acumulada: formato `+6.2f` (ej. `+12.34`).
- Tablas: estilo ASCII generado por `make_table()`.
- No se guarda Q-table por experimento en CSV.

---

## ¿Cómo se usa?

Desde la carpeta `app_proyecto_apr`:

```bash
python experiment.py
```

O invocando la función directamente:

```bash
python -c "from experiment import run_grid_experiments; run_grid_experiments([0.1,0.2],[1,3])"
```

---

## Salida esperada

- Archivos `reporte_alpha_<alpha>_episodios_<n>.txt` con secciones de entrenamiento, explotación y resumen de Q-table.
- Archivo `experiment_results/summary_experiments.txt` con una fila por experimento.

---

## Notas de mantenimiento

- Si cambia la API de `agent.explore()`, actualizar `experiment.py`, `train.py` y esta documentación.
- El resumen asume que `sum_steps` incluye episodios terminales y no terminales.

---

Autor: Equipo de desarrollo del proyecto  
Fecha: 2026-05-12

[Environment](environment.md) · [Agent](agent.md) · [Train](train.md) · [Run](run.md) · [Game](game.md) · [Experiment](experiment.md) · [Diagramas](diagramas.md)

[⬅ Volver al README](../README.md)