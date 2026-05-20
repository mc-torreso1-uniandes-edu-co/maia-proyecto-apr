# Diagramas del proyecto

[README](../README.md)

## Diagrama de clases

![Diagrama de clases](diagrama_clases.png)

Figura: Diagrama de clases del ambiente, el agente y la aplicación visual.

## Diagrama de secuencia de entrenamiento

![Diagrama de secuencia de entrenamiento](secuencia_entrenamiento.png)

Figura: Secuencia de entrenamiento del agente con Q-Learning.

## Flujo visual del agente

![Diagrama de secuencia visual](secuencia_visual.png)

Figura: Secuencia de ejecución visual del agente en Pygame.

## Diagrama de secuencia de experimentos

![Diagrama de secuencia de experimentos](secuencia_experimentos.png)

Figura: Secuencia de ejecución de experimentos con variación de parámetros y generación de reportes.

---

## Regenerar los diagramas

Si editas archivos `.mmd`, puedes regenerar los PNG con Mermaid CLI (`mmdc`) o con el script incluido `generate_diagrams.py`.

Instalar Mermaid CLI (requiere Node/npm):

```bash
npm install -g @mermaid-js/mermaid-cli
```

Generar manualmente un diagrama:

```bash
mmdc -i diagrama_clases.mmd -o diagrama_clases.png
```

Generar todos los `.mmd` del directorio con el script Python:

```bash
python generate_diagrams.py
# o desde la raíz del repo:
python app_proyecto_apr/generate_diagrams.py --dir app_proyecto_apr
```

[Environment](environment.md) · [Agent](agent.md) · [Train](train.md) · [Run](run.md) · [Game](game.md) · [Experiment](experiment.md) · [Diagramas](diagramas.md)

[⬅ Volver al README](../README.md)