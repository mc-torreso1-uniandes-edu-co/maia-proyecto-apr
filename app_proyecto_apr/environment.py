from itertools import product
import pandas as pd

class door_key_ball_environment:
    """
    Ambiente RL del proyecto:
    Estado: S = (R, C, KP, BP, DO)

    R  = fila del agente
    C  = columna del agente
    KP = llave recogida
    BP = bola recogida
    DO = puerta abierta
    """

    def __init__(
        self,
        board=((1, 4), (1, 9)),
        walls=((1, 5), (2, 5), (3, 5)),
        door=(4, 5),
        key=(2, 4),
        ball=(4, 4),
        exit=(1, 7),
        initial_state=(3, 1, 0, 0, 0),
        max_steps=1000,
    ):
        self.board = board
        (self.min_row, self.max_row), (self.min_col, self.max_col) = board

        self.walls = set(walls)
        self.door = door
        self.key = key
        self.ball = ball
        self.exit = exit

        door_col = self.door[1]
        wall_cols = sorted({col for _, col in self.walls})
        if door_col in wall_cols:
            separator_col = door_col
        elif wall_cols:
            separator_col = wall_cols[0]
        else:
            separator_col = door_col

        self.left_room_cols = set(range(self.min_col, separator_col))
        self.right_room_cols = set(range(separator_col + 1, self.max_col + 1))
        self.right_rooms_col = self.right_room_cols

        self.initial_state = initial_state
        self.current_state = self.initial_state
        self.max_steps = max_steps
        self.steps = 0

        self.actions = [
            "UP",
            "DOWN",
            "RIGHT",
            "LEFT",
            "PICK_OBJECT",
            "OPEN_DOOR",
        ]

        self.rewards = {
            "PICK_KEY": 3,
            "PICK_BALL": 2,
            "OPEN_DOOR": 5,
            "EXIT": 15,
            "CROSS_TO_RIGHT_ROOM": 1,
            "RETURN_TO_DOOR": -2,
            "RIGHT_FROM_CLOSED_DOOR": -1,
            "INVALID_OPEN_DOOR": -3,
            "INVALID_MOVE": -0.1,
            "VALID_MOVE_LEFT_ROOM": -0.02,
            "VALID_MOVE_RIGHT_ROOM": -0.01,
            "VALID_MOVE_DOOR": -0.01,
            "INVALID_PICK_OBJECT": -0.1,
            "TERMINAL": 0,
        }

    def in_board(self, row, col):
        return (
            self.min_row <= row <= self.max_row
            and self.min_col <= col <= self.max_col
        )

    def is_wall(self, row, col):
        return (row, col) in self.walls

    def is_door(self, row, col):
        return (row, col) == self.door

    def is_exit(self, row, col):
        return (row, col) == self.exit

    def is_terminal(self, state):
        row, col, *_ = state
        return self.is_exit(row, col)

    def is_valid_agent_position(self, state):
        row, col, *_ = state

        if not self.in_board(row, col):
            return False

        if self.is_wall(row, col):
            return False

        return True

    def get_currente_statet(self):
        return self.current_state

    def state_value(self, state=None):
        if state is None:
            state = self.current_state

        if self.is_terminal(state):
            return self.rewards["EXIT"]

        return 0

    def get_possible_actions(self, state):
        row, col, kp, bp, do = state
        possible_actions = []
        
        if self.is_terminal(state):
            return possible_actions
        
        moves = [
            ("UP", row - 1, col),
            ("DOWN", row + 1, col),
            ("RIGHT", row, col + 1),
            ("LEFT", row, col - 1),
        ]
        
        for action_name, new_row, new_col in moves:
            if self.in_board(new_row, new_col) and not self.is_wall(new_row, new_col):
                if not ((row, col) == self.door and action_name == "RIGHT" and do == 0):
                    possible_actions.append(action_name)
        
        if ((row, col) == self.key and kp == 0) or \
           ((row, col) == self.ball and kp == 1 and bp == 0):
            possible_actions.append("PICK_OBJECT")
        
        if (row, col) == self.door and kp == 1 and bp == 1 and do == 0:
            possible_actions.append("OPEN_DOOR")
        
        return possible_actions

    def get_action_index(self, action):
        index = 0
        for a in self.actions:
            if a == action:
                return index
            index += 1
        raise ValueError(f"Acción no reconocida: {action}")

    def get_possible_states(self, state, action):
        next_state, reward, done = self.do_action(state, action)
        return [(next_state, reward, done)]

    def reset(self):
        self.current_state = self.initial_state
        self.steps = 0
        return self.current_state

    def step_current(self, action):
        next_state, reward, done = self.do_action(self.current_state, action)
        self.current_state = next_state
        self.steps += 1

        if self.steps >= self.max_steps and not done:
            done = True

        return next_state, reward, done, {"step": self.steps}

    def do_action(self, state, action):
        row, col, *_ = state

        if self.is_terminal(state):
            return state, self.rewards["TERMINAL"], True

        if action == "UP":
            next_state, reward = self.do_move(state, row - 1, col, action)

        elif action == "DOWN":
            next_state, reward = self.do_move(state, row + 1, col, action)

        elif action == "RIGHT":
            next_state, reward = self.do_move(state, row, col + 1, action)

        elif action == "LEFT":
            next_state, reward = self.do_move(state, row, col - 1, action)

        elif action == "PICK_OBJECT":
            next_state, reward = self.do_pick_object(state)

        elif action == "OPEN_DOOR":
            next_state, reward = self.do_open_door(state)

        else:
            raise ValueError(f"Acción no reconocida: {action}")

        if self.is_terminal(next_state):
            return next_state, self.rewards["EXIT"], True

        return next_state, reward, False

    def do_move(self, state, new_row, new_col, action):
        row, col, kp, bp, do = state

        if not self.in_board(new_row, new_col):
            return state, self.rewards["INVALID_MOVE"]

        if self.is_wall(new_row, new_col):
            return state, self.rewards["INVALID_MOVE"]

        # Regla específica: desde puerta cerrada hacia la derecha es inválido.
        if (row, col) == self.door and action == "RIGHT" and do == 0:
            return state, self.rewards["RIGHT_FROM_CLOSED_DOOR"]

        next_state = (new_row, new_col, kp, bp, do)

        # Cruzar desde la puerta abierta hacia habitación derecha.
        if (row, col) == self.door and (new_row, new_col) == (4, 6) and do == 1:
            return next_state, self.rewards["CROSS_TO_RIGHT_ROOM"]

        # Regresar desde habitación derecha a la puerta.
        if (row, col) == (4, 6) and (new_row, new_col) == self.door and do == 1:
            return next_state, self.rewards["RETURN_TO_DOOR"]

        if col in self.left_room_cols:
            return next_state, self.rewards["VALID_MOVE_LEFT_ROOM"]

        if col in self.right_room_cols:
            return next_state, self.rewards["VALID_MOVE_RIGHT_ROOM"]

        if (row, col) == self.door:
            return next_state, self.rewards["VALID_MOVE_DOOR"]

        return next_state, self.rewards["VALID_MOVE_RIGHT_ROOM"]

    def do_pick_object(self, state):
        row, col, kp, bp, do = state

        # Recoger llave.
        if (row, col) == self.key and kp == 0:
            next_state = (row, col, 1, bp, do)
            return next_state, self.rewards["PICK_KEY"]

        # Recoger bola. requiere KP=1.
        if (row, col) == self.ball and kp == 1 and bp == 0:
            next_state = (row, col, kp, 1, do)
            return next_state, self.rewards["PICK_BALL"]

        return state, self.rewards["INVALID_PICK_OBJECT"]

    def do_open_door(self, state):
        row, col, kp, bp, do = state

        if (row, col) == self.door and kp == 1 and bp == 1 and do == 0:
            next_state = (row, col, kp, bp, 1)
            return next_state, self.rewards["OPEN_DOOR"]

        return state, self.rewards["INVALID_OPEN_DOOR"]

    def get_states(self):
        states = []

        for row, col, kp, bp, do in product(
            range(self.min_row, self.max_row + 1),
            range(self.min_col, self.max_col + 1),
            [0, 1],
            [0, 1],
            [0, 1],
        ):
            state = (row, col, kp, bp, do)

            if self.is_valid_agent_position(state):
                states.append(state)

        return states

    def generate_transition_table(self):
        rows = []

        for state in self.get_states():
            for action in self.actions:
                next_state, reward, done = self.do_action(state, action)

                rows.append({
                    "S": state,
                    "A": action,
                    "NS": next_state,
                    "P": 1.0,
                    "R": reward,
                    "Terminal": done,
                })

        return pd.DataFrame(rows)

    def describe(self):
        return {
            "state": "(R, C, KP, BP, DO)",
            "initial_state": self.initial_state,
            "exit": self.exit,
            "key": self.key,
            "ball": self.ball,
            "door": self.door,
            "walls": self.walls,
            "actions": self.actions,
            "max_steps": self.max_steps,
            "rewards": self.rewards,
        }