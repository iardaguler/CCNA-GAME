import pygame
from settings import *

class BaseLevel:
    def __init__(self, screen, task_title="MISSION"):
        self.screen = screen
        self.task_title = task_title
        
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

        self.user_input = ""
        self.feedback = ""
        self.history = []
        self.steps = []
        
        # Style overrides for Windows CMD vs Cisco CLI
        self.term_bg_color = (10, 12, 16)
        self.term_text_color = NEON_GREEN
        self.term_border_color = (40, 44, 50)
        self.term_header_color = (30, 32, 38)
        self.term_title = " SSH Terminal - root@device"
        self.term_title_color = (150, 150, 150)
        self.is_windows_cmd = False

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

    def get_status_text(self):
        return "STATUS: SECURE" if self.completed else "STATUS: ACTIVE"

    def get_status_color(self):
        return NEON_GREEN if self.completed else (200, 200, 200)

    def draw_top_bar(self):
        bar_h = 80
        pygame.draw.rect(self.screen, (10, 15, 20), (0, 0, SCREEN_WIDTH, bar_h))
        pygame.draw.line(self.screen, NEON_GREEN, (0, bar_h), (SCREEN_WIDTH, bar_h), 3)
        title = self.font_header.render(self.task_title, True, NEON_GREEN)
        self.screen.blit(title, (30, 20))
        
        status_surf = self.font_header.render(self.get_status_text(), True, self.get_status_color())
        status_rect = status_surf.get_rect(topright=(SCREEN_WIDTH - 30, 20))
        self.screen.blit(status_surf, status_rect)

    def get_prompt_string(self):
        return ">"

    def draw_terminal(self):
        x, y = 30, 110
        w, h = 820, 620
        pygame.draw.rect(self.screen, (0, 0, 0, 128), (x + 10, y + 10, w, h), border_radius=5)
        
        if self.is_windows_cmd:
            pygame.draw.rect(self.screen, BLACK, (x, y, w, h), border_radius=0)
            pygame.draw.rect(self.screen, (100, 100, 100), (x, y, w, h), 2, border_radius=0)
            pygame.draw.rect(self.screen, (220, 220, 220), (x, y, w, 25))
            title = self.font_ui_bold.render(self.term_title, True, BLACK)
            self.screen.blit(title, (x + 5, y + 2))
            pygame.draw.rect(self.screen, (200, 50, 50), (x + w - 30, y + 2, 25, 20))
            
            content_x = x + 10
            content_y = y + 35
        else:
            pygame.draw.rect(self.screen, self.term_bg_color, (x, y, w, h), border_radius=5)
            pygame.draw.rect(self.screen, self.term_border_color, (x, y, w, h), 2, border_radius=5)
            pygame.draw.rect(self.screen, self.term_header_color, (x, y, w, 30), border_top_left_radius=5, border_top_right_radius=5)
            title = self.font_ui.render(self.term_title, True, self.term_title_color)
            self.screen.blit(title, (x + 10, y + 5))
            for i, color in enumerate([(255, 80, 80), (255, 200, 80), (80, 200, 80)]):
                pygame.draw.circle(self.screen, color, (x + w - 20 - (i * 25), y + 15), 6)
            pygame.draw.rect(self.screen, (30, 35, 40), (x + w - 15, y + 30, 15, h - 30))
            pygame.draw.rect(self.screen, (60, 65, 70), (x + w - 12, y + 35, 9, 50), border_radius=4)
            
            content_x = x + 15
            content_y = y + 45
            
        line_h = 24
        
        # Draw history
        lines_to_draw = self.history[-21:] if len(self.history) > 21 else self.history
        
        if self.is_windows_cmd:
            lines_to_draw = self.history[:-1] if self.history else []
            last_line = self.history[-1] if self.history else ""
        
        for line in lines_to_draw:
            txt = self.font_term.render(line, True, self.term_text_color)
            self.screen.blit(txt, (content_x, content_y))
            content_y += line_h
            
        # Active Prompt
        if self.is_windows_cmd:
            prompt_base = last_line.replace("_", "")
            active_text = prompt_base + self.user_input
        else:
            prompt_base = self.get_prompt_string()
            active_text = prompt_base + self.user_input
            
        active_txt = self.font_term.render(active_text, True, self.term_text_color)
        self.screen.blit(active_txt, (content_x, content_y))

        # Cursor
        if (self.timer // 30) % 2 == 0:
            cursor_x = content_x + active_txt.get_width()
            if self.is_windows_cmd:
                pygame.draw.rect(self.screen, WHITE, (cursor_x, content_y + 16, 10, 3))
            else:
                pygame.draw.rect(self.screen, NEON_GREEN, (cursor_x, content_y + 2, 10, 20))

    def draw_side_panel(self):
        panel_x = 870
        panel_y = 110
        panel_w = 380
        panel_h = 620
        pygame.draw.rect(self.screen, (20, 22, 28), (panel_x, panel_y, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(self.screen, (50, 200, 50) if self.completed else (60, 60, 70),
                         (panel_x, panel_y, panel_w, panel_h), 2, border_radius=8)
        cursor_y = panel_y + 20
        max_txt_w = panel_w - 40
        head_txt = self.font_header.render("OBJECTIVES", True, NEON_GREEN)
        self.screen.blit(head_txt, (panel_x + 20, cursor_y))
        cursor_y += 40

        for step in self.steps:
            card_start_y = cursor_y
            content_y = cursor_y + 10
            icon = "[OK]" if step.get("done") else "[  ]"
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
            border_color = NEON_GREEN if step.get("done") else (60, 60, 60)
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
            
            # Determine feedback color
            color = (100, 200, 255)
            upper_fb = self.feedback.upper()
            if "ERROR" in upper_fb or "FAIL" in upper_fb:
                color = (255, 80, 80)
            elif "SUCCESS" in upper_fb or "SECURE" in upper_fb:
                color = NEON_GREEN
            elif "HINT" in upper_fb or "VULNERABLE" in upper_fb:
                color = (255, 200, 50)
                
            self.draw_wrapped_text(self.feedback, self.font_ui, color, self.screen, panel_x + 25, cursor_y + 10,
                                   log_rect.width - 20)

    def draw_victory_popup(self, title_text, subtitle_text, sub_sub_text="Handshake Successful"):
        # Semi-transparent minimalist overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)) # Darker, more professional
        self.screen.blit(overlay, (0, 0))
        
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        
        # Sleek decorative elements
        line_width = 600
        pygame.draw.line(self.screen, NEON_GREEN, (center_x - line_width//2, center_y - 90), (center_x + line_width//2, center_y - 90), 1)
        pygame.draw.line(self.screen, NEON_GREEN, (center_x - line_width//2, center_y + 90), (center_x + line_width//2, center_y + 90), 1)
        
        # Main Title (e.g., ACCESS GRANTED)
        t1 = self.font_big.render(title_text, True, NEON_GREEN)
        t1_rect = t1.get_rect(center=(center_x, center_y - 25))
        
        # Subtitle
        t2 = self.font_ui_bold.render(subtitle_text.upper(), True, WHITE)
        t2_rect = t2.get_rect(center=(center_x, center_y + 35))
        
        # Terminal-style status
        status_msg = f"[SECURE_SESSION] : {sub_sub_text}..."
        t3 = self.font_small.render(status_msg, True, (150, 150, 150))
        t3_rect = t3.get_rect(center=(center_x, center_y + 65))
        
        # Blinking cursor effect on title
        if (pygame.time.get_ticks() // 400) % 2 == 0:
            cursor_rect = pygame.Rect(t1_rect.right + 10, t1_rect.top + 10, 15, t1_rect.height - 20)
            pygame.draw.rect(self.screen, NEON_GREEN, cursor_rect)

        self.screen.blit(t1, t1_rect)
        self.screen.blit(t2, t2_rect)
        self.screen.blit(t3, t3_rect)

    def draw(self):
        self.screen.fill((15, 18, 25))
        self.draw_top_bar()
        self.draw_terminal()
        self.draw_side_panel()
        if self.completed:
            self.draw_victory_popup("MISSION COMPLETE", "OBJECTIVES ACHIEVED")
