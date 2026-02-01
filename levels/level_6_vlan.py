import pygame
from settings import *


class Level6:
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

        # --- SWITCH DURUMU ---
        self.hostname = "Switch"
        self.current_mode = 1
        self.current_interface = ""

        self.user_input = ""
        self.feedback = "System Ready. Configure VLANs for Department Separation."

        # --- SOLA YASLI & TAŞMAYAN BAŞLANGIÇ ÇIKTISI ---
        # Sadece en gerekli satırları tutuyoruz ki ekran taşmasın.
        pad = " " * 28

        self.history = [
            "Switch> enable",
            "Switch# show vlan brief",
            "VLAN Name       Status    Ports",
            "---- ---------- --------- ---------------------------",
            f"1    default    active    Fa0/1, Fa0/2, Fa0/3, Fa0/4",
            f"{pad}Fa0/5, Fa0/6, Fa0/7, Fa0/8",
            f"{pad}Fa0/9..Fa0/24, Gi0/1-2",
            "1002 fddi-def   act/unsup ",
            "1003 token-ring act/unsup ",
            "",
            "Switch#",
            "--- SEGMENTATION REQUIRED ---"
        ]

        self.task_title = "MISSION: VLAN SEGMENTATION"

        # --- GÖREV KARTLARI ---
        self.steps = [
            {
                "title": "1. Create VLAN 10 (Sales)",
                "desc": "Create the VLAN ID and name it.",
                "cmds": "vlan 10 > name Sales > exit",
                "done": False
            },
            {
                "title": "2. Create VLAN 20 (HR)",
                "desc": "Create the VLAN ID and name it.",
                "cmds": "vlan 20 > name HR > exit",
                "done": False
            },
            {
                "title": "3. Assign Port fa0/1 to Sales",
                "desc": "Move interface FastEthernet0/1 to VLAN 10.",
                "cmds": "int fa0/1 > switchport access vlan 10",
                "done": False
            },
            {
                "title": "4. Assign Port fa0/2 to HR",
                "desc": "Move interface FastEthernet0/2 to VLAN 20.",
                "cmds": "int fa0/2 > switchport access vlan 20",
                "done": False
            }
        ]

        # Hedef Durumlar
        self.vlan10_exists = False
        self.vlan20_exists = False
        self.port1_assigned = False
        self.port2_assigned = False

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

        # --- DÜZELTME BURADA: BUFFER LİMİTİ ---
        # Ekran yüksekliğine sığması için geçmişi 21 satırda tutuyoruz.
        # Bu sayede asla aşağı taşmıyor.
        if len(self.history) > 21:
            # Fazlalık kadar baştan sil
            del self.history[:len(self.history) - 21]

        # --- MODE 1: PRIVILEGED ---
        if self.current_mode == 1:
            if cmd in ["configure terminal", "conf t"]:
                self.current_mode = 2
                self.feedback = "Global Config Mode."
            elif cmd == "":
                pass
            else:
                self.feedback = "Error: Type 'conf t' to configure VLANs."

        # --- MODE 2: GLOBAL CONFIG ---
        elif self.current_mode == 2:
            if cmd.startswith("vlan "):
                parts = cmd.split()
                if len(parts) > 1:
                    vid = parts[1]
                    if vid == "10":
                        self.current_mode = 4
                        self.vlan10_exists = True
                        self.feedback = "VLAN 10 Created. Name it 'Sales'."
                        self.history.append("VLAN 10 added.")
                    elif vid == "20":
                        self.current_mode = 4
                        self.vlan20_exists = True
                        self.feedback = "VLAN 20 Created. Name it 'HR'."
                        self.history.append("VLAN 20 added.")
                    else:
                        self.feedback = "Error: Task requires VLAN 10 and 20."
                else:
                    self.feedback = "Usage: vlan <id>"

            elif cmd.startswith("interface ") or cmd.startswith("int "):
                if "fa0/1" in cmd:
                    self.current_mode = 3
                    self.current_interface = "fa0/1"
                    self.feedback = "Configuring Interface fa0/1."
                elif "fa0/2" in cmd:
                    self.current_mode = 3
                    self.current_interface = "fa0/2"
                    self.feedback = "Configuring Interface fa0/2."
                else:
                    self.feedback = "Error: Use 'int fa0/1' or 'int fa0/2'."

            elif cmd in ["exit", "end"]:
                self.current_mode = 1
                self.feedback = "Back to Privileged Mode."

        # --- MODE 3: INTERFACE CONFIG ---
        elif self.current_mode == 3:
            if cmd.startswith("switchport access vlan "):
                parts = cmd.split()
                if len(parts) > 3:
                    vid = parts[3]
                    if self.current_interface == "fa0/1" and vid == "10":
                        if self.vlan10_exists:
                            self.port1_assigned = True
                            self.feedback = "SUCCESS: fa0/1 moved to VLAN 10."
                            self.complete_step(2)
                        else:
                            self.feedback = "Error: Create VLAN 10 first!"

                    elif self.current_interface == "fa0/2" and vid == "20":
                        if self.vlan20_exists:
                            self.port2_assigned = True
                            self.feedback = "SUCCESS: fa0/2 moved to VLAN 20."
                            self.complete_step(3)
                        else:
                            self.feedback = "Error: Create VLAN 20 first!"
                    else:
                        self.feedback = "Error: Wrong VLAN for this port."
                else:
                    self.feedback = "Usage: switchport access vlan <id>"

            elif cmd == "exit":
                self.current_mode = 2
                self.feedback = "Exited interface mode."

        # --- MODE 4: VLAN CONFIG ---
        elif self.current_mode == 4:
            if cmd.startswith("name "):
                name = cmd.split()[1]
                self.feedback = f"VLAN name set to {name}."

                if self.vlan10_exists and not self.steps[0]["done"] and name == "Sales":
                    self.complete_step(0)
                elif self.vlan20_exists and not self.steps[1]["done"] and name == "HR":
                    self.complete_step(1)

            elif cmd == "exit":
                self.current_mode = 2
                self.feedback = "VLAN configuration saved."

        # Kazanma Kontrolü
        if self.port1_assigned and self.port2_assigned:
            self.completed = True
            self.history.append("--- SEGMENTATION COMPLETE ---")

    def complete_step(self, index):
        if not self.steps[index]["done"]:
            self.steps[index]["done"] = True

    def get_prompt_string(self):
        if self.current_mode == 1:
            return "Switch#"
        elif self.current_mode == 2:
            return "Switch(config)#"
        elif self.current_mode == 3:
            return "Switch(config-if)#"
        elif self.current_mode == 4:
            return "Switch(config-vlan)#"
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
        status_text = "STATUS: DEFAULT VLAN 1" if not self.completed else "STATUS: SEGMENTED"
        status_color = (200, 200, 200) if not self.completed else NEON_GREEN
        status_surf = self.font_header.render(status_text, True, status_color)
        status_rect = status_surf.get_rect(topright=(SCREEN_WIDTH - 30, 20))
        self.screen.blit(status_surf, status_rect)

    def draw_terminal(self):
        x, y = 50, 110
        w, h = 800, 620
        # Terminal Arkaplan
        pygame.draw.rect(self.screen, (0, 0, 0, 128), (x + 10, y + 10, w, h), border_radius=5)
        pygame.draw.rect(self.screen, (10, 12, 16), (x, y, w, h), border_radius=5)
        pygame.draw.rect(self.screen, (40, 44, 50), (x, y, w, h), 2, border_radius=5)

        # Başlık
        pygame.draw.rect(self.screen, (30, 32, 38), (x, y, w, 30), border_top_left_radius=5, border_top_right_radius=5)
        title = self.font_ui.render(" SSH Terminal - admin@switch", True, (150, 150, 150))
        self.screen.blit(title, (x + 10, y + 5))

        # Süsler
        for i, color in enumerate([(255, 80, 80), (255, 200, 80), (80, 200, 80)]):
            pygame.draw.circle(self.screen, color, (x + w - 20 - (i * 25), y + 15), 6)

        # Scrollbar Süsü
        pygame.draw.rect(self.screen, (30, 35, 40), (x + w - 15, y + 30, 15, h - 30))
        pygame.draw.rect(self.screen, (60, 65, 70), (x + w - 12, y + 35, 9, 50), border_radius=4)

        content_x = x + 15
        content_y = y + 45
        line_h = 24

        # --- DÜZELTME: SADECE SON 21 SATIRI ÇİZ ---
        # Bu kısım garanti olsun diye var, process_command zaten siliyor.
        lines_to_draw = self.history[-21:]

        for line in lines_to_draw:
            txt = self.font_term.render(line, True, NEON_GREEN)
            self.screen.blit(txt, (content_x, content_y))
            content_y += line_h

        # Aktif Satır
        prompt = self.get_prompt_string()
        active_txt = self.font_term.render(prompt + self.user_input, True, NEON_GREEN)
        self.screen.blit(active_txt, (content_x, content_y))

        # İmleç
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
        head_txt = self.font_header.render("VLAN CONFIG GUIDE", True, NEON_GREEN)
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
        log_title = self.font_ui_bold.render("SYSTEM LOG:", True, (150, 150, 150))
        self.screen.blit(log_title, (panel_x + 20, cursor_y))
        cursor_y += 25
        log_bg_h = panel_h - (cursor_y - panel_y) - 15
        if log_bg_h > 0:
            log_rect = pygame.Rect(panel_x + 15, cursor_y, panel_w - 30, log_bg_h)
            pygame.draw.rect(self.screen, (10, 10, 10), log_rect, border_radius=5)
            if "Error" in self.feedback:
                color = (255, 80, 80)
            elif "SUCCESS" in self.feedback:
                color = NEON_GREEN
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
        t1 = self.font_big.render("VLANS CONFIGUED", True, NEON_GREEN)
        t2 = self.font_header.render("NETWORK TRAFFIC SEGMENTED", True, WHITE)
        t3 = self.font_ui.render("Level 6 Complete.", True, (150, 150, 150))
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