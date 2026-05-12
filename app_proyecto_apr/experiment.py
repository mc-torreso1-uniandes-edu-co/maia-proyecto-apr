from __future__ import annotations

from pathlib import Path
from statistics import mean
from typing import Iterable

from environment import door_key_ball_environment
from agent import q_learning_agent


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "experiment_results"
SUMMARY_TXT = OUTPUT_DIR / "summary_experiments.txt"
DEFAULT_ALPHAS = [0.05, 0.1, 0.2]
DEFAULT_EPISODES = [50, 2500, 5000]
DEFAULT_GAMMA = 0.95
DEFAULT_EPSILON = 1.0
DEFAULT_EPSILON_MIN = 0.1
DEFAULT_EPSILON_DECAY = 0.995
METRIC_HEADERS = [
    "alpha",
    "episodios",
    "terminales",
    "no_terminales",
    "prom_pasos_episodio",
    "max_pasos_terminales",
    "min_pasos_terminales",
    "estados",
    "aprendidos",
    "en_cero",
    "densidad",
    "q_max",
    "q_min",
    "prom_qmax",
]

def format_float(value: float) -> str:
    """Convierte un valor decimal a un formato seguro para nombres de archivo."""
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return text.replace("-", "m").replace(".", "_")


def ensure_output_dir() -> Path:
    """Crea la carpeta de salida si no existe."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def make_table(headers: list[str], rows: list[list[str]]) -> str:
    """Construye una tabla ASCII con encabezado, separadores y cierre."""
    widths = [len(header) for header in headers]
    for row in rows:
        for idx, value in enumerate(row):
            widths[idx] = max(widths[idx], len(value))

    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    header_row = "| " + " | ".join(headers[idx].ljust(widths[idx]) for idx in range(len(headers))) + " |"

    lines = [border, header_row, border]
    for row in rows:
        lines.append("| " + " | ".join(row[idx].ljust(widths[idx]) for idx in range(len(row))) + " |")
    lines.append(border)
    return "\n".join(lines)


def summarize_q_table(agent: q_learning_agent, top_n: int = 10) -> str:
    """Genera un análisis textual de la Q-table entrenada."""
    lines: list[str] = []
    q_table = agent.q_table
    total_states = len(agent.states)
    action_names = agent.actions

    rows_with_learning = 0
    zero_rows = 0
    non_zero_values = 0
    row_max_values: list[float] = []

    for _, row in enumerate(q_table):
        if (row != 0).any():
            rows_with_learning += 1
            non_zero_values += int((row != 0).sum())
        else:
            zero_rows += 1
        row_max_values.append(float(row.max()))

    all_values = q_table.flatten()

    lines.append("=== análisis de la q-table ===")
    summary_table = make_table(
        headers=[
            "estados",
            "aprendidos",
            "en_cero",
            "no_cero",
            "densidad",
            "q_max",
            "q_min",
            "prom_qmax",
        ],
        rows=[[
            str(total_states),
            str(rows_with_learning),
            str(zero_rows),
            str(non_zero_values),
            f"{100 * non_zero_values / all_values.size:.2f}%",
            f"{float(q_table.max()):.6f}",
            f"{float(q_table.min()):.6f}",
            f"{mean(row_max_values):.6f}",
        ]],
    )
    lines.append(summary_table)
    lines.append("")

    ranked_states = sorted(
        (
            (float(row.max()), agent.states[idx], row)
            for idx, row in enumerate(q_table)
        ),
        key=lambda item: item[0],
        reverse=True,
    )

    lines.append(f"top {min(top_n, len(ranked_states))} estados por valor máximo aprendido:")
    top_rows: list[list[str]] = []
    for rank, (state_max, state, row) in enumerate(ranked_states[:top_n], start=1):
        best_action_idx = int(row.argmax())
        best_action = action_names[best_action_idx]
        top_rows.append([str(rank), str(state), best_action, f"{state_max:.6f}"])

    top_table = make_table(
        headers=["rank", "state", "best_action", "q_max"],
        rows=top_rows,
    )
    lines.append(top_table)

    return "\n".join(lines)


def run_exploitation(agent: q_learning_agent, max_steps: int | None = None) -> str:
    """Ejecuta una explotación  y retorna el log en texto plano."""
    if max_steps is None:
        max_steps = agent.env.max_steps

    original_epsilon = agent.epsilon
    agent.epsilon = 0.0

    lines: list[str] = []
    state = agent.env.reset()
    done = False
    total_reward = 0.0
    step_rows: list[list[str]] = []

    lines.append("=== explotación ===")

    while not done and agent.env.steps < max_steps:
        action = agent.choose_action(state)
        next_state, reward, done, info = agent.step(action)
        total_reward += reward
        step_rows.append(
            [
                f"{info['step']:03d}",
                str(state),
                action,
                str(next_state),
                f"{reward:+6.2f}",
                f"{total_reward:+6.2f}",
                str(done),
            ]
        )
        state = next_state

    lines.append(
        make_table(
            headers=["step", "state", "action", "next_state", "reward", "a_reward", "done"],
            rows=step_rows,
        )
    )

    if agent.env.is_terminal(state):
        lines.append("resultado_terminal = True")
    else:
        lines.append("resultado_terminal = False")

    lines.append(
        make_table(
            headers=["final_state", "recompensa_acumulada"],
            rows=[[str(state), f"{total_reward:+6.2f}"]],
        )
    )

    agent.epsilon = original_epsilon
    return "\n".join(lines)


def build_summary_row(
    alpha: float,
    episodes: int,
    training_summary: tuple[int, int, int, int, int],
    agent: q_learning_agent,
) -> dict[str, str]:
    terminales, no_terminales, sum_steps, max_steps, min_steps = training_summary

    q_table = agent.q_table
    rows_with_learning = 0
    zero_rows = 0
    non_zero_values = 0
    row_max_values: list[float] = []

    for row in q_table:
        if (row != 0).any():
            rows_with_learning += 1
            non_zero_values += int((row != 0).sum())
        else:
            zero_rows += 1
        row_max_values.append(float(row.max()))

    return {
        "alpha": f"{alpha}",
        "episodios": f"{episodes}",
        "terminales": str(terminales),
        "no_terminales": str(no_terminales),
        "prom_pasos_episodio": f"{sum_steps / episodes:.2f}" if episodes > 0 else "0.00",
        "max_pasos_terminales": str(max_steps),
        "min_pasos_terminales": str(min_steps),
        "estados": str(len(agent.states)),
        "aprendidos": str(rows_with_learning),
        "en_cero": str(zero_rows),
        "densidad": f"{100 * non_zero_values / q_table.size:.2f}%",
        "q_max": f"{float(q_table.max()):.6f}",
        "q_min": f"{float(q_table.min()):.6f}",
        "prom_qmax": f"{mean(row_max_values):.6f}",
    }


def write_summary_txt(rows: list[dict[str, str]], output_path: Path) -> None:
    """Escribe un resumen comparativo final en formato TXT."""
    if not rows:
        return

    widths = [len(h) for h in METRIC_HEADERS]
    for row in rows:
        for idx, header in enumerate(METRIC_HEADERS):
            widths[idx] = max(widths[idx], len(str(row.get(header, ""))))

    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header_row = "| " + " | ".join(METRIC_HEADERS[idx].ljust(widths[idx]) for idx in range(len(METRIC_HEADERS))) + " |"
    lines = ["# RESUMEN FINAL DE EXPERIMENTOS", "", border, header_row, border]

    for row in rows:
        lines.append(
            "| " + " | ".join(str(row.get(header, "")).ljust(widths[idx]) for idx, header in enumerate(METRIC_HEADERS)) + " |"
        )

    lines.append(border)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_experiment_report(
    alpha: float,
    episodes: int,
    training_summary: tuple[int, int, int, int, int],
    q_table_summary: str,
    exploitation_log: str,
    output_path: Path,
) -> None:
    """Escribe el reporte completo del experimento en un archivo TXT."""
    terminales, no_terminales, sum_steps, max_steps, min_steps = training_summary

    training_table = make_table(
        headers=["terminales", "no_terminales", "prom_pasos_episodio", "max_pasos_terminales", "min_pasos_terminales"],
        rows=[[str(terminales), str(no_terminales), f"{sum_steps / episodes:.2f}" if episodes > 0 else "0.00", str(max_steps), str(min_steps)]],
    )

    report_lines = [
        "# experimento q-learning",
        f"alpha = {alpha}",
        f"episodios = {episodes}",
        f"gamma = {DEFAULT_GAMMA}",
        f"epsilon inicial = {DEFAULT_EPSILON}",
        f"epsilon mínimo = {DEFAULT_EPSILON_MIN}",
        f"epsilon decay = {DEFAULT_EPSILON_DECAY}",
        "",
        "=== resumen de entrenamiento ===",
        training_table,
        "",
        q_table_summary,
        "",
        exploitation_log,
        "",
    ]

    output_path.write_text("\n".join(report_lines), encoding="utf-8")


def train_and_analyze(alpha: float, episodes: int) -> tuple[Path, dict[str, str]]:
    """Entrena, analiza y explota un experimento específico."""
    ensure_output_dir()

    env = door_key_ball_environment()
    agent = q_learning_agent(
        env,
        alpha=alpha,
    )

    training_summary = agent.explore(episodes)
    alpha_text = format_float(alpha)
    report_path = OUTPUT_DIR / f"reporte_alpha_{alpha_text}_episodios_{episodes}.txt"
    summary_row = build_summary_row(alpha, episodes, training_summary, agent)
    q_table_summary = summarize_q_table(agent)
    exploitation_log = run_exploitation(agent)

    write_experiment_report(
        alpha=alpha,
        episodes=episodes,
        training_summary=training_summary,
        q_table_summary=q_table_summary,
        exploitation_log=exploitation_log,
        output_path=report_path,
    )

    return report_path, summary_row


def run_grid_experiments(
    alphas: Iterable[float] = DEFAULT_ALPHAS,
    episode_counts: Iterable[int] = DEFAULT_EPISODES,
) -> tuple[list[Path], list[dict[str, str]]]:
    """Ejecuta el barrido completo de hiperparámetros."""
    reports: list[Path] = []
    summary_rows: list[dict[str, str]] = []
    for episodes in episode_counts:
        for alpha in alphas:
            print(f"Entrenando con episodios={episodes} y alpha={alpha}...")
            report_path, summary_row = train_and_analyze(alpha, episodes)
            reports.append(report_path)
            summary_rows.append(summary_row)
            print(f"Reporte guardado en: {report_path}")
    return reports, summary_rows


def main() -> None:
    """Punto de entrada principal del script."""
    print("\nIniciando experimentos...")
    reports, summary_rows = run_grid_experiments()
    write_summary_txt(summary_rows, SUMMARY_TXT)
    print("\nExperimentos completados.")
    print("Archivos generados:")
    for report in reports:
        print(f"- {report}")
    print(f"- {SUMMARY_TXT}")


if __name__ == "__main__":
    main()
