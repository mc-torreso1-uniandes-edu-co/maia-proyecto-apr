# Documentación de experiment.py

Resumen breve
---------------
`experiment.py` orquesta la ejecución de experimentos de entrenamiento y explotación del agente, genera un informe por experimento (archivo TXT) y escribe un resumen final comparativo (`experiment_results/summary_experiments.txt`).

Propósito
--------
- Ejecutar una malla de experimentos (grid) variando parámetros (por ejemplo, `alpha`, `episodios`).
- Generar un reporte por experimento con tablas ASCII que contienen métricas de entrenamiento y explotación.
- Generar al final un resumen global comparando los experimentos realizados.

Archivos de salida
------------------
- Carpeta: `experiment_results/`
- Por experimento: `reporte_alpha_<alpha>_episodios_<n>.txt` (informe TXT con tablas)
- Resumen final: `experiment_results/summary_experiments.txt`

Contrato clave: `agent.explore()`
--------------------------------
El `experiment.py` asume que el agente implementa `explore()` con el siguiente contrato (orden y tipos):

- retorna 5 valores en este orden:
  1. `terminales` (int): número de episodios que terminaron (terminales)
  2. `no_terminales` (int): número de episodios no terminales
  3. `sum_steps` (int): suma de pasos de todos los episodios (terminales + no terminales)
  4. `max_pasos_terminales` (int): máximo de pasos observado entre episodios terminales
  5. `min_pasos_terminales` (int): mínimo de pasos observado entre episodios terminales

Nota: `prom_pasos_episodio` en los reportes se calcula como `sum_steps / episodios`.

Funciones principales (resumen)
-----------------------------
- `make_table(headers, rows)`
  - Genera una tabla ASCII a partir de `headers` (lista de strings) y `rows` (lista de listas).

- `summarize_q_table(agent)`
  - Calcula estadísticas resumen de la Q-table del `agent` (si aplica). Usado para incluir resumen numérico en el informe.

- `run_exploitation(agent)`
  - Ejecuta la fase de explotación con el agente y devuelve una tabla con: estados visitados, reward por episodio y `a_reward`.
  
- `write_experiment_report(path, ...)`
  - Ensambla y escribe el informe TXT por experimento en `path`. Incluye secciones de entrenamiento, explotación y resumen de Q-table.
  - Todos los encabezados dentro del informe están en minúsculas.

- `build_summary_row(params, metrics)`
  - Prepara una fila del resumen global con los campos principales: `alpha`, `episodios`, `terminales`, `no_terminales`, `prom_pasos_episodio`, `max_pasos_terminales`, `min_pasos_terminales`, entre otros.

- `write_summary_txt(path, rows)`
  - Escribe `summary_experiments.txt` con el conjunto de filas construidas por `build_summary_row`.

- `run_grid_experiments(alphas, episodios_list)`
  - Función de alto nivel que itera la malla de valores. Nota: la lógica final itera primero por `episodios` y luego por `alphas` (orden: episodios → alphas).

Formato y convenciones
----------------------
- Encabezados y secciones: siempre en minúsculas.
- Reward y reward acumulada: formato `+6.2f` (ej: `+12.34`).
- Tablas: estilo ASCII generado por `make_table()`.
- No se escribe la Q-table por experimento (se eliminó el guardado CSV por experimento).

Ejemplos de ejecución
---------------------
Ejecutar el script como módulo o importando la función de experimentos:

```bash
python experiment.py
# o desde Python
python -c "from experiment import run_grid_experiments; run_grid_experiments([0.1,0.2],[1,3])"
```

Salida esperada
---------------
- Archivos `reporte_alpha_<alpha>_episodios_<n>.txt` en `experiment_results/` con 3 secciones principales: entrenamiento, explotación y resumen de q-table.
- Archivo `experiment_results/summary_experiments.txt` con una fila por experimento y las columnas de métricas comparativas (incluye `prom_pasos_episodio`, `max_pasos_terminales`, `min_pasos_terminales`).

Notas de implementación y mantenimiento
-------------------------------------
- Si se modifica la API de `agent.explore()` hay que actualizar el contrato documentado arriba y todos los callers (`train.py`, `experiment.py`).
- El generador de resumen asume que `sum_steps` incluye episodios terminales y no terminales.
- Si desea que el resumen final se exporte también como CSV, se puede añadir una función auxiliar para convertir las filas ASCII en CSV; actualmente el flujo evita crear CSV intermedios.


Autor: Equipo de desarrollo del proyecto
Fecha: 2026-05-12
