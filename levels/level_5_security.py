import pygame
from settings import *


class Level5:
    def __init__(self, screen):
        self.screen = screen

        # --- FONT YÖNETİMİ ---
        try:
            self.font_term = pygame.font.SysFont("Consolas", 18)
            self.font_header = pygame.font.SysFont("Impact", 30)
            self.font_ui = pygame.font.SysFont("Arial", 16)
            self.font_ui_bold = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_big = pygame.font.SysFont("Arial", 60, bold=True)
            self.font_small = pygame.font.SysFont("Consolas", 14)
        except:
            self.font_term = pygame.font.SysFont(None, 24)
            self.font_header = pygame.font.SysFont(None, 40)
            self.font_ui = pygame.font.SysFont(None, 20)
            self.font_ui_bold = pygame.font.SysFont(None, 20, bold=True)
            self.font_big = pygame.font.SysFont(None, 60)
            self.font_small = pygame.font.SysFont(None, 18)

        self.completed = False
        self.timer = 0
        self.anim_scale = 0

        # --- ROUTER DURUMU ---
        self.hostname = "ARDOS"
        self.current_mode = 1
        self.current_line = ""

        # KULLANICI ŞİFRELERİ (Dinamik)
        self.secret_pass = None
        self.console_pass = None
        self.vty_pass = None

        self.user_input = ""
        self.feedback = "SECURITY AUDIT: System is VULNERABLE. Set STRONG passwords."

        self.history = [
            "ARDOS# show running-config",
            "Building configuration...",
            "Current configuration : 1024 bytes",
            "! No passwords set!",
            "! No service password-encryption",
            "ARDOS#",
            "--- SECURITY HARDENING REQUIRED ---"
        ]

        self.task_title = "MISSION: DEVICE HARDENING"

        # --- GÖREV KARTLARI ---
        self.steps = [
            {
                "title": "1. Set Enable Secret",
                "desc": "Protect privileged mode with ANY strong password.",
                "cmds": "enable secret <password>",
                "done": False
            },
            {
                "title": "2. Encrypt All Passwords",
                "desc": "Hide plain-text passwords in config file.",
                "cmds": "service password-encryption",
                "done": False
            },
            {
                "title": "3. Secure Console Port",
                "desc": "Set physical port password & enable login.",
                "cmds": "line console 0 > password <pass> > login > exit",
                "done": False
            },
            {
                "title": "4. Secure VTY (Remote)",
                "desc": "Set remote access password & enable login.",
                "cmds": "line vty 0 4 > password <pass> > login > exit",
                "done": False
            }
        ]

        # State Flags
        self.service_encryption = False
        self.temp_line_login = False  # Login yazıldı mı kontrolü

    def events(self, event):
        if self.completed: return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.process_command(self.user_input)
                self.user_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            else:
                if len(event.unicode) > 0 and event.unicode.isprintable():
                    self.user_input += event.unicode

    def process_command(self, cmd):
        cmd = cmd.strip()

        self.history.append(self.get_prompt_string() + cmd)
        if len(self.history) > 20: self.history.pop(0)

        # --- MODE 1: PRIVILEGED ---
        if self.current_mode == 1:
            if cmd in ["configure terminal", "conf t"]:
                self.current_mode = 2
                self.feedback = "SUCCESS: Global Config Mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "HINT: Type 'conf t' to start configuration."

        # --- MODE 2: GLOBAL CONFIG ---
        elif self.current_mode == 2:
            # 1. Enable Secret (DİNAMİK)
            if cmd.startswith("enable secret"):
                parts = cmd.split()
                if len(parts) >= 3:
                    user_pass = parts[2]  # "enable" "secret" "sifre"
                    self.secret_pass = user_pass
                    self.feedback = f"SUCCESS: Secret set to '{user_pass}' (Hashed)."
                    self.history.append(f"[Syslog] Secret password set.")
                    self.complete_step(0)
                else:
                    self.feedback = "ERROR: Incomplete command. Usage: enable secret <password>"

            # 2. Service Password Encryption
            elif cmd == "service password-encryption":
                self.service_encryption = True
                self.feedback = "SUCCESS: Encryption service active."
                self.history.append("[Syslog] Encryption service enabled")
                self.complete_step(1)

            # Enter Line Console
            elif cmd == "line console 0":
                self.current_mode = 3
                self.current_line = "console"
                self.temp_line_login = False  # Sıfırla
                self.feedback = "MODE: Console Config. Set 'password <...>' and 'login'."

            # Enter Line VTY
            elif cmd == "line vty 0 4":
                self.current_mode = 3
                self.current_line = "vty"
                self.temp_line_login = False  # Sıfırla
                self.feedback = "MODE: VTY Config. Set 'password <...>' and 'login'."

            elif cmd in ["exit", "end"]:
                self.current_mode = 1
                self.feedback = "Back to Privileged Mode."

            elif cmd == "":
                pass
            else:
                self.feedback = "ERROR: Unknown command."

        # --- MODE 3: LINE CONFIG ---
        elif self.current_mode == 3:
            # Password Set (DİNAMİK)
            if cmd.startswith("password"):
                parts = cmd.split()
                if len(parts) >= 2:
                    user_pass = parts[1]

                    if self.current_line == "console":
                        self.console_pass = user_pass
                    elif self.current_line == "vty":
                        self.vty_pass = user_pass

                    self.feedback = f"OK: Password set to '{user_pass}'."
                    self.history.append("Password stored.")
                else:
                    self.feedback = "ERROR: Missing password. Usage: password <word>"

            elif cmd == "login":
                self.temp_line_login = True
                self.feedback = "OK: Login check enabled."
                self.history.append("Login enabled")

            elif cmd == "exit":
                # Çıkarken kontrol et: Şifre var mı? Login var mı?
                is_secure = False

                if self.current_line == "console":
                    if self.console_pass and self.temp_line_login:
                        is_secure = True
                        self.feedback = "SUCCESS: Console port secured."
                        self.complete_step(2)

                elif self.current_line == "vty":
                    if self.vty_pass and self.temp_line_login:
                        is_secure = True
                        self.feedback = "SUCCESS: Remote access secured."
                        self.complete_step(3)

                if not is_secure:
                    self.feedback = "FAIL: Line NOT secure! Did you set password AND 'login'?"
                    self.history.append("%Warning: Security incomplete")

                self.current_mode = 2
                self.current_line = ""

            elif cmd == "":
                pass
            else:
                self.feedback = "HINT: Use 'password <your_pass>' and 'login'."

        # Kazanma Kontrolü
        # Tüm şifreler belirlenmiş ve encryption açılmışsa
        if self.secret_pass and self.console_pass and self.vty_pass and self.service_encryption:
            # Console ve VTY'nin 'login' ile bitirildiğini step kontrolünden anlıyoruz
            if all(step["done"] for step in self.steps):
                self.completed = True
                self.history.append("--- SYSTEM FULLY HARDENED ---")

    def complete_step(self, index):
        if not self.steps[index]["done"]:
            self.steps[index]["done"] = True

    def get_prompt_string(self):
        if self.current_mode == 1:
            return f"{self.hostname}#"
        elif self.current_mode == 2:
            return f"{self.hostname}(config)#"
        elif self.current_mode == 3:
            return f"{self.hostname}(config-line)#"
        return ">"

    def update(self):
        self.timer += 1
        if self.completed and self.anim_scale < 1.0:
            self.anim_scale += 0.05

    def draw_wrapped_text(self, text, font, color, surface, x, y, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            w, h = font.size(test_line)
            if w < max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        current_y = y
        for line in lines:
            txt_surf = font.render(line, True, color)
            surface.blit(txt_surf, (x, current_y))
            current_y += font.get_height() + 2
        return current_y

    def draw_top_bar(self):
        bar_h = 80
        pygame.draw.rect(self.screen, (10, 15, 20), (0, 0, SCREEN_WIDTH, bar_h))
        pygame.draw.line(self.screen, NEON_GREEN, (0, bar_h), (SCREEN_WIDTH, bar_h), 3)
        title = self.font_header.render(self.task_title, True, NEON_GREEN)
        self.screen.blit(title, (30, 20))
        status_text = "STATUS: VULNERABLE" if not self.completed else "STATUS: SECURE"
        status_color = (255, 80, 80) if not self.completed else NEON_GREEN
        status_surf = self.font_header.render(status_text, True, status_color)
        status_rect = status_surf.get_rect(topright=(SCREEN_WIDTH - 30, 20))
        self.screen.blit(status_surf, status_rect)

    def draw_terminal(self):
        x, y = 50, 110
        w, h = 800, 620
        pygame.draw.rect(self.screen, (0, 0, 0, 128), (x + 10, y + 10, w, h), border_radius=5)
        pygame.draw.rect(self.screen, (10, 12, 16), (x, y, w, h), border_radius=5)
        pygame.draw.rect(self.screen, (40, 44, 50), (x, y, w, h), 2, border_radius=5)
        pygame.draw.rect(self.screen, (30, 32, 38), (x, y, w, 30), border_top_left_radius=5, border_top_right_radius=5)
        title = self.font_ui.render(" SSH Terminal - root@ardos-router", True, (150, 150, 150))
        self.screen.blit(title, (x + 10, y + 5))
        for i, color in enumerate([(255, 80, 80), (255, 200, 80), (80, 200, 80)]):
            pygame.draw.circle(self.screen, color, (x + w - 20 - (i * 25), y + 15), 6)
        pygame.draw.rect(self.screen, (30, 35, 40), (x + w - 15, y + 30, 15, h - 30))
        pygame.draw.rect(self.screen, (60, 65, 70), (x + w - 12, y + 35, 9, 50), border_radius=4)
        content_x = x + 15
        content_y = y + 45
        line_h = 24
        for line in self.history:
            txt = self.font_term.render(line, True, NEON_GREEN)
            self.screen.blit(txt, (content_x, content_y))
            content_y += line_h
        prompt = self.get_prompt_string()
        active_txt = self.font_term.render(prompt + self.user_input, True, NEON_GREEN)
        self.screen.blit(active_txt, (content_x, content_y))
        if (self.timer // 30) % 2 == 0:
            cursor_x = content_x + active_txt.get_width()
            pygame.draw.rect(self.screen, NEON_GREEN, (cursor_x, content_y + 2, 10, 20))

    def draw_side_panel(self):
        panel_x = 880
        panel_y = 110
        panel_w = 380
        panel_h = 620
        pygame.draw.rect(self.screen, (20, 22, 28), (panel_x, panel_y, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(self.screen, (50, 200, 50) if self.completed else (60, 60, 70),
                         (panel_x, panel_y, panel_w, panel_h), 2, border_radius=8)
        cursor_y = panel_y + 20
        max_txt_w = panel_w - 40
        head_txt = self.font_header.render("HARDENING GUIDE", True, NEON_GREEN)
        self.screen.blit(head_txt, (panel_x + 20, cursor_y))
        cursor_y += 40

        for step in self.steps:
            card_start_y = cursor_y
            content_y = cursor_y + 10
            icon = "[OK]" if step["done"] else "[  ]"
            title_txt = f"{icon} {step['title']}"
            content_y = self.draw_wrapped_text(title_txt, self.font_ui_bold, WHITE, self.screen, panel_x + 20,
                                               content_y, max_txt_w)
            content_y += 5
            content_y = self.draw_wrapped_text(step['desc'], self.font_ui, (180, 180, 180), self.screen, panel_x + 20,
                                               content_y, max_txt_w)
            content_y += 5
            cmd_txt = f"Cmd: {step['cmds']}"
            content_y = self.draw_wrapped_text(cmd_txt, self.font_small, (100, 200, 255), self.screen, panel_x + 20,
                                               content_y, max_txt_w)
            card_height = content_y - card_start_y + 10
            card_rect = pygame.Rect(panel_x + 10, card_start_y, panel_w - 20, card_height)
            border_color = NEON_GREEN if step["done"] else (60, 60, 60)
            pygame.draw.rect(self.screen, border_color, card_rect, 1, border_radius=5)
            cursor_y = content_y + 15

        cursor_y += 10
        pygame.draw.line(self.screen, (60, 65, 70), (panel_x + 20, cursor_y), (panel_x + panel_w - 20, cursor_y), 2)
        cursor_y += 15
        log_title = self.font_ui_bold.render("SYSTEM AUDIT LOG:", True, (150, 150, 150))
        self.screen.blit(log_title, (panel_x + 20, cursor_y))
        cursor_y += 25
        log_bg_h = panel_h - (cursor_y - panel_y) - 15
        if log_bg_h > 0:
            log_rect = pygame.Rect(panel_x + 15, cursor_y, panel_w - 30, log_bg_h)
            pygame.draw.rect(self.screen, (10, 10, 10), log_rect, border_radius=5)
            if "FAIL" in self.feedback or "ERROR" in self.feedback:
                color = (255, 80, 80)
            elif "SUCCESS" in self.feedback:
                color = NEON_GREEN
            elif "HINT" in self.feedback:
                color = (255, 200, 50)
            else:
                color = (100, 200, 255)
            self.draw_wrapped_text(self.feedback, self.font_ui, color, self.screen, panel_x + 25, cursor_y + 10,
                                   log_rect.width - 20)

    def draw_victory_popup(self):
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        w, h = 700, 350
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (center_x, center_y)
        pygame.draw.rect(self.screen, (10, 20, 10), rect)
        pygame.draw.rect(self.screen, NEON_GREEN, rect, 5)
        t1 = self.font_big.render("DEVICE HARDENED", True, NEON_GREEN)
        t2 = self.font_header.render("SECURITY PROTOCOLS APPLIED", True, WHITE)
        t3 = self.font_ui.render("All systems secure.", True, (150, 150, 150))
        self.screen.blit(t1, t1.get_rect(center=(center_x, center_y - 40)))
        self.screen.blit(t2, t2.get_rect(center=(center_x, center_y + 30)))
        self.screen.blit(t3, t3.get_rect(center=(center_x, center_y + 80)))

    def draw(self):
        self.screen.fill((15, 18, 25))
        self.draw_top_bar()
        self.draw_terminal()
        self.draw_side_panel()
        if self.completed:
            self.draw_victory_popup()