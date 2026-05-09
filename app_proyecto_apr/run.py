from environment import door_key_ball_environment
from agent import q_learning_agent
import time


def render(state):
    """Imprime una representación ASCII del estado actual del tablero.

    Args:
        state: Estado del agente en formato (R, C, KP, BP, DO).
    """

    grid = [["." for _ in range(9)] for _ in range(4)]

    r, c, kp, bp, do = state

    grid[r-1][c-1] = "A"
    grid[1][3] = "K" if kp == 0 else "*"
    grid[3][3] = "B" if bp == 0 else "*"
    grid[3][4] = "D" if do == 0 else "O"
    grid[0][6] = "E"

    for w in [(0,4),(1,4),(2,4)]:
        grid[w[0]][w[1]] = "#"

    print("\n".join([" ".join(row) for row in grid]))
    print("-"*20)

def run():
    """Carga la Q-table y ejecuta una demostración en consola."""
    env = door_key_ball_environment()
    agent = q_learning_agent(env)

    try:
        agent.load_q_table()
        print("Q-table cargada correctamente.")
    except FileNotFoundError:
        print("Advertencia: no se encontró q_table.csv. Ejecuta train.py para entrenar el agente.")
    agent.epsilon = 0

    agent.explode(render_func=render, step_delay=3.0)
    print("¡Episodio terminado!")


if __name__ == "__main__":
    run()
