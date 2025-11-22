"""
Yardımcı fonksiyonlar ve araçlar
"""
import os
import re
import platform
import shutil
from config import YOUTUBE_DOMAINS, VIDEO_ID_PATTERNS


def validate_url(url):
    """URL'nin geçerli bir YouTube video URL'si olup olmadığını kontrol eder"""
    if not url or not url.strip():
        return False

    url = url.strip()

    # YouTube domain kontrolü
    has_youtube_domain = any(domain in url for domain in YOUTUBE_DOMAINS)

    if not has_youtube_domain:
        return False

    # Video ID pattern'lerini kontrol et
    for pattern in VIDEO_ID_PATTERNS:
        if re.search(pattern, url):
            return True

    # Eğer sadece domain varsa ama video ID yoksa geçersiz
    return False


def get_default_downloads_folder():
    """Varsayılan Downloads klasörünü bulur"""
    try:
        # Önce standart yolu dene
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.exists(downloads_path):
            return downloads_path

        # Windows'ta alternatif yolları dene
        if platform.system() == "Windows":
            user_profile = os.environ.get('USERPROFILE', '')
            if user_profile:
                alt_paths = [
                    os.path.join(user_profile, "Downloads"),
                    os.path.join(user_profile, "İndirilenler"),  # Türkçe Windows
                ]
                for path in alt_paths:
                    if os.path.exists(path):
                        return path

        # Bulunamazsa proje klasörünü kullan
        return os.path.dirname(__file__)
    except:
        return os.path.dirname(__file__)


def check_ffmpeg():
    """FFmpeg'in kurulu olup olmadığını kontrol eder"""
    # Önce sistem PATH'inde kontrol et
    if shutil.which("ffmpeg") is not None:
        return True
    # Sonra proje klasöründe kontrol et
    local_ffmpeg = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
    return os.path.exists(local_ffmpeg)


def get_ffmpeg_path():
    """FFmpeg'in yolunu döndürür"""
    # Önce sistem PATH'inde kontrol et
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    # Sonra proje klasöründe kontrol et
    local_ffmpeg = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
    if os.path.exists(local_ffmpeg):
        return local_ffmpeg
    return None


def get_ffmpeg_location():
    """yt-dlp için FFmpeg konumunu döndürür (sadece dizin)"""
    ffmpeg_path = get_ffmpeg_path()
    if ffmpeg_path and os.path.exists(ffmpeg_path):
        return os.path.dirname(ffmpeg_path)
    return None


def format_bytes(bytes_value):
    """Byte değerini okunabilir formata çevirir"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"


def format_speed(speed):
    """İndirme hızını MB/s formatında döndürür"""
    if not speed:
        return "0.00 MB/s"
    speed_mb = speed / (1024 * 1024)
    return f"{speed_mb:.2f} MB/s"
