from environment import door_key_ball_environment
from agent import q_learning_agent

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def smooth(x: pd.Series | np.ndarray | list[float], window: int = 50) -> np.ndarray:
    """Suaviza una secuencia usando una media móvil.

    Args:
        x: Secuencia numérica a suavizar.
        window: Tamaño de la ventana deslizante.

    Returns:
        ndarray con la serie suavizada.
    """
    return pd.Series(x).rolling(window, min_periods=1).mean().to_numpy()


def plot_learning_curve(history_csv: str | Path, out_dir: Path, window: int = 50) -> Path | None:
    """Genera la curva de aprendizaje a partir del historial de entrenamiento.

    Lee `training_history.csv`, dibuja la recompensa original y la versión
    suavizada, y guarda la imagen en `learning_curve.png`.

    Args:
        history_csv: Ruta del archivo con el historial.
        out_dir: Carpeta de salida para la figura.
        window: Ventana usada por `smooth()`.

    Returns:
        Ruta del archivo PNG generado o `None` si no fue posible crear la figura.
    """
    try:
        df = pd.read_csv(history_csv)
    except Exception:
        return None

    if 'reward' not in df.columns:
        return None

    y = np.asarray(df['reward'].values)
    x = np.asarray(df['episode'].values) if 'episode' in df.columns else np.arange(len(y)) + 1

    plt.figure(figsize=(9, 5))
    plt.plot(x, y, color='lightgray', alpha=0.9, label='original')
    plt.plot(x, smooth(y, window), color='tab:blue', label=f'suavizada (w={window})')
    plt.xlabel('Episodios')
    plt.ylabel('Recompensa')
    plt.title('Curva de aprendizaje')
    plt.grid(True)
    plt.legend()

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'learning_curve.png'
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    return out_path


def plot_q_heatmap(q_csv: str | Path, out_dir: Path) -> Path | None:
    """Genera un mapa de calor de la Q-table mostrando estados relevantes.

    El gráfico filtra estados que tienen al menos un valor Q distinto de cero,
    conserva las etiquetas de todos los estados filtrados en el eje Y y ajusta
    automáticamente el alto de la figura para mejorar la legibilidad.

    Args:
        q_csv: Ruta del archivo CSV de la Q-table.
        out_dir: Carpeta de salida para la figura.

    Returns:
        Ruta del archivo PNG generado o `None` si no fue posible crear la figura.
    """
    try:
        df = pd.read_csv(q_csv)
    except Exception:
        return None

    out_dir.mkdir(parents=True, exist_ok=True)

    if 'STATE' in df.columns:
        display = df.set_index('STATE')

        # Mostrar solo estados con al menos un valor Q distinto de cero
        display = display[(display != 0).any(axis=1)]

        if len(display) == 0:
            return None

        figure_height = max(8, 0.25 * len(display))
        plt.figure(figsize=(14, figure_height))
        ax = sns.heatmap(display, cmap='coolwarm', center=0, yticklabels=list(display.index))
        ax.set_yticklabels(display.index, rotation=0, fontsize=8)
        plt.xlabel('Acción')
        plt.ylabel('Estado')
        plt.title(f'Mapa de calor Q-table (estado vs acción) - {len(display)} estados aprendidos')
        out_path = out_dir / 'qtable_heatmap_states_actions.png'
        plt.savefig(out_path, dpi=150, bbox_inches='tight')
        plt.close()
        return out_path

def train(episodes: int = 500) -> None:
    """Entrena al agente durante la cantidad de episodios indicada.

    Args:
        episodes: Número de episodios usados para el entrenamiento.

    Side Effects:
        Guarda `q_table.csv`, actualiza `experiment_results/training_history.csv`
        y genera las imágenes `learning_curve.png` y
        `qtable_heatmap_states_actions.png` si los datos necesarios existen.
    """
    env = door_key_ball_environment()
    agent = q_learning_agent(env)

    terminales, no_terminales, sum_steps, max_steps, min_steps = agent.explore(episodes, track=True)
    print(f"episodios: {episodes} |terminales: {terminales} | no_terminales: {no_terminales} | prom_pasos_episodio: {sum_steps / episodes if episodes > 0 else 0:.2f} | max_pasos_terminales: {max_steps} | min_pasos_terminales: {min_steps}")

    agent.save_q_table()

    # generar gráficas (si hay historial y q-table)
    base = Path(__file__).resolve().parent
    out_dir = base / 'experiment_results'
    hist_path = out_dir / 'training_history.csv'
    q_path = base / 'q_table.csv'

    lc = plot_learning_curve(hist_path, out_dir)
    if lc:
        print(f"Curva de aprendizaje guardada en: {lc}")

    qh = plot_q_heatmap(q_path, out_dir)
    if qh:
        print(f"Mapa de calor Q-table guardado en: {qh}")

    print("Entrenamiento completado")

if __name__ == "__main__":
    train()