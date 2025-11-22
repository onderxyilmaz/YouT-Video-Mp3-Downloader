"""
Uygulama konfigürasyonu ve sabitler
"""
import os
import json
from pathlib import Path


# Uygulama sabitleri
APP_VERSION = "v1.0.0"
APP_NAME = "YouT Video Mp3 Downloader"
DEVELOPER_NAME = "UnderSpeed"

# Pencere boyutları
WINDOW_WIDTH = 745
WINDOW_HEIGHT = 745

# URL pattern'leri
YOUTUBE_DOMAINS = ['youtube.com', 'youtu.be']
VIDEO_ID_PATTERNS = [
    r'(?:youtube\.com/watch\?v=|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})',
    r'youtu\.be/([a-zA-Z0-9_-]{11})',
    r'[?&]v=([a-zA-Z0-9_-]{11})'
]

# FFmpeg kurulum URL'leri
FFMPEG_URLS = [
    "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
    "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
]

# İndirme ayarları
DEFAULT_AUDIO_QUALITY = '192'
DEFAULT_VIDEO_FORMAT = 'mp4'
DEFAULT_AUDIO_FORMAT = 'mp3'

# İlerleme güncelleme ayarları
PROGRESS_UPDATE_THROTTLE = 0.1  # saniye (100ms)
URL_CHECK_DEBOUNCE = 500  # milisaniye


class Config:
    """Kullanıcı ayarlarını yönetir"""

    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), "config.json")
        self._config = self._load_config()

    def _load_config(self):
        """Config dosyasını yükler"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Config dosyası okunamadı: {e}")
        return {}

    def _save_config(self):
        """Config dosyasını kaydeder"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Config dosyası yazılamadı: {e}")

    def get(self, key, default=None):
        """Ayar değerini döndürür"""
        return self._config.get(key, default)

    def set(self, key, value):
        """Ayar değerini günceller ve kaydeder"""
        self._config[key] = value
        self._save_config()

    def get_last_download_folder(self):
        """Son seçilen indirme klasörünü döndürür"""
        folder = self.get('last_download_folder')
        if folder and os.path.exists(folder):
            return folder
        return None

    def set_last_download_folder(self, folder_path):
        """Son seçilen indirme klasörünü kaydeder"""
        self.set('last_download_folder', folder_path)
