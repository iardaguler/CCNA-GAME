import pygame
import sys
from settings import *
from utils.save_manager import load_progress, save_progress
from utils.sound_manager import sound_manager

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.SysFont(FONT_NAME, 80, bold=True)
        self.font_button = pygame.font.SysFont(FONT_NAME, 30, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAME, 20)

        self.start_game = False
        self.selected_level = 1

        self.blink_timer = 0
        self.show_cursor = True

        self.unlocked_levels = load_progress()

        self.btn_width = 300
        self.btn_height = 50
        
        self.buttons = []
        
        # Oyna/Çıkış yerine Level Select
        start_y = 350
        cols = 5
        x_spacing = 180
        y_spacing = 80
        
        start_x = (SCREEN_WIDTH - (cols * x_spacing)) // 2 + 90
        
        self.level_buttons = []
        for i in range(1, 12):
            row = (i - 1) // cols
            col = (i - 1) % cols
            
            x = start_x + col * x_spacing
            y = start_y + row * y_spacing
            
            rect = pygame.Rect(x - 70, y, 140, 50)
            self.level_buttons.append({"level": i, "rect": rect})

        self.btn_quit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 100, 400, 60)
        self.btn_audio_rect = pygame.Rect(20, 20, 200, 45)

    def events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            if self.btn_audio_rect.collidepoint(mouse_pos):
                sound_manager.toggle_music()

            for btn in self.level_buttons:
                if btn["rect"].collidepoint(mouse_pos) and btn["level"] <= self.unlocked_levels:
                    self.selected_level = btn["level"]
                    self.start_game = True

            if self.btn_quit_rect.collidepoint(mouse_pos):
                pygame.quit()
                sys.exit()

    def update(self):
        self.blink_timer += 1
        if self.blink_timer > 30:
            self.show_cursor = not self.show_cursor
            self.blink_timer = 0

    def draw_button(self, rect, text, base_color, hover_color, mouse_pos, locked=False):
        is_hovered = rect.collidepoint(mouse_pos) and not locked

        if locked:
            bg_color = (30, 30, 30)
            text_color = (100, 100, 100)
            pygame.draw.rect(self.screen, bg_color, rect)
            pygame.draw.rect(self.screen, text_color, rect, 2)
        elif is_hovered:
            bg_color = hover_color
            text_color = BLACK
            pygame.draw.rect(self.screen, bg_color, rect)
        else:
            bg_color = BLACK
            border_color = base_color
            text_color = base_color
            pygame.draw.rect(self.screen, border_color, rect, 2)

        text_surf = self.font_button.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw(self):
        self.screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()

        title_text = self.font_big.render("CCNA-GAME MASTER", True, NEON_GREEN)
        subtitle_text = self.font_button.render("NETWORK DEFENDER SIMULATION", True, WHITE)

        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        sub_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 190))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, sub_rect)

        pygame.draw.line(self.screen, NEON_GREEN, (SCREEN_WIDTH // 2 - 250, 170), (SCREEN_WIDTH // 2 + 250, 170), 4)

        sel_txt = self.font_button.render("SELECT LEVEL", True, NEON_GREEN)
        self.screen.blit(sel_txt, sel_txt.get_rect(center=(SCREEN_WIDTH // 2, 280)))

        for btn in self.level_buttons:
            lvl = btn["level"]
            locked = lvl > self.unlocked_levels
            self.draw_button(
                rect=btn["rect"],
                text=f"Lvl {lvl}",
                base_color=NEON_GREEN,
                hover_color=NEON_GREEN,
                mouse_pos=mouse_pos,
                locked=locked
            )

        self.draw_button(
            rect=self.btn_quit_rect,
            text="TERMINATE SESSION",
            base_color=(200, 50, 50),
            hover_color=(255, 50, 50),
            mouse_pos=mouse_pos
        )

        # Audio Toggle Button
        audio_text = "AUDIO: ON" if sound_manager.music_enabled else "AUDIO: OFF"
        audio_color = NEON_GREEN if sound_manager.music_enabled else GRAY
        self.draw_button(
            rect=self.btn_audio_rect,
            text=audio_text,
            base_color=audio_color,
            hover_color=NEON_GREEN,
            mouse_pos=mouse_pos
        )

        if self.show_cursor:
            cursor_text = self.font_small.render("_", True, NEON_GREEN)
            self.screen.blit(cursor_text, (20, SCREEN_HEIGHT - 40))

        ver_text = self.font_small.render("System v2.0 | Secure Shell", True, GRAY)
        ver_rect = ver_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        self.screen.blit(ver_text, ver_rect)
