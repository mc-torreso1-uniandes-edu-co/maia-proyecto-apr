from environment import door_key_ball_environment
from agent import q_learning_agent

def train(episodes=5000):
    env = door_key_ball_environment()
    agent = q_learning_agent(env)

    t, nt, s = agent.explore(episodes)

    print(f"Total de episodios: {episodes}")
    print(f"Episodios terminados en terminal: {t}")
    print(f"Episodios no terminados en terminal: {nt}")
    if t > 0:
        print(f"Promedio de pasos para episodios terminales: {s / t:.2f}")
    print("Entrenamiento completado")

if __name__ == "__main__":
    train()