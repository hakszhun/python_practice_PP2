import pygame
import os

class MusicPlayer:
    def __init__(self, music_folder):
        self.music_folder = music_folder
        self.playlist = []
        self.current_track_index = 0
        self.is_stopped = True  
        
        
        if os.path.exists(self.music_folder):
            self.load_playlist()
        
    def load_playlist(self):
        supported_formats = ('.mp3', '.wav')
        for file in os.listdir(self.music_folder):
            if file.lower().endswith(supported_formats):
                self.playlist.append(os.path.join(self.music_folder, file))
    
    def play(self):
        if not self.playlist:
            return

        if self.is_stopped:
            pygame.mixer.music.load(self.playlist[self.current_track_index])
            pygame.mixer.music.play()
            self.is_stopped = False
        else:
            # Если музыка была на паузе 
            pygame.mixer.music.unpause()
    
    def stop(self):
        pygame.mixer.music.stop()
        self.is_stopped = True  
    
    def next_track(self):
        if self.playlist:
            self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
            self.is_stopped = True # Сбрасываем флаг, чтобы play загрузил новый трек
            self.play()
    
    def previous_track(self):
        if self.playlist:
            self.current_track_index = (self.current_track_index - 1) % len(self.playlist)
            self.is_stopped = True
            self.play()
    
    def get_current_track_name(self):
        if self.playlist and not self.is_stopped:
            return os.path.basename(self.playlist[self.current_track_index])
        return "Stopped / No tracks"

    def get_playlist_info(self):
        if not self.playlist:
            return "Playlist is empty"
        return f"Track {self.current_track_index + 1}/{len(self.playlist)}"