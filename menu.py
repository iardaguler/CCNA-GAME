import pygame
import sys
from settings import *


class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        # Başlık için büyük font
        self.font_big = pygame.font.SysFont(FONT_NAME, 80, bold=True)
        # Butonlar için küçültülmüş ve güvenli font (Taşmayı önler)
        self.font_button = pygame.font.SysFont(FONT_NAME, 30, bold=True)
        # Alt bilgi fontu
        self.font_small = pygame.font.SysFont(FONT_NAME, 20)

        self.start_game = False

        # İmleç animasyonu için
        self.blink_timer = 0
        self.show_cursor = True

        # --- BUTON AYARLARI ---
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        # Buton boyutlarını genişlettik (Genişlik: 500px, Yükseklik: 60px)
        self.btn_width = 500
        self.btn_height = 60

        # Buton Konumları (Tam ortalamak için matematiksel hesap)
        self.btn_play_rect = pygame.Rect(center_x - (self.btn_width // 2), center_y + 40, self.btn_width,
                                         self.btn_height)
        self.btn_quit_rect = pygame.Rect(center_x - (self.btn_width // 2), center_y + 130, self.btn_width,
                                         self.btn_height)

    def events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Oyna Butonu
            if self.btn_play_rect.collidepoint(mouse_pos):
                self.start_game = True

            # Çıkış Butonu
            if self.btn_quit_rect.collidepoint(mouse_pos):
                pygame.quit()
                sys.exit()

    def update(self):
        # İmleç yanıp sönme hızı
        self.blink_timer += 1
        if self.blink_timer > 30:
            self.show_cursor = not self.show_cursor
            self.blink_timer = 0

    def draw_button(self, rect, text, base_color, hover_color, mouse_pos):
        """
        Profesyonel buton çizme fonksiyonu.
        Bu fonksiyon hem arkaplanı hem yazıyı hatasız hizalar.
        """
        is_hovered = rect.collidepoint(mouse_pos)

        # Renkleri belirle
        if is_hovered:
            # Üzerine gelince: İçi Dolu Renkli, Yazı Siyah
            bg_color = hover_color
            text_color = BLACK
            pygame.draw.rect(self.screen, bg_color, rect)  # İçi dolu çizim
        else:
            # Normal: İçi Boş (Siyah), Çerçeve Renkli, Yazı Renkli
            bg_color = BLACK
            border_color = base_color
            text_color = base_color
            pygame.draw.rect(self.screen, border_color, rect, 2)  # Sadece çerçeve (2px)

        # Yazıyı oluştur
        text_surf = self.font_button.render(text, True, text_color)

        # Yazıyı butonun tam geometrik merkezine yerleştir
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw(self):
        self.screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()

        # --- BAŞLIK ---
        title_text = self.font_big.render("CCNA-GAME MASTER", True, NEON_GREEN)
        subtitle_text = self.font_button.render("NETWORK DEFENDER SIMULATION", True, WHITE)

        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        sub_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 250))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, sub_rect)

        # Çizgi
        pygame.draw.line(self.screen, NEON_GREEN, (SCREEN_WIDTH // 2 - 250, 230), (SCREEN_WIDTH // 2 + 250, 230), 4)

        # --- BUTONLARI ÇİZ ---
        # Helper fonksiyon kullanarak sıfır hata ile çiziyoruz

        # 1. Başlat Butonu (Yeşil Tema)
        self.draw_button(
            rect=self.btn_play_rect,
            text="ESTABLISH CONNECTION",
            base_color=NEON_GREEN,
            hover_color=NEON_GREEN,
            mouse_pos=mouse_pos
        )

        # 2. Çıkış Butonu (Kırmızı Tema)
        self.draw_button(
            rect=self.btn_quit_rect,
            text="TERMINATE SESSION",
            base_color=(200, 50, 50),  # Biraz daha koyu kırmızı normal hali için
            hover_color=(255, 50, 50),  # Parlak kırmızı hover için
            mouse_pos=mouse_pos
        )

        # --- ALT BİLGİ ---
        if self.show_cursor:
            cursor_text = self.font_small.render("_", True, NEON_GREEN)
            self.screen.blit(cursor_text, (20, SCREEN_HEIGHT - 40))

        ver_text = self.font_small.render("System v1.0 | Secure Shell", True, GRAY)
        ver_rect = ver_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        self.screen.blit(ver_text, ver_rect)