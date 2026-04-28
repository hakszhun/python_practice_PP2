import json
import os

class SettingsManager:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.default_settings = {
            "snake_color": [0, 255, 0],  # Green
            "grid_overlay": True,
            "sound_enabled": True
        }
        self.settings = self.load_settings()
    
    def load_settings(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return self.default_settings.copy()
        else:
            self.save_settings(self.default_settings)
            return self.default_settings.copy()
    
    def save_settings(self, settings=None):
        if settings is None:
            settings = self.settings
        with open(self.filename, 'w') as f:
            json.dump(settings, f, indent=4)
    
    def get(self, key):
        return self.settings.get(key, self.default_settings.get(key))
    
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()