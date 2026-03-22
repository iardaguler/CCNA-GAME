import pygame
import sys
from settings import *
from menu import MainMenu
from utils.save_manager import save_progress, load_progress
from utils.ui_components import TransitionScreen
from utils.sound_manager import sound_manager

# Import Levels
from levels.level_1_physical import Level1
from levels.level_2_cli import Level2
from levels.level_3_ip import Level3
from levels.level_4_connectivity import Level4
from levels.level_5_security import Level5
from levels.level_6_vlan import Level6
from levels.level_7_routing import Level7
from levels.level_8_acl import Level8
from levels.level_9_nat import Level9
from levels.level_10_dhcp import Level10
from levels.level_11_subnetting import Level11

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont(FONT_NAME, 40, bold=True)

        self.level_index = 0
        self.current_level = None
        
        self.transition = None
        self.is_transitioning = False
        
        # Start Background Music
        sound_manager.play_music()
        
        self.load_level()

    def load_level(self):
        if self.level_index == 0:
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
        elif self.level_index == 7:
            self.current_level = Level7(self.screen)
        elif self.level_index == 8:
            self.current_level = Level8(self.screen)
        elif self.level_index == 9:
            self.current_level = Level9(self.screen)
        elif self.level_index == 10:
            self.current_level = Level10(self.screen)
        elif self.level_index == 11:
            self.current_level = Level11(self.screen)
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

            if self.current_level and not self.is_transitioning:
                self.current_level.events(event)

    def update(self):
        if self.is_transitioning and self.transition:
            self.transition.update()
            if self.transition.finished:
                self.is_transitioning = False
                self.transition = None
                
                # Advance Level
                if self.level_index < 11:
                    self.level_index += 1
                else:
                    self.level_index = -1 # Victory
                self.load_level()
            return

        if self.current_level:
            self.current_level.update()

            if self.level_index == 0 and hasattr(self.current_level, 'start_game'):
                if self.current_level.start_game:
                    self.level_index = self.current_level.selected_level
                    self.load_level()

            elif hasattr(self.current_level, 'completed') and self.current_level.completed:
                # Play success SFX once
                sound_manager.play_success()
                
                # Save progress immediately
                save_progress(self.level_index + 1)
                
                # Start Transition
                next_lvl_num = self.level_index + 1
                next_name = f"LEVEL {next_lvl_num}" if next_lvl_num <= 11 else "VICTORY"
                self.transition = TransitionScreen(self.screen, next_name)
                self.is_transitioning = True

    def draw(self):
        if self.is_transitioning and self.transition:
            self.transition.draw()
        elif self.current_level:
            self.current_level.draw()
        elif self.level_index == -1:
            self.screen.fill(BLACK)
            text = self.font.render("CONGRATULATIONS! ALL MODULES COMPLETED.", True, NEON_GREEN)
            subtext = self.font.render("You are now a Network Defender.", True, WHITE)

            text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
            sub_rect = subtext.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))

            self.screen.blit(text, text_rect)
            self.screen.blit(subtext, sub_rect)
            
            # Back to menu instruction
            back = self.font.render("Press ESC to return to Menu", True, GRAY)
            self.screen.blit(back, back.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100)))

            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.level_index = 0
                self.load_level()

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
