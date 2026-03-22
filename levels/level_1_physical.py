import pygame
import math
from settings import *


class Level1:
    def __init__(self, screen):
        self.screen = screen
        # Font Tanımları
        self.font_header = pygame.font.SysFont("Impact", 32)
        self.font_sub = pygame.font.SysFont(FONT_NAME, 20)
        self.font_label = pygame.font.SysFont(FONT_NAME, 16, bold=True)
        # Popup için büyük font ekledik
        self.font_big = pygame.font.SysFont("Arial", 60, bold=True)

        try:
            self.font_terminal = pygame.font.SysFont("Consolas", 18)
        except:
            self.font_terminal = pygame.font.SysFont("monospace", 18)

        self.completed = False
        self.timer = 0

        self.task_title = "MISSION: PHYSICAL LAYER CONNECTIVITY"
        self.task_desc = "Objective: Establish connection between Router & Switch via Console."

        # CİHAZ AYARLARI
        device_width = 360
        device_height = 70
        center_x = SCREEN_WIDTH // 2 - (device_width // 2) - 50

        self.router_rect = pygame.Rect(center_x, 220, device_width, device_height)
        self.switch_rect = pygame.Rect(center_x, 380, device_width, device_height)

        self.router_port_center = (self.router_rect.right - 50, self.router_rect.centery)
        self.switch_port_center = (self.switch_rect.right - 50, self.switch_rect.centery)

        self.router_hitbox = pygame.Rect(0, 0, 60, 60)
        self.router_hitbox.center = self.router_port_center

        self.switch_hitbox = pygame.Rect(0, 0, 60, 60)
        self.switch_hitbox.center = self.switch_port_center

        self.dragging = False
        self.drag_start_pos = None
        self.mouse_pos = (0, 0)
        self.drag_source = None
        self.cable_connected = False
        self.console_open = False
        self.console_rect = pygame.Rect(SCREEN_WIDTH - 650, 180, 600, 450)

    def events(self, event):
        if self.completed: return  # Bitince etkileşimi kes

        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.cable_connected:
                if self.router_hitbox.collidepoint(event.pos):
                    self.dragging = True
                    self.drag_source = "router"
                    self.drag_start_pos = self.router_port_center
                elif self.switch_hitbox.collidepoint(event.pos):
                    self.dragging = True
                    self.drag_source = "switch"
                    self.drag_start_pos = self.switch_port_center

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                if self.drag_source == "router" and self.switch_hitbox.collidepoint(event.pos):
                    self.cable_connected = True
                elif self.drag_source == "switch" and self.router_hitbox.collidepoint(event.pos):
                    self.cable_connected = True
                self.dragging = False
                self.drag_source = None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.cable_connected and self.router_rect.collidepoint(event.pos):
                self.console_open = True

    def update(self):
        self.timer += 1
        if self.cable_connected and self.console_open:
            self.completed = True

    def draw_victory_popup(self):
        """STANDARTLAŞTIRILMIŞ BAŞARI EKRANI (SLEEK)"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        
        line_width = 600
        pygame.draw.line(self.screen, NEON_GREEN, (center_x - line_width//2, center_y - 90), (center_x + line_width//2, center_y - 90), 1)
        pygame.draw.line(self.screen, NEON_GREEN, (center_x - line_width//2, center_y + 90), (center_x + line_width//2, center_y + 90), 1)

        t1 = self.font_big.render("PHYSICAL LINK UP", True, NEON_GREEN)
        t2 = self.font_sub.render("LAYER 1 CONNECTIVITY ESTABLISHED", True, WHITE)
        t3 = self.font_label.render("[SECURE_SESSION] : Handshake Successful...", True, (150, 150, 150))

        self.screen.blit(t1, t1.get_rect(center=(center_x, center_y - 25)))
        self.screen.blit(t2, t2.get_rect(center=(center_x, center_y + 35)))
        self.screen.blit(t3, t3.get_rect(center=(center_x, center_y + 65)))

    def draw_top_bar(self):
        bar_height = 80
        pygame.draw.rect(self.screen, (15, 15, 20), (0, 0, SCREEN_WIDTH, bar_height))
        pygame.draw.line(self.screen, NEON_GREEN, (0, bar_height), (SCREEN_WIDTH, bar_height), 2)

        title_surf = self.font_header.render(self.task_title, True, NEON_GREEN)
        self.screen.blit(title_surf, (30, 15))
        desc_surf = self.font_sub.render(self.task_desc, True, GRAY)
        self.screen.blit(desc_surf, (30, 50))

        status_text = "STATUS: ACTIVE" if not self.completed else "STATUS: COMPLETE"
        status_color = (255, 50, 50) if not self.completed else NEON_GREEN
        status_surf = self.font_header.render(status_text, True, status_color)
        status_rect = status_surf.get_rect(topright=(SCREEN_WIDTH - 30, 25))
        self.screen.blit(status_surf, status_rect)

    def draw_grid_background(self):
        self.screen.fill((10, 12, 18))
        grid_color = (25, 30, 40)
        gap = 50
        for x in range(0, SCREEN_WIDTH, gap):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, gap):
            pygame.draw.line(self.screen, grid_color, (0, y), (SCREEN_WIDTH, y))

        rack_color = (40, 45, 50)
        left_pole_x = self.router_rect.left - 30
        right_pole_x = self.router_rect.right + 30
        pygame.draw.rect(self.screen, rack_color, (left_pole_x, 80, 20, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, rack_color, (right_pole_x, 80, 20, SCREEN_HEIGHT))

        for y in range(100, SCREEN_HEIGHT, 40):
            pygame.draw.circle(self.screen, (10, 10, 10), (left_pole_x + 10, y), 5)
            pygame.draw.circle(self.screen, (10, 10, 10), (right_pole_x + 10, y), 5)

    def draw_device(self, rect, name, color_highlight, port_center_pos):
        ear_width = 30
        pygame.draw.rect(self.screen, (70, 70, 75),
                         (rect.left - ear_width, rect.top, rect.width + (ear_width * 2), rect.height), border_radius=4)
        pygame.draw.rect(self.screen, (30, 32, 36), rect)
        pygame.draw.rect(self.screen, color_highlight, rect, 2)

        for i in range(5):
            vent_x = rect.left + 20 + (i * 10)
            pygame.draw.line(self.screen, (50, 50, 50), (vent_x, rect.top + 10), (vent_x, rect.bottom - 10), 2)

        label = self.font_label.render(name, True, WHITE)
        self.screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

        port_bg_rect = pygame.Rect(0, 0, 100, 40)
        port_bg_rect.center = port_center_pos
        pygame.draw.rect(self.screen, (20, 20, 20), port_bg_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), port_bg_rect, 1)

        start_x = port_bg_rect.left + 10
        for i in range(4):
            p_x = start_x + (i * 22)
            p_y = port_bg_rect.centery - 8
            pygame.draw.rect(self.screen, (5, 5, 5), (p_x, p_y, 16, 16))
            pygame.draw.line(self.screen, (150, 150, 0), (p_x + 2, p_y), (p_x + 14, p_y), 2)

            led_color = (30, 0, 0)
            if self.cable_connected:
                led_color = NEON_GREEN if (self.timer // 15) % 2 == 0 else (0, 100, 0)
            pygame.draw.circle(self.screen, led_color, (p_x + 8, p_y - 5), 2)

    def draw_cable(self, start_pos, end_pos, is_active):
        inner_color = (50, 150, 255) if is_active else (255, 200, 0)
        pygame.draw.line(self.screen, BLACK, start_pos, end_pos, 9)
        pygame.draw.line(self.screen, inner_color, start_pos, end_pos, 5)
        pygame.draw.circle(self.screen, (200, 200, 200), start_pos, 6)
        pygame.draw.circle(self.screen, (200, 200, 200), end_pos, 6)

    def draw(self):
        self.draw_grid_background()
        self.draw_top_bar()
        self.draw_device(self.router_rect, "CISCO 2911 ISR", (0, 122, 204), self.router_port_center)
        self.draw_device(self.switch_rect, "CISCO CATALYST 2960", (255, 140, 0), self.switch_port_center)

        if self.dragging and self.drag_start_pos:
            self.draw_cable(self.drag_start_pos, self.mouse_pos, False)

        if self.cable_connected:
            self.draw_cable(self.router_port_center, self.switch_port_center, True)

        if self.console_open:
            shadow = self.console_rect.copy().move(8, 8)
            pygame.draw.rect(self.screen, (0, 0, 0, 150), shadow)
            pygame.draw.rect(self.screen, (10, 12, 16), self.console_rect)
            pygame.draw.rect(self.screen, NEON_GREEN, self.console_rect, 2)

            header = pygame.Rect(self.console_rect.x, self.console_rect.y, self.console_rect.width, 32)
            pygame.draw.rect(self.screen, (30, 35, 40), header)
            pygame.draw.line(self.screen, NEON_GREEN, (header.left, header.bottom), (header.right, header.bottom), 1)

            pygame.draw.circle(self.screen, (255, 80, 80), (header.right - 20, header.centery), 6)
            pygame.draw.circle(self.screen, (255, 200, 80), (header.right - 40, header.centery), 6)

            title = self.font_label.render("ADMIN TERMINAL - COM1", True, NEON_GREEN)
            self.screen.blit(title, (header.x + 10, header.y + 8))

            lines = [
                "",
                "Router> enable",
                "Router# configure terminal",
                "Router(config)# interface gig0/0",
                "Router(config-if)# no shutdown",
                "",
                "%LINK-3-UPDOWN: Interface GigabitEthernet0/0, changed state to up",
                "%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/0, changed state to up",
                "",
                "> SYSTEM CHECK: PHYSICAL LAYER OK.",
                "> READY FOR NEXT LEVEL..."
            ]
            y = self.console_rect.y + 45
            for line in lines:
                txt = self.font_terminal.render(line, True, NEON_GREEN)
                self.screen.blit(txt, (self.console_rect.x + 15, y))
                y += 20

            if (self.timer // 20) % 2 == 0:
                pygame.draw.rect(self.screen, NEON_GREEN, (self.console_rect.x + 15, y, 10, 18))

        # Alt Footer'ı kaldırdık, yerine Popup gelecek
        if self.completed:
            self.draw_victory_popup()
        else:
            # HINT sadece oyun bitmemişse görünsün
            footer_y = SCREEN_HEIGHT - 30
            hint_text = "HINT: Drag connection from Router module to Switch module. Right-click Router for CLI."
            hint_surf = self.font_label.render(hint_text, True, GRAY)
            self.screen.blit(hint_surf, (20, footer_y))