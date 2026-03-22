import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.music_path = "assets/audio/game-music.wav"
        self.success_path = "assets/audio/level-completed.wav"
        
        self.music_enabled = True
        self.volume = 0.5
        
        # Load Success SFX
        self.success_sfx = None
        if os.path.exists(self.success_path):
            try:
                self.success_sfx = pygame.mixer.Sound(self.success_path)
                self.success_sfx.set_volume(self.volume)
            except Exception as e:
                print(f"Error loading SFX: {e}")

    def play_music(self, loop=-1):
        if self.music_enabled and os.path.exists(self.music_path):
            try:
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(loop)
            except Exception as e:
                print(f"Error playing music: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()
            
    def play_success(self):
        if self.music_enabled and self.success_sfx:
            self.success_sfx.play()

# Global Instance
sound_manager = SoundManager()
