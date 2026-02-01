import pygame
from settings import *


class Level4:
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

        # --- PC DURUMU ---
        self.pc_ip = "0.0.0.0"
        self.pc_mask = "0.0.0.0"
        self.pc_gateway = "0.0.0.0"

        self.user_input = ""
        self.feedback = "Terminal Ready. Use 'ipconfig' to check status."

        self.history = [
            "Microsoft Windows [Version 10.0.19045]",
            "(c) Microsoft Corporation. All rights reserved.",
            "",
            "C:\\Users\\Admin>_"
        ]

        self.task_title = "MISSION: ENDPOINT CONNECTIVITY"

        # --- GÖREV KARTLARI ---
        self.steps = [
            {
                "title": "1. Check Configuration",
                "desc": "Verify current network adapter settings.",
                "cmds": "ipconfig",
                "done": False
            },
            {
                "title": "2. Assign Static IP",
                "desc": "Set any IP (Must be different from Gateway).",
                "cmds": "set ip <ip> <mask> <gateway>",
                "done": False
            },
            {
                "title": "3. Verify Connectivity",
                "desc": "Test connection to the Router (Gateway).",
                "cmds": "ping 192.168.1.1",
                "done": False
            }
        ]

        self.ip_set = False
        self.ping_success = False

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

        # Geçmişe ekle
        if self.history:
            self.history[-1] = self.history[-1].replace("_", "") + cmd

        if len(self.history) > 22: self.history = self.history[6:]

        if cmd == "ipconfig":
            self.history.append("")
            self.history.append("Ethernet adapter Ethernet0:")
            self.history.append(f"   IPv4 Address. . . . . . : {self.pc_ip}")
            self.history.append(f"   Subnet Mask . . . . . . : {self.pc_mask}")
            self.history.append(f"   Default Gateway . . . . : {self.pc_gateway}")
            self.history.append("")
            self.feedback = "SUCCESS: Configuration displayed."
            self.complete_step(0)

        elif cmd.startswith("set ip"):
            parts = cmd.split()
            if len(parts) == 5:
                ip = parts[2]
                mask = parts[3]
                gw = parts[4]

                # --- 1. KONTROL: IP ÇAKIŞMASI ---
                # Kullanıcı istediği IP'yi verebilir ama Gateway ile AYNI olamaz.
                if ip == gw:
                    self.feedback = "ERROR: IP Conflict! Client IP cannot be same as Gateway."
                    self.history.append("Error: Duplicate IP address detected.")

                # --- 2. KONTROL: GATEWAY DOĞRU MU? ---
                # Router'ın IP'si 192.168.1.1 sabit olduğu için Gateway bu olmalı.
                elif gw != "192.168.1.1":
                    self.feedback = "ERROR: Gateway unreachable. Target Router is 192.168.1.1"
                    self.history.append("Error: Invalid Default Gateway.")

                else:
                    # --- BAŞARILI ATAMA (SUBNET KONTROLÜ YOK) ---
                    # Kullanıcı 10.0.0.5 bile verse kabul ediyoruz.
                    # Ancak Ping aşamasında bu sorun çıkaracak (Gerçekçi simülasyon).
                    self.pc_ip = ip
                    self.pc_mask = mask
                    self.pc_gateway = gw
                    self.ip_set = True
                    self.feedback = f"SUCCESS: Static IP {ip} assigned."
                    self.history.append("Command completed successfully.")
                    self.complete_step(1)
            else:
                self.history.append("Usage: set ip <ip> <mask> <gateway>")
                self.feedback = "ERROR: Invalid syntax."

        elif cmd.startswith("ping"):
            target = cmd.split()[-1]
            self.history.append(f"Pinging {target} with 32 bytes of data:")

            if target == "192.168.1.1":
                # --- PING MANTIĞI ---
                # IP atanmış mı? VE IP adresi doğru subnet'te mi (192.168.1.x)?
                # Eğer kullanıcı 10.0.0.5 verdiyse IP atanır ama PING ÇALIŞMAZ.

                correct_subnet = self.pc_ip.startswith("192.168.1.")

                if self.ip_set and correct_subnet:
                    # Başarılı Ping
                    self.history.append(f"Reply from {target}: bytes=32 time<1ms TTL=128")
                    self.history.append(f"Reply from {target}: bytes=32 time<1ms TTL=128")
                    self.history.append(f"Reply from {target}: bytes=32 time<1ms TTL=128")
                    self.history.append(f"Reply from {target}: bytes=32 time<1ms TTL=128")
                    self.ping_success = True
                    self.feedback = "SUCCESS: Connectivity Verified!"
                    self.complete_step(2)
                elif self.ip_set and not correct_subnet:
                    # Yanlış IP Bloğu (Örn: 10.0.0.5 verdiyse)
                    self.history.append("Request timed out.")
                    self.history.append("Request timed out.")
                    self.history.append("Request timed out.")
                    self.history.append("Request timed out.")
                    self.feedback = "FAIL: Destination host unreachable (Subnet Mismatch)."
                else:
                    # Hiç IP verilmemişse
                    self.history.append("General failure.")
                    self.feedback = "FAIL: PC needs a valid IP first!"
            else:
                self.history.append("Request timed out.")
                self.feedback = "ERROR: Target unreachable."

        elif cmd == "cls":
            self.history = []

        else:
            if cmd != "":
                self.history.append(f"'{cmd}' is not recognized as an internal command.")
                self.feedback = "ERROR: Unknown command."

        self.history.append("C:\\Users\\Admin>_")

        if self.ip_set and self.ping_success:
            self.completed = True

    def complete_step(self, index):
        if not self.steps[index]["done"]:
            self.steps[index]["done"] = True

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
        status_text = "STATUS: DISCONNECTED" if not self.completed else "STATUS: CONNECTED"
        status_color = (200, 200, 200) if not self.completed else NEON_GREEN
        status_surf = self.font_header.render(status_text, True, status_color)
        status_rect = status_surf.get_rect(topright=(SCREEN_WIDTH - 30, 20))
        self.screen.blit(status_surf, status_rect)

    def draw_terminal(self):
        x, y = 50, 110
        w, h = 800, 620
        pygame.draw.rect(self.screen, (0, 0, 0, 128), (x + 10, y + 10, w, h), border_radius=5)
        pygame.draw.rect(self.screen, BLACK, (x, y, w, h), border_radius=0)
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, w, h), 2, border_radius=0)
        pygame.draw.rect(self.screen, (220, 220, 220), (x, y, w, 25))
        title = self.font_ui_bold.render(" Command Prompt - C:\\Windows\\System32\\cmd.exe", True, BLACK)
        self.screen.blit(title, (x + 5, y + 2))
        pygame.draw.rect(self.screen, (200, 50, 50), (x + w - 30, y + 2, 25, 20))

        content_x = x + 10
        content_y = y + 35
        line_h = 24

        lines_to_draw = self.history[:-1] if self.history else []
        last_line = self.history[-1] if self.history else ""

        for line in lines_to_draw:
            txt = self.font_term.render(line, True, WHITE)
            self.screen.blit(txt, (content_x, content_y))
            content_y += line_h

        prompt_base = last_line.replace("_", "")
        active_text = prompt_base + self.user_input
        txt_active = self.font_term.render(active_text, True, WHITE)
        self.screen.blit(txt_active, (content_x, content_y))

        if (self.timer // 30) % 2 == 0:
            cursor_x = content_x + txt_active.get_width()
            pygame.draw.rect(self.screen, WHITE, (cursor_x, content_y + 16, 10, 3))

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

        head_txt = self.font_header.render("OPERATIONS GUIDE", True, NEON_GREEN)
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

        log_title = self.font_ui_bold.render("SYSTEM OUTPUT:", True, (150, 150, 150))
        self.screen.blit(log_title, (panel_x + 20, cursor_y))
        cursor_y += 25

        log_bg_h = panel_h - (cursor_y - panel_y) - 15
        if log_bg_h > 0:
            log_rect = pygame.Rect(panel_x + 15, cursor_y, panel_w - 30, log_bg_h)
            pygame.draw.rect(self.screen, (10, 10, 10), log_rect, border_radius=5)

            if "ERROR" in self.feedback or "FAIL" in self.feedback:
                color = (255, 80, 80)
            elif "SUCCESS" in self.feedback:
                color = NEON_GREEN
            else:
                color = (100, 200, 255)
            self.draw_wrapped_text(self.feedback, self.font_ui, color, self.screen, panel_x + 25, cursor_y + 10,
                                   log_rect.width - 20)

    def draw_victory_popup(self):
        """Bölüm Sonu Animasyonu"""
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        w, h = 700, 350
        rect = pygame.Rect(0, 0, w, h)
        rect.center = (center_x, center_y)
        pygame.draw.rect(self.screen, (10, 20, 10), rect)
        pygame.draw.rect(self.screen, NEON_GREEN, rect, 5)

        t1 = self.font_big.render("PING SUCCESSFUL", True, NEON_GREEN)
        t2 = self.font_header.render("END-TO-END CONNECTIVITY VERIFIED", True, WHITE)
        t3 = self.font_ui.render("Loading Final Level...", True, (150, 150, 150))

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