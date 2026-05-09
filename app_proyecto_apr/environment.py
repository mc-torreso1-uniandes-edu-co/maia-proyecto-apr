from itertools import product
import pandas as pd

class door_key_ball_environment:
    """Entorno de aprendizaje por refuerzo del proyecto puerta-llave-bola.

    El estado se representa como S = (R, C, KP, BP, DO), donde:
    R  = fila del agente.
    C  = columna del agente.
    KP = llave recogida.
    BP = bola recogida.
    DO = puerta abierta.
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
        """Inicializa el tablero, los objetos, las recompensas y el estado actual.

        Args:
            board: Límites del tablero como ((fila_min, fila_max), (col_min, col_max)).
            walls: Celdas que representan paredes.
            door: Posición de la puerta.
            key: Posición de la llave.
            ball: Posición de la bola.
            exit: Posición de la salida.
            initial_state: Estado inicial del agente.
            max_steps: Número máximo de pasos por episodio.
        """
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
        """Indica si una posición está dentro de los límites del tablero.

        Args:
            row: Fila a validar.
            col: Columna a validar.
        """
        return (
            self.min_row <= row <= self.max_row
            and self.min_col <= col <= self.max_col
        )

    def is_wall(self, row, col):
        """Indica si una celda corresponde a una pared.

        Args:
            row: Fila de la celda.
            col: Columna de la celda.
        """
        return (row, col) in self.walls

    def is_door(self, row, col):
        """Indica si una celda corresponde a la puerta.

        Args:
            row: Fila de la celda.
            col: Columna de la celda.
        """
        return (row, col) == self.door

    def is_exit(self, row, col):
        """Indica si una celda corresponde a la salida.

        Args:
            row: Fila de la celda.
            col: Columna de la celda.
        """
        return (row, col) == self.exit

    def is_terminal(self, state):
        """Indica si el estado actual ya llegó a la salida.

        Args:
            state: Estado del agente en formato (R, C, KP, BP, DO).
        """
        row, col, *_ = state
        return self.is_exit(row, col)

    def is_valid_agent_position(self, state):
        """Valida que la posición del agente sea una celda transitable.

        Args:
            state: Estado del agente en formato (R, C, KP, BP, DO).
        """
        row, col, *_ = state

        if not self.in_board(row, col):
            return False

        if self.is_wall(row, col):
            return False

        return True

    def get_currente_statet(self):
        """Retorna el estado actual almacenado en el entorno."""
        return self.current_state

    def state_value(self, state=None):
        """Retorna el valor inmediato del estado si es terminal.

        Args:
            state: Estado a evaluar. Si es None, usa el estado actual.
        """
        if state is None:
            state = self.current_state

        if self.is_terminal(state):
            return self.rewards["EXIT"]

        return 0

    def get_possible_actions(self, state):
        """Devuelve las acciones válidas desde un estado dado.

        Args:
            state: Estado del agente en formato (R, C, KP, BP, DO).
        """
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
        """Obtiene el índice de una acción dentro de la lista de acciones.

        Args:
            action: Nombre de la acción.
        """
        index = 0
        for a in self.actions:
            if a == action:
                return index
            index += 1
        raise ValueError(f"Acción no reconocida: {action}")

    def get_possible_states(self, state, action):
        """Retorna el estado sucesor posible para una acción dada.

        Args:
            state: Estado de origen.
            action: Acción a evaluar.
        """
        next_state, reward, done = self.do_action(state, action)
        return [(next_state, reward, done)]

    def reset(self):
        """Reinicia el entorno al estado inicial y pone el contador en cero."""
        self.current_state = self.initial_state
        self.steps = 0
        return self.current_state

    def step_current(self, action):
        """Aplica una acción sobre el estado actual y avanza el entorno.

        Args:
            action: Acción a ejecutar.
        """
        next_state, reward, done = self.do_action(self.current_state, action)
        self.current_state = next_state
        self.steps += 1

        if self.steps >= self.max_steps and not done:
            done = True

        return next_state, reward, done, {"step": self.steps}

    def do_action(self, state, action):
        """Ejecuta una acción arbitraria sobre un estado dado.

        Args:
            state: Estado de partida.
            action: Acción a ejecutar.
        """
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
        """Procesa un movimiento del agente y asigna la recompensa correspondiente.

        Args:
            state: Estado de partida.
            new_row: Fila destino.
            new_col: Columna destino.
            action: Acción de movimiento ejecutada.
        """
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
        """Procesa la acción de recoger un objeto si la condición es válida.

        Args:
            state: Estado del agente.
        """
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
        """Intenta abrir la puerta cuando se cumplen las precondiciones.

        Args:
            state: Estado del agente.
        """
        row, col, kp, bp, do = state

        if (row, col) == self.door and kp == 1 and bp == 1 and do == 0:
            next_state = (row, col, kp, bp, 1)
            return next_state, self.rewards["OPEN_DOOR"]

        return state, self.rewards["INVALID_OPEN_DOOR"]

    def get_states(self):
        """Genera todos los estados válidos del espacio de estados."""
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
        """Construye una tabla de transiciones determinista para todo el entorno."""
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
        """Devuelve un resumen legible de la configuración del entorno."""
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