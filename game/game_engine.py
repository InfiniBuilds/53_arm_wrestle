import math
import random
import pygame


class GameEngine:

    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Arm position:
        # -100 = Player wins
        # +100 = Computer wins
        self.arm_position = 0.0
        self.target_limit = 100.0
        self.last_key = None

        # Player stamina
        self.stamina = 100.0
        self.max_stamina = 100.0

        self.winner = None
        self.game_state = "PLAYING"

        # -----------------------------
        # AI SETTINGS
        # -----------------------------
        self.ai_strength = 0.35
        self.normal_ai_strength = 0.35
        self.surge_ai_strength = 1.0
        self.cooldown_ai_strength = 0.15

        # AI cycle timing in milliseconds
        self.ai_state = "NORMAL"
        self.ai_state_timer = 0

        self.normal_duration = 5000
        self.surge_duration = 2000
        self.cooldown_duration = 3500

        # -----------------------------
        # COUNTER-SURGE SETTINGS
        # -----------------------------
        self.counter_surge_active = False
        self.counter_surge_timer = 0

        self.counter_window = 700
        self.counter_duration = 1500
        self.counter_push_strength = 8.4
        self.counter_recovery = 2.0

        # Used to detect when surge ends
        self.previous_ai_state = "NORMAL"

        # -----------------------------
        # FONTS
        # -----------------------------
        self.font_big = pygame.font.SysFont(None, 44)
        self.font_med = pygame.font.SysFont(None, 26)
        self.font_small = pygame.font.SysFont(None, 22)

    # =========================================================
    # INPUT
    # =========================================================

    def handle_event(self, event):

        # Rematch
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type == pygame.KEYDOWN:

            # Player is exhausted
            if self.stamina <= 10:
                return

            # ---------------------------------
            # PLAYER PUSH
            # ---------------------------------

            if event.key == pygame.K_LEFT:
                if self.last_key != pygame.K_LEFT:

                    push_strength = 4.2

                    # Counter-surge bonus
                    if self.counter_surge_active:
                        push_strength = self.counter_push_strength
                        self.stamina = min(
                            self.max_stamina,
                            self.stamina + self.counter_recovery
                        )

                    # Player pushes toward -100
                    self.arm_position -= push_strength

                    self.stamina = max(
                        0.0,
                        self.stamina - 2.0
                    )

                    self.last_key = pygame.K_LEFT

            elif event.key == pygame.K_RIGHT:
                if self.last_key != pygame.K_RIGHT:

                    push_strength = 4.2

                    # Counter-surge bonus
                    if self.counter_surge_active:
                        push_strength = self.counter_push_strength
                        self.stamina = min(
                            self.max_stamina,
                            self.stamina + self.counter_recovery
                        )

                    # Player pushes toward -100
                    self.arm_position -= push_strength

                    self.stamina = max(
                        0.0,
                        self.stamina - 2.0
                    )

                    self.last_key = pygame.K_RIGHT

    # =========================================================
    # UPDATE
    # =========================================================

    def update(self):

        if self.game_state != "PLAYING":
            return

        # Delta time in milliseconds
        dt = pygame.time.get_ticks()

        # -----------------------------------------------------
        # AI STATE MACHINE
        # -----------------------------------------------------

        current_time = pygame.time.get_ticks()

        # Initialize timer on first update
        if self.ai_state_timer == 0:
            self.ai_state_timer = current_time

        elapsed = current_time - self.ai_state_timer

        self.previous_ai_state = self.ai_state

        # NORMAL -> SURGE
        if self.ai_state == "NORMAL":

            self.ai_strength = self.normal_ai_strength

            if elapsed >= self.normal_duration:
                self.ai_state = "SURGE"
                self.ai_state_timer = current_time

        # SURGE -> COOLDOWN
        elif self.ai_state == "SURGE":

            self.ai_strength = self.surge_ai_strength

            if elapsed >= self.surge_duration:
                self.ai_state = "COOLDOWN"
                self.ai_state_timer = current_time

        # COOLDOWN -> NORMAL
        elif self.ai_state == "COOLDOWN":

            self.ai_strength = self.cooldown_ai_strength

            if elapsed >= self.cooldown_duration:
                self.ai_state = "NORMAL"
                self.ai_state_timer = current_time

        # -----------------------------------------------------
        # COUNTER-SURGE DETECTION
        # -----------------------------------------------------

        # When surge ends, open a short counter window
        if (
            self.previous_ai_state == "SURGE"
            and self.ai_state == "COOLDOWN"
        ):
            self.counter_surge_active = True
            self.counter_surge_timer = current_time

        # Counter window expires
        if self.counter_surge_active:

            counter_elapsed = (
                current_time - self.counter_surge_timer
            )

            if counter_elapsed >= self.counter_window:
                self.counter_surge_active = False

        # -----------------------------------------------------
        # AI PUSH
        # -----------------------------------------------------

        ai_variance = random.uniform(0.3, 1.0)

        self.arm_position += (
            self.ai_strength * ai_variance
        )

        # -----------------------------------------------------
        # PLAYER STAMINA RECOVERY
        # -----------------------------------------------------

        if self.stamina < self.max_stamina:

            recovery = 0.8

            # Counter-surge recovery boost
            if self.counter_surge_active:
                recovery = self.counter_recovery

            self.stamina = min(
                self.max_stamina,
                self.stamina + recovery
            )

        # -----------------------------------------------------
        # WIN / LOSS
        # -----------------------------------------------------

        if self.arm_position <= -self.target_limit:

            self.arm_position = -self.target_limit
            self.winner = "PLAYER"
            self.game_state = "GAME_OVER"

        elif self.arm_position >= self.target_limit:

            self.arm_position = self.target_limit
            self.winner = "COMPUTER"
            self.game_state = "GAME_OVER"

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):

        self.arm_position = 0.0
        self.stamina = 100.0
        self.last_key = None

        self.winner = None
        self.game_state = "PLAYING"

        # Reset AI
        self.ai_strength = self.normal_ai_strength
        self.ai_state = "NORMAL"
        self.ai_state_timer = pygame.time.get_ticks()

        self.previous_ai_state = "NORMAL"

        # Reset counter surge
        self.counter_surge_active = False
        self.counter_surge_timer = 0

    # =========================================================
    # RENDER
    # =========================================================

    def render(self, screen):

        screen.fill((25, 28, 35))

        # -----------------------------------------------------
        # TITLE
        # -----------------------------------------------------

        title_surf = self.font_big.render(
            "ARM WRESTLE SHOWDOWN",
            True,
            (240, 240, 240)
        )

        screen.blit(
            title_surf,
            (
                self.width // 2 - title_surf.get_width() // 2,
                12
            )
        )

        # -----------------------------------------------------
        # PLAYER / COMPUTER LABELS
        # -----------------------------------------------------

        player_header = self.font_med.render(
            "PLAYER",
            True,
            (80, 160, 255)
        )

        computer_header = self.font_med.render(
            "COMPUTER",
            True,
            (255, 100, 80)
        )

        screen.blit(player_header, (60, 55))
        screen.blit(
            computer_header,
            (self.width - 150, 55)
        )

        # -----------------------------------------------------
        # TABLE
        # -----------------------------------------------------

        table_rect = pygame.Rect(
            40,
            100,
            self.width - 80,
            310
        )

        pygame.draw.rect(
            screen,
            (110, 50, 15),
            table_rect,
            border_radius=14
        )

        pygame.draw.rect(
            screen,
            (70, 30, 8),
            table_rect,
            width=5,
            border_radius=14
        )

        pygame.draw.line(
            screen,
            (45, 18, 4),
            (self.width // 2, 100),
            (self.width // 2, 410),
            4
        )

        # -----------------------------------------------------
        # ARM POSITION
        # -----------------------------------------------------

        offset_x = (
            self.arm_position / self.target_limit
        ) * 95

        hand_x = (
            self.width // 2
        ) + int(offset_x)

        hand_y = 235

        p_shoulder = (70, 330)
        p_elbow = (140, 215)

        c_shoulder = (
            self.width - 70,
            330
        )

        c_elbow = (
            self.width - 140,
            215
        )

        # Player arm
        pygame.draw.line(
            screen,
            (200, 145, 110),
            p_shoulder,
            p_elbow,
            32
        )

        pygame.draw.line(
            screen,
            (215, 160, 125),
            p_elbow,
            (hand_x, hand_y),
            26
        )

        pygame.draw.circle(
            screen,
            (185, 130, 95),
            p_elbow,
            18
        )

        # Computer arm
        pygame.draw.line(
            screen,
            (170, 110, 85),
            c_shoulder,
            c_elbow,
            32
        )

        pygame.draw.line(
            screen,
            (185, 125, 95),
            c_elbow,
            (hand_x, hand_y),
            26
        )

        pygame.draw.circle(
            screen,
            (150, 95, 70),
            c_elbow,
            18
        )

        # Hands
        pygame.draw.circle(
            screen,
            (225, 175, 140),
            (hand_x, hand_y),
            24
        )

        pygame.draw.circle(
            screen,
            (160, 115, 85),
            (hand_x, hand_y),
            24,
            width=3
        )

        # -----------------------------------------------------
        # STAMINA
        # -----------------------------------------------------

        stamina_label = self.font_med.render(
            "STAMINA",
            True,
            (220, 220, 220)
        )

        screen.blit(
            stamina_label,
            (40, 445)
        )

        stamina_bg = pygame.Rect(
            140,
            448,
            240,
            22
        )

        stamina_fill = pygame.Rect(
            140,
            448,
            int(
                240 *
                (self.stamina / self.max_stamina)
            ),
            22
        )

        pygame.draw.rect(
            screen,
            (45, 50, 60),
            stamina_bg,
            border_radius=6
        )

        if self.stamina > 25:
            bar_color = (60, 210, 100)
        else:
            bar_color = (220, 60, 60)

        pygame.draw.rect(
            screen,
            bar_color,
            stamina_fill,
            border_radius=6
        )

        # -----------------------------------------------------
        # TASK 3: EXHAUSTION WARNING
        # -----------------------------------------------------

        if self.stamina <= 10:

            exhaustion_text = self.font_med.render(
                "EXHAUSTED! RECOVERING...",
                True,
                (255, 80, 80)
            )

            screen.blit(
                exhaustion_text,
                (
                    self.width // 2 -
                    exhaustion_text.get_width() // 2,
                    490
                )
            )

        # -----------------------------------------------------
        # TASK 2: AI SURGE INDICATOR
        # -----------------------------------------------------

        if self.ai_state == "SURGE":

            surge_text = self.font_med.render(
                "!!! AI POWER SURGE !!!",
                True,
                (255, 180, 50)
            )

            screen.blit(
                surge_text,
                (
                    self.width // 2 -
                    surge_text.get_width() // 2,
                    520
                )
            )

        elif self.ai_state == "COOLDOWN":

            cooldown_text = self.font_small.render(
                "AI COOLDOWN",
                True,
                (100, 220, 255)
            )

            screen.blit(
                cooldown_text,
                (
                    self.width // 2 -
                    cooldown_text.get_width() // 2,
                    520
                )
            )

        # -----------------------------------------------------
        # TASK 4: COUNTER-SURGE INDICATOR
        # -----------------------------------------------------

        if self.counter_surge_active:

            counter_text = self.font_med.render(
                "COUNTER SURGE! PUSH NOW!",
                True,
                (100, 255, 150)
            )

            screen.blit(
                counter_text,
                (
                    self.width // 2 -
                    counter_text.get_width() // 2,
                    550
                )
            )

        # -----------------------------------------------------
        # GAME OVER
        # -----------------------------------------------------

        if self.game_state == "GAME_OVER":

            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 200)
            )

            screen.blit(
                overlay,
                (0, 0)
            )

            if self.winner == "PLAYER":

                win_text = "PLAYER WINS THE MATCH!"
                color = (80, 240, 100)

            else:

                win_text = "COMPUTER WINS!"
                color = (240, 80, 80)

            text_surf = self.font_big.render(
                win_text,
                True,
                color
            )

            screen.blit(
                text_surf,
                (
                    self.width // 2 -
                    text_surf.get_width() // 2,
                    self.height // 2 - 45
                )
            )

            restart_surf = self.font_med.render(
                "Press [R] to Rematch",
                True,
                (240, 240, 240)
            )

            screen.blit(
                restart_surf,
                (
                    self.width // 2 -
                    restart_surf.get_width() // 2,
                    self.height // 2 + 10
                )
            )