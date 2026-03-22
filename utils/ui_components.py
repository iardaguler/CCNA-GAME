import pygame
import random
from settings import *

class TransitionScreen:
    def __init__(self, screen, next_level_name, duration_ms=3000):
        self.screen = screen
        self.next_level_name = next_level_name
        self.duration = duration_ms
        self.start_time = pygame.time.get_ticks()
        self.progress = 0
        self.finished = False
        
        self.font_big = pygame.font.SysFont(FONT_NAME, 50, bold=True)
        self.font_small = pygame.font.SysFont(FONT_NAME, 20)
        
        self.messages = [
            "Handshaking with remote host...",
            "Establishing encrypted tunnel...",
            "Loading network protocols...",
            "Synchronizing routing tables...",
            "Checking firewall integrity...",
            "Initializing secure session...",
            "Verifying administrator credentials...",
            "Allocating memory buffers...",
            "Finalizing connection parameters..."
        ]
        self.current_message = self.messages[0]
        self.last_msg_change = self.start_time
        
        # Matrix-like background effect
        self.hex_chars = "0123456789ABCDEF"
        self.matrix_chars = []
        for _ in range(30):
            self.matrix_chars.append({
                "x": random.randint(0, SCREEN_WIDTH),
                "y": random.randint(0, SCREEN_HEIGHT),
                "speed": random.randint(2, 8),
                "val": random.choice(self.hex_chars)
            })

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        self.progress = min(elapsed / self.duration, 1.0)
        
        if self.progress >= 1.0:
            self.finished = True
            
        # Change message every 600ms
        if now - self.last_msg_change > 600:
            self.current_message = random.choice(self.messages)
            self.last_msg_change = now
            
        # Update matrix background
        for char in self.matrix_chars:
            char["y"] += char["speed"]
            if char["y"] > SCREEN_HEIGHT:
                char["y"] = -20
                char["x"] = random.randint(0, SCREEN_WIDTH)
            if random.random() < 0.1:
                char["val"] = random.choice(self.hex_chars)

    def draw(self):
        self.screen.fill((5, 10, 15))
        
        # Draw Matrix Background
        for char in self.matrix_chars:
            txt = self.font_small.render(char["val"], True, (0, 60, 0))
            self.screen.blit(txt, (char["x"], char["y"]))
            
        # Title
        title_surf = self.font_big.render(f"ACCESSING {self.next_level_name}...", True, NEON_GREEN)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(title_surf, title_rect)
        
        # Progress Bar Outer
        bar_w, bar_h = 600, 30
        bar_x = (SCREEN_WIDTH - bar_w) // 2
        bar_y = SCREEN_HEIGHT // 2
        
        pygame.draw.rect(self.screen, (30, 30, 30), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(self.screen, NEON_GREEN, (bar_x, bar_y, bar_w, bar_h), 2)
        
        # Progress Bar Inner (Fills up)
        fill_w = int(bar_w * self.progress)
        if fill_w > 0:
            pygame.draw.rect(self.screen, NEON_GREEN, (bar_x + 4, bar_y + 4, fill_w - 8, bar_h - 8))
            
            # Add a "scan" glow effect to the bar
            glow_x = bar_x + 4 + (fill_w - 18)
            if glow_x > bar_x + 4:
                pygame.draw.rect(self.screen, (200, 255, 200), (glow_x, bar_y + 4, 10, bar_h - 8))

        # Percentage
        perc_text = f"{int(self.progress * 100)}%"
        perc_surf = self.font_small.render(perc_text, True, WHITE)
        self.screen.blit(perc_surf, (bar_x + bar_w + 15, bar_y + 5))

        # Status Message
        msg_surf = self.font_small.render(self.current_message, True, (150, 150, 150))
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, bar_y + 60))
        self.screen.blit(msg_surf, msg_rect)
        
        # "ENCRYPTING..." animation
        if (pygame.time.get_ticks() // 200) % 4 != 0:
            dots = "." * ((pygame.time.get_ticks() // 400) % 4)
            loading_txt = self.font_small.render("SECURE CONNECTION ACTIVE" + dots, True, NEON_GREEN)
            self.screen.blit(loading_txt, (20, SCREEN_HEIGHT - 40))
