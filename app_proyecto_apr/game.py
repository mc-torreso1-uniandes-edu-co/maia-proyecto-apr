import pygame
import time
from environment import door_key_ball_environment
from agent import q_learning_agent


class rl_game_app:

    def __init__(self):
        pygame.init()

        self.sum_reward = 0
        self.env = door_key_ball_environment()
        self.agent = q_learning_agent(self.env)
        self.q_table_loaded = True
        try:
            self.agent.load_q_table()
            print("Q-table cargada correctamente.")
        except FileNotFoundError:
            self.q_table_loaded = False
            print("Advertencia: no se encontró q_table.csv. Ejecuta train.py para entrenar el agente.")
        self.agent.epsilon = 0  # explotación

        self.cell_size = 80
        self.rows = 4
        self.cols = 9
        self.panel_height = 120

        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size + self.panel_height

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Proyecto Aprendizaje por Refuerzo - 202612 - Team 30")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 14)
        self.big_font = pygame.font.SysFont("consolas", 28, bold=True)

        self.reset()
        self.started = False

        self.colors = {
            "bg": (80, 80, 80),
            "grid": (180, 180, 180),
            "wall": (30, 30, 30),
            "door_closed": (40, 90, 200),
            "door_open": (80, 80, 80),
            "key": (40, 90, 200),
            "ball": (220, 50, 50),
            "exit": (40, 90, 200),
            "agent": (220, 50, 50),
            "text": (20, 20, 20),
            "panel": (230, 230, 230),
        }

    def reset(self):
        self.state = self.env.reset()
        self.done = False
        self.last_state = None
        self.last_action = None
        self.last_reward = 0
        self.last_next_state = None
        self.step_count = 0
        self.sum_reward = 0

    def cell_rect(self, r, c):
        return pygame.Rect(
            (c - 1) * self.cell_size,
            (r - 1) * self.cell_size,
            self.cell_size,
            self.cell_size
        )

    def draw_grid(self):
        self.screen.fill(self.colors["bg"])
        for r in range(1, self.rows + 1):
            for c in range(1, self.cols + 1):
                rect = self.cell_rect(r, c)
                pygame.draw.rect(self.screen, self.colors["grid"], rect, 1)

    def draw_static(self):
        _, _, kp, bp, do = self.state

        # paredes
        for w in self.env.walls:
            pygame.draw.rect(self.screen, self.colors["wall"], self.cell_rect(*w))

        # puerta
        color = self.colors["door_open"] if do else self.colors["door_closed"]
        pygame.draw.rect(self.screen, color, self.cell_rect(*self.env.door))
        self.draw_text_center("D", self.env.door, (255, 255, 255))

        # llave
        if kp == 0:
            self.draw_text_center("K", self.env.key, (255, 255, 255), self.colors["key"])

        # bola
        if bp == 0:
            self.draw_text_center("B", self.env.ball, (255, 255, 255), self.colors["ball"])

        # salida
        pygame.draw.rect(self.screen, self.colors["exit"], self.cell_rect(*self.env.exit))
        self.draw_text_center("E", self.env.exit, (255, 255, 255))

    def draw_agent(self):
        r, c, *_ = self.state
        rect = self.cell_rect(r, c)
        pygame.draw.polygon(self.screen, self.colors["agent"], [
            (rect.centerx, rect.bottom - 10),
            (rect.right - 10, rect.top + 15),
            (rect.left + 10, rect.top + 15),
        ])
        self.draw_text_center("A", (r, c), (255, 255, 255))

    def draw_panel(self):
        y = self.rows * self.cell_size
        pygame.draw.rect(self.screen, self.colors["panel"], (0, y, self.width, self.panel_height))

        if self.started:
            if self.last_state is None:
                status = f" initial state:{str(self.state)}"
            else :
                estado = str(self.last_state)
                nuevo_estado = str(self.last_next_state)
                accion = str(self.last_action)
                try:
                    rv = float(self.last_reward)
                except Exception:
                    rv = 0.0
                recompensa = f"{rv:+6.2f}"

                try:
                    rv = float(self.sum_reward)
                except Exception:
                    rv = 0.0
                suma_recompensa = f"{rv:+6.2f}"

                status = (
                    f"{self.env.steps:>2}- state:{estado:>15.15}-->{nuevo_estado:>15.15}" 
                    f" action:{accion:<11.11} reward:{recompensa:>6}-->{suma_recompensa:>6}"
                )

            if not self.q_table_loaded:
                status += " Q-table no cargada: entrena con train.py"

            surface = self.font.render(status, True, self.colors["text"])
            status_rect = surface.get_rect(midleft=(2, y + self.panel_height - 20))
            self.screen.blit(surface, status_rect)
        else:
            surface = self.big_font.render("ESPACIO para iniciar ESC para salir", True, self.colors["text"])
            prompt_rect = surface.get_rect(center=(self.width // 2, y + self.panel_height // 2))
            self.screen.blit(surface, prompt_rect)

        if self.done:
            msg = "OBJETIVO ALCANZADO" if self.env.is_terminal(self.state) else "FIN"
            surface = self.big_font.render(msg, True, (0, 120, 0))
            msg_rect = surface.get_rect(midtop=(self.width // 2, y + 6))
            self.screen.blit(surface, msg_rect)

            surface = self.big_font.render("ESPACIO para reiniciar ESC para salir", True, self.colors["text"])
            prompt_rect = surface.get_rect(center=(self.width // 2, y + self.panel_height // 2))
            self.screen.blit(surface, prompt_rect)

    def draw_text_center(self, text, pos, color, bg=None):
        r, c = pos
        rect = self.cell_rect(r, c)
        if bg:
            pygame.draw.circle(self.screen, bg, rect.center, 30)

        surface = self.big_font.render(text, True, color)
        text_rect = surface.get_rect(center=rect.center)
        self.screen.blit(surface, text_rect)

    def step_forward(self):
        if self.done:
            return
        s = self.state
        a = self.agent.choose_action(s)
        ns, r, done, info = self.agent.step(a)

        self.last_state = s
        self.last_action = a
        self.last_reward = r
        self.last_next_state = ns
        self.sum_reward += r

        self.state = ns
        self.done = done
        self.step_count = info["step"]

        print(
             f"Paso {info['step']:<2} | Acción: {a:<11.11} | Estado: {ns} | Recompensa: {r:+6.2f} | Suma: {self.sum_reward:+6.2f} | Done: {done}"
        )

    def render(self, state=None):
        if state is not None:
            self.state = state

        self.done = self.env.is_terminal(self.state)
        self.draw_grid()
        self.draw_static()
        self.draw_agent()
        self.draw_panel()
        pygame.display.flip()
        pygame.event.pump()

    def run(self, step_interval = 5.0):
        self.agent.epsilon = 0
        self.reset()
        self.started = False

        running = True
        auto_running = False
        last_step_time = time.time()

        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_SPACE:
                            if self.done:
                                self.reset()
                                self.started = True
                                auto_running = True
                                last_step_time = time.time()
                            elif not self.started:
                                self.started = True
                                auto_running = True
                                last_step_time = time.time()
                            else:
                                auto_running = not auto_running

                if self.started and auto_running and not self.done:
                    now = time.time()
                    if (now - last_step_time) >= step_interval:
                        self.step_forward()
                        last_step_time = now

                self.render(self.state)
                self.clock.tick(30)
        finally:
            pygame.quit()

if __name__ == "__main__":
    app = rl_game_app()
    app.run(step_interval=5.0)