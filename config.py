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
WINDOW_HEIGHT = 750

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
DEFAULT_DOWNLOAD_TYPE = 'video'

# Retry ayarları
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # saniye

# İlerleme güncelleme ayarları
PROGRESS_UPDATE_THROTTLE = 0.1  # saniye (100ms)
URL_CHECK_DEBOUNCE = 500  # milisaniye

# Kalite seçenekleri
# Format string'leri: Çalışan örnekteki gibi basit ve etkili
# bv* = bestvideo (herhangi bir format), ba = bestaudio
# Son fallback: best (herhangi bir format)
VIDEO_QUALITY_OPTIONS = {
    'En İyi': 'bv*+ba/best',
    '1080p': 'bv*[height<=1080]+ba/best[height<=1080]',
    '720p': 'bv*[height<=720]+ba/best[height<=720]',
    '480p': 'bv*[height<=480]+ba/best[height<=480]',
    '360p': 'bv*[height<=360]+ba/best[height<=360]'
}

AUDIO_QUALITY_OPTIONS = {
    '320 kbps': '320',
    '256 kbps': '256',
    '192 kbps': '192',
    '128 kbps': '128'
}


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

    # Kalite ayarları
    def get_video_quality(self):
        """Video kalitesi ayarını döndürür"""
        return self.get('video_quality', 'En İyi')

    def set_video_quality(self, quality):
        """Video kalitesi ayarını kaydeder"""
        self.set('video_quality', quality)

    def get_audio_quality(self):
        """Ses kalitesi ayarını döndürür"""
        return self.get('audio_quality', '192 kbps')

    def set_audio_quality(self, quality):
        """Ses kalitesi ayarını kaydeder"""
        self.set('audio_quality', quality)

    # İndirme tipi
    def get_default_download_type(self):
        """Varsayılan indirme tipini döndürür"""
        return self.get('default_download_type', DEFAULT_DOWNLOAD_TYPE)

    def set_default_download_type(self, download_type):
        """Varsayılan indirme tipini kaydeder"""
        self.set('default_download_type', download_type)

    # Retry ayarları
    def get_max_retries(self):
        """Maximum retry sayısını döndürür"""
        return self.get('max_retries', MAX_RETRY_ATTEMPTS)

    def set_max_retries(self, count):
        """Maximum retry sayısını kaydeder"""
        self.set('max_retries', count)

    def get_auto_retry(self):
        """Otomatik retry aktif mi?"""
        return self.get('auto_retry', True)

    def set_auto_retry(self, enabled):
        """Otomatik retry ayarını kaydeder"""
        self.set('auto_retry', enabled)
