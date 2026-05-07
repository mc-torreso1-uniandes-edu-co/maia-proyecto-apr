import ast
import numpy as np
import random
import pandas as pd
import time

class q_learning_agent:

    def __init__(self, env, alpha=0.1, gamma=0.95, epsilon=1.0, epsilon_min=0.1, epsilon_decay=0.995):
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
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)
        else :
            return self.best_action(state)
    
    def best_action(self, state):
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
        s = self.state_to_idx[state]
        a = self.action_to_idx[action]
        ns = self.state_to_idx[next_state]
        current_q = self.q_table[s, a]
        update_q = (1 - self.alpha) * current_q + self.alpha * (reward + self.gamma * np.max(self.q_table[ns]))

        self.q_table[s, a] = update_q

    def step(self, action):
        next_state, reward, done = self.env.do_action(self.env.current_state, action)
        self.env.current_state = next_state
        self.env.steps += 1

        if self.env.steps >= self.env.max_steps and not done:
            done = True

        return next_state, reward, done, {"step": self.env.steps}

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_q_table(self, path="q_table.csv"):
        rows = []
        for state, q_values in zip(self.states, self.q_table):
            row = {
                "STATE": str(state),
            }
            row.update({action: q_values[i] for i, action in enumerate(self.actions)})
            rows.append(row)

        pd.DataFrame(rows).to_csv(path, index=False)

    def load_q_table(self, path="q_table.csv"):
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
        count_not_terminal = 0
        count_is_terminal = 0
        sum_steps = 0

        for _ in range(episodes):

            state = self.env.reset()
            done = False
        
            while not done:
                action = self.choose_action(state)
                ns, r, done, _ = self.step(action)

                self.update_values(state, action, r, ns)
                state = ns
            if self.env.is_terminal(state):
                count_is_terminal += 1
                sum_steps += self.  env.steps
            else :
                count_not_terminal += 1

        self.save_q_table()
        return count_is_terminal, count_not_terminal, sum_steps

    def explode(self, render_func=None, step_delay=1.0):
        state = self.env.reset()
        done = False

        if render_func is not None:
            render_func(state)

        while not done:
            action = self.choose_action(state)
            ns, r, done, info = self.step(action)

            print(f"Paso {info['step']} | {state} -> {action} -> {ns} | R={r}")

            state = ns
            if render_func is not None:
                render_func(state)

            time.sleep(step_delay)

        if render_func is not None:
            render_func(state)
