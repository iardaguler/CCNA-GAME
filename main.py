import pygame
import sys
from settings import *
from menu import MainMenu

# Import Levels
from levels.level_1_physical import Level1
from levels.level_2_cli import Level2
from levels.level_3_ip import Level3
from levels.level_4_connectivity import Level4
from levels.level_5_security import Level5
from levels.level_6_vlan import Level6


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont(FONT_NAME, 40, bold=True)

        # --- LEVEL MANAGEMENT ---
        self.level_index = 0  # <--- 0 YAPTIK (Artık Menüden başlıyor)
        self.current_level = None
        self.load_level()

    def load_level(self):
        """Loads the current level based on index"""
        if self.level_index == 0:  # <--- MENU EKLENDİ
            self.current_level = MainMenu(self.screen)
        elif self.level_index == 1:
            self.current_level = Level1(self.screen)
        elif self.level_index == 2:
            self.current_level = Level2(self.screen)
        elif self.level_index == 3:
            self.current_level = Level3(self.screen)
        elif self.level_index == 4:
            self.current_level = Level4(self.screen)
        elif self.level_index == 5:
            self.current_level = Level5(self.screen)
        elif self.level_index == 6:
            self.current_level = Level6(self.screen)
        else:
            self.current_level = None

    def run(self):
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            # Pass events to the current level
            if self.current_level:
                self.current_level.events(event)

    def update(self):
        if self.current_level:
            self.current_level.update()

            # --- MENU LOGIC (LEVEL 0) ---
            # Eğer şu an Menüdeysek ve kullanıcı "Start"a bastıysa:
            if self.level_index == 0 and hasattr(self.current_level, 'start_game'):
                if self.current_level.start_game:
                    self.level_index = 1  # Level 1'e geç
                    self.load_level()

            # --- GAME LEVELS LOGIC ---
            # Normal leveller için completion kontrolü
            elif hasattr(self.current_level, 'completed') and self.current_level.completed:
                # Wait briefly
                self.draw()
                pygame.time.wait(2000)

                # Advance level
                self.level_index += 1
                self.load_level()

    def draw(self):
        if self.current_level:
            self.current_level.draw()
        else:
            # VICTORY SCREEN
            self.screen.fill(BLACK)
            text = self.font.render("CONGRATULATIONS! ALL TASKS COMPLETED.", True, NEON_GREEN)
            subtext = self.font.render("New levels coming soon...", True, WHITE)

            # Center text
            text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
            sub_rect = subtext.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))

            self.screen.blit(text, text_rect)
            self.screen.blit(subtext, sub_rect)

        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()