import ast
import numpy as np
import random
import pandas as pd
import time
from pathlib import Path
from typing import Callable
from environment import door_key_ball_environment

class q_learning_agent:
    """Agente Q-learning que aprende una política a partir del entorno.

    El agente mantiene una Q-table indexada por estado y acción, y ofrece
    utilidades para seleccionar acciones, actualizar valores, guardar y
    cargar el modelo aprendido, además de registrar historial de entrenamiento
    y ejecutar demostraciones paso a paso.
    """

    def __init__(self, env: door_key_ball_environment, alpha: float = 0.1, gamma: float = 0.95, epsilon: float = 1.0, epsilon_min: float = 0.1, epsilon_decay: float = 0.995) -> None:
        """Inicializa el agente con hiperparámetros y la tabla Q vacía.

        Args:
            env: Entorno con el que interactúa el agente.
            alpha: Tasa de aprendizaje.
            gamma: Factor de descuento para recompensas futuras.
            epsilon: Probabilidad inicial de exploración.
            epsilon_min: Valor mínimo permitido para epsilon.
            epsilon_decay: Factor de decaimiento de epsilon.
        """
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        self.states = env.get_states()
        self.actions = env.actions

        self.state_to_idx = {s: i for i, s in enumerate(self.states)}
        self.action_to_idx = {a: i for i, a in enumerate(self.actions)}

        self.q_table = np.zeros((len(self.states), len(self.actions)))
    
    def choose_action(self, state: tuple[int, int, int, int, int]) -> str:
        """Selecciona una acción usando exploración epsilon-greedy.

        Args:
            state: Estado actual del entorno.

        Returns:
            Nombre de la acción seleccionada.
        """
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)
        else :
            return self.best_action(state)
    
    def best_action(self, state: tuple[int, int, int, int, int]) -> str:
        """Devuelve la mejor acción conocida evitando acciones sin progreso.

        Args:
            state: Estado desde el que se evalúan las acciones.

        Returns:
            Acción con mayor valor Q que no deje el estado sin cambios,
            cuando exista una alternativa mejor.
        """
        s_idx = self.state_to_idx[state]
        action_indexes = list(range(len(self.actions)))
        action_indexes.sort(key=lambda idx: self.q_table[s_idx, idx], reverse=True)

        for idx in action_indexes:
            action = self.actions[idx]
            next_state, _, _ = self.env.do_action(state, action)
            if next_state != state:
                return action

        return self.actions[action_indexes[0]]

    def update_values(self, state: tuple[int, int, int, int, int], action: str, reward: float, next_state: tuple[int, int, int, int, int]) -> None:
        """Actualiza la Q-table con la regla clásica de Q-learning.

        Args:
            state: Estado actual.
            action: Acción ejecutada.
            reward: Recompensa observada.
            next_state: Estado siguiente alcanzado.
        """
        s = self.state_to_idx[state]
        a = self.action_to_idx[action]
        ns = self.state_to_idx[next_state]
        current_q = self.q_table[s, a]
        update_q = (1 - self.alpha) * current_q + self.alpha * (reward + self.gamma * np.max(self.q_table[ns]))

        self.q_table[s, a] = update_q

    def step(self, action: str) -> tuple[tuple[int, int, int, int, int], float, bool, dict[str, int]]:
        """Ejecuta una acción en el entorno y devuelve la transición obtenida.

        Args:
            action: Acción a ejecutar en el estado actual del entorno.

        Returns:
            Tupla con `next_state`, `reward`, `done` e información del paso.
        """
        next_state, reward, done = self.env.do_action(self.env.current_state, action)
        self.env.current_state = next_state
        self.env.steps += 1

        if self.env.steps >= self.env.max_steps and not done:
            done = True

        return next_state, reward, done, {"step": self.env.steps}

    def decay_epsilon(self) -> None:
        """Reduce gradualmente la tasa de exploración hasta `epsilon_min`.

        Returns:
            None. Solo actualiza `self.epsilon` si todavía está por encima
            del mínimo configurado.
        """
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_q_table(self, path: str = "q_table.csv") -> None:
        """Guarda la Q-table en un archivo CSV legible por pandas.

        Args:
            path: Ruta del archivo CSV de salida.
        """
        rows = []
        for state, q_values in zip(self.states, self.q_table):
            row = {
                "STATE": str(state),
            }
            row.update({action: q_values[i] for i, action in enumerate(self.actions)})
            rows.append(row)

        pd.DataFrame(rows).to_csv(path, index=False)

    def load_q_table(self, path: str = "q_table.csv") -> None:
        """Carga la Q-table desde CSV.

        Args:
            path: Ruta del archivo CSV de entrada.

        Behavior:
            Acepta con columna `STATE` y columnas de acciones. 
            Solo carga estados que existen en el entorno y asigna 
            los valores Q correspondientes.
        """
        df = pd.read_csv(path)

        if "STATE" in df.columns:
            q = np.zeros((len(self.states), len(self.actions)))
            for _, row in df.iterrows():
                state: tuple[int, int, int, int, int] = ast.literal_eval(row["STATE"])
                if state in self.state_to_idx:
                    s_idx = self.state_to_idx[state]
                    for i, action in enumerate(self.actions):
                        q[s_idx, i] = float(row[action])
            self.q_table = q


    def explore(self, episodes: int, track: bool = False) -> tuple[int, int, int, int, int]:
        """Entrena al agente durante varios episodios.

        Args:
            episodes: Número de episodios de entrenamiento.
            track: Si es True, registra el historial de entrenamiento.

        Returns:
            Una tupla con: episodios terminales, episodios no terminales, suma
            de pasos, máximo de pasos terminales y mínimo de pasos terminales.
        """
        count_terminal = 0
        count_non_terminal = 0
        sum_steps = 0
        max_steps_terminal = 0
        min_steps_terminal = 0
        # registro por episodio para análisis / curvas de aprendizaje
        episode_rewards: list[float] = []
        episode_steps: list[int] = []
        episode_eps: list[float] = []

        for e in range(episodes):

            state = self.env.reset()
            done = False
            episode_reward = 0.0

            # registrar epsilon al inicio del episodio
            episode_eps.append(self.epsilon)
        
            while not done:
                action = self.choose_action(state)
                ns, r, done, _ = self.step(action)

                self.update_values(state, action, r, ns)
                state = ns
                episode_reward += float(r)

            terminal = self.env.is_terminal(state)


            if terminal:
                count_terminal += 1
                if self.env.steps > max_steps_terminal:
                    max_steps_terminal = self.env.steps
                if min_steps_terminal == 0 or self.env.steps < min_steps_terminal:
                    min_steps_terminal = self.env.steps
            else:
                count_non_terminal += 1

            if track:    
                color = "\033[92m" if terminal else "\033[91m"  # verde si terminal, rojo si no
                print(f"{color}episodio: {e + 1:>3} | recompensa: {episode_reward:>+7.2f} | pasos: {self.env.steps:>4} | epsilon: {self.epsilon:.4f} | terminal:{terminal}\033[0m")
                time.sleep(0.1)

            sum_steps += self.env.steps
            episode_rewards.append(episode_reward)
            episode_steps.append(int(self.env.steps))
            
            self.decay_epsilon()

        #self.save_q_table()
        # guardar historial de entrenamiento para análisis externo
        try:
            base = Path(__file__).resolve().parent
            out_dir = base / "experiment_results"
            out_dir.mkdir(parents=True, exist_ok=True)
            hist_path = out_dir / "training_history.csv"
            pd.DataFrame({
                "episode": list(range(1, len(episode_rewards) + 1)),
                "reward": episode_rewards,
                "steps": episode_steps,
                "epsilon": episode_eps,
            }).to_csv(hist_path, index=False)
        except Exception:
            pass
        
        return count_terminal, count_non_terminal, sum_steps, max_steps_terminal, min_steps_terminal

    def explode(self, render_func: Callable[[tuple[int, int, int, int, int]], None] | None = None, step_delay: float = 1.0) -> list[tuple[tuple[int, int, int, int, int], str, tuple[int, int, int, int, int], float, float, bool]]:
        """Ejecuta un episodio en modo demostración imprimiendo cada transición.

        Args:
            render_func: Función opcional para dibujar o imprimir el estado.
            step_delay: Tiempo de espera entre pasos, en segundos.

        Returns:
            Lista de transiciones con estado, acción, siguiente estado,
            recompensa acumulada y marca de término.
        """
        state = self.env.reset()
        done = False
        result = []
        reward = 0

        if render_func is not None:
            render_func(state)

        while not done:
            action = self.choose_action(state)
            ns, r, done, info = self.step(action)
            reward += r

            print(f"Paso {info['step']} | {state} -> {action} -> {ns} | R={r}")
            result.append((state, action, ns, r, reward, done))

            state = ns
            if render_func is not None:
                render_func(state)

            time.sleep(step_delay)

        if render_func is not None:
            render_func(state)
        
        return result
