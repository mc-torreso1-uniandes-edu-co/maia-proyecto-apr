from environment import door_key_ball_environment
from agent import q_learning_agent

def train(episodes=5000):
    """Entrena al agente durante la cantidad de episodios indicada.

    Args:
        episodes: Número de episodios usados para el entrenamiento.
    """
    env = door_key_ball_environment()
    agent = q_learning_agent(env)

    terminales, no_terminales, sum_steps, max_steps, min_steps = agent.explore(episodes)
    agent.save_q_table()

    print(f"Total de episodios: {episodes}")
    print(f"Episodios terminados en terminal: {terminales}")
    print(f"Episodios no terminados en terminal: {no_terminales}")
    if episodes > 0:
        print(f"Promedio de pasos por episodio: {sum_steps / episodes:.2f}")
        print(f"Mínimo de pasos en episodios terminales: {min_steps}")
        print(f"Máximo de pasos en episodios terminales: {max_steps}")
    print("Entrenamiento completado")

if __name__ == "__main__":
    train()