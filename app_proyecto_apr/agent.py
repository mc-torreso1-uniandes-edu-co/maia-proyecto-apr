import ast
import numpy as np
import random
import pandas as pd
import time

class q_learning_agent:
    """Agente Q-learning que aprende una política a partir del entorno.

    El agente mantiene una Q-table indexada por estado y acción, y ofrece
    utilidades para explorar, actualizar valores, guardar y cargar el modelo
    aprendido.
    """

    def __init__(self, env, alpha=0.1, gamma=0.95, epsilon=1.0, epsilon_min=0.1, epsilon_decay=0.995):
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
    
    def choose_action(self, state):
        """Selecciona una acción usando exploración epsilon-greedy.

        Args:
            state: Estado actual del entorno.
        """
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)
        else :
            return self.best_action(state)
    
    def best_action(self, state):
        """Devuelve la mejor acción conocida evitando movimientos que no cambian el estado.

        Args:
            state: Estado desde el que se evalúan las acciones.
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

    def update_values(self, state, action, reward, next_state):
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

    def step(self, action):
        """Ejecuta una acción en el entorno y devuelve la transición obtenida.

        Args:
            action: Acción a ejecutar en el estado actual del entorno.
        """
        next_state, reward, done = self.env.do_action(self.env.current_state, action)
        self.env.current_state = next_state
        self.env.steps += 1

        if self.env.steps >= self.env.max_steps and not done:
            done = True

        return next_state, reward, done, {"step": self.env.steps}

    def decay_epsilon(self):
        """Reduce gradualmente la tasa de exploración."""
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_q_table(self, path="q_table.csv"):
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

    def load_q_table(self, path="q_table.csv"):
        """Carga la Q-table desde CSV, soportando varios formatos históricos.

        Args:
            path: Ruta del archivo CSV de entrada.
        """
        df = pd.read_csv(path)

        if "STATE" in df.columns:
            q = np.zeros((len(self.states), len(self.actions)))
            for _, row in df.iterrows():
                state = ast.literal_eval(row["STATE"])
                if state in self.state_to_idx:
                    s_idx = self.state_to_idx[state]
                    for i, action in enumerate(self.actions):
                        q[s_idx, i] = float(row[action])
            self.q_table = q
            return

        state_columns = ["R", "C", "KP", "BP", "DO"]

        if all(col in df.columns for col in state_columns):
            q = np.zeros((len(self.states), len(self.actions)))
            for _, row in df.iterrows():
                state = tuple(int(row[col]) for col in state_columns)
                if state in self.state_to_idx:
                    s_idx = self.state_to_idx[state]
                    for i, action in enumerate(self.actions):
                        q[s_idx, i] = float(row[action])
            self.q_table = q
        else:
            self.q_table = df.to_numpy(dtype=float)

    def explore(self, episodes):
        """Entrena al agente durante varios episodios.

        Args:
            episodes: Número de episodios de entrenamiento.
        """
        count_terminal = 0
        count_non_terminal = 0
        sum_steps = 0
        max_steps_terminal = 0
        min_steps_terminal = 0

        for _ in range(episodes):

            state = self.env.reset()
            done = False
        
            while not done:
                action = self.choose_action(state)
                ns, r, done, _ = self.step(action)

                self.update_values(state, action, r, ns)
                state = ns

            if self.env.is_terminal(state):
                count_terminal += 1
                if self.env.steps > max_steps_terminal:
                    max_steps_terminal = self.env.steps
                if min_steps_terminal == 0 or self.env.steps < min_steps_terminal:
                    min_steps_terminal = self.env.steps
            else:
                count_non_terminal += 1

            sum_steps += self.env.steps
            
            self.decay_epsilon()

        #self.save_q_table()
        return count_terminal, count_non_terminal, sum_steps, max_steps_terminal, min_steps_terminal

    def explode(self, render_func=None, step_delay=1.0):
        """Ejecuta un episodio en modo demostración imprimiendo cada transición.

        Args:
            render_func: Función opcional para dibujar o imprimir el estado.
            step_delay: Tiempo de espera entre pasos, en segundos.
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
