"""
YouTube indirme işlemlerini yöneten modül
"""
import os
import yt_dlp
import requests
import zipfile
import shutil
import platform
import time
from config import FFMPEG_URLS, DEFAULT_AUDIO_QUALITY
from utils import get_ffmpeg_location, check_ffmpeg, get_ffmpeg_path, format_speed


class DownloadManager:
    """YouTube video/ses indirme işlemlerini yönetir"""

    def __init__(self, progress_callback=None, status_callback=None):
        """
        Args:
            progress_callback: İlerleme güncellemeleri için callback (0.0-1.0 arası değer)
            status_callback: Durum mesajları için callback (message, color)
        """
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.current_download_type = None
        self.video_downloaded = False
        self._last_progress_update = 0
        self.has_ffmpeg = check_ffmpeg()
        self.ffmpeg_path = get_ffmpeg_path()

    def _update_progress(self, value):
        """İlerleme çubuğunu günceller (throttle ile)"""
        current_time = time.time()
        if current_time - self._last_progress_update >= 0.1:  # 100ms throttle
            if self.progress_callback:
                self.progress_callback(max(0.0, min(1.0, float(value))))
            self._last_progress_update = current_time

    def _update_status(self, message, color="gray"):
        """Durum mesajını günceller"""
        if self.status_callback:
            self.status_callback(message, color)

    def _download_hook(self, d):
        """yt-dlp ilerleme hook'u"""
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                progress = downloaded / total

                # "both" durumunda progress'i ayarla
                if self.current_download_type == "both":
                    if not self.video_downloaded:
                        # Video indiriliyor: 0-0.5 aralığı
                        mapped_progress = progress * 0.5
                        self._update_progress(mapped_progress)
                        speed = d.get('speed', 0)
                        if speed:
                            self._update_status(f"Video indiriliyor... {format_speed(speed)}", "yellow")
                    else:
                        # Ses indiriliyor: 0.5-1.0 aralığı
                        mapped_progress = 0.5 + (progress * 0.5)
                        self._update_progress(mapped_progress)
                        speed = d.get('speed', 0)
                        if speed:
                            self._update_status(f"Ses indiriliyor... {format_speed(speed)}", "yellow")
                else:
                    # Normal durum (video veya audio tek başına)
                    self._update_progress(progress)
                    speed = d.get('speed', 0)
                    if speed:
                        self._update_status(f"İndiriliyor... {format_speed(speed)}", "yellow")
        elif d['status'] == 'finished':
            if self.current_download_type == "both":
                if not self.video_downloaded:
                    self._update_progress(0.5)
                    self._update_status("Video tamamlandı, ses indiriliyor...", "yellow")
                    self.video_downloaded = True
                else:
                    self._update_progress(1.0)
                    self._update_status("İndirme tamamlandı!", "green")
            else:
                self._update_progress(1.0)
                self._update_status("İndirme tamamlandı!", "green")

    def download(self, url, output_path, download_type="video"):
        """
        Video/ses indirir

        Args:
            url: YouTube video URL'si
            output_path: İndirme klasörü
            download_type: "video", "audio" veya "both"

        Returns:
            True: Başarılı
            False: Hata oluştu

        Raises:
            Exception: İndirme hatası
        """
        # FFmpeg durumunu güncelle
        self.has_ffmpeg = check_ffmpeg()
        self.ffmpeg_path = get_ffmpeg_path()

        # İndirme tipini ayarla
        self.current_download_type = download_type
        self.video_downloaded = False

        try:
            # Ortak ayarlar
            base_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._download_hook],
                'noplaylist': True,
                'quiet': False,
                'no_warnings': False,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                    }
                },
            }

            # FFmpeg konumunu ayarla
            ffmpeg_location = get_ffmpeg_location()
            if ffmpeg_location:
                base_opts['ffmpeg_location'] = ffmpeg_location

            if download_type == "video":
                ydl_opts = self._get_video_opts(base_opts)
            elif download_type == "audio":
                ydl_opts = self._get_audio_opts(base_opts)
            else:  # both
                self._download_both(url, output_path, base_opts)
                return True

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self._update_status("İndirme tamamlandı!", "green")
            self._update_progress(1.0)
            return True

        except Exception as e:
            self._update_status(f"Hata: {str(e)[:50]}...", "red")
            raise

        finally:
            self.current_download_type = None
            self.video_downloaded = False

    def _get_video_opts(self, base_opts):
        """Video indirme ayarlarını döndürür"""
        if self.has_ffmpeg:
            return {
                **base_opts,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            }
        else:
            return {
                **base_opts,
                'format': 'best[ext=mp4]/best',
            }

    def _get_audio_opts(self, base_opts):
        """Ses indirme ayarlarını döndürür"""
        if self.has_ffmpeg:
            return {
                **base_opts,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': DEFAULT_AUDIO_QUALITY,
                }],
            }
        else:
            return {
                **base_opts,
                'format': 'bestaudio/best',
            }

    def _download_both(self, url, output_path, base_opts):
        """Video ve ses'i ayrı ayrı indirir"""
        if not self.has_ffmpeg:
            self._update_status("FFmpeg bulunamadı! Sadece video indiriliyor...", "orange")

        # Önce video indir
        self.video_downloaded = False
        self._update_progress(0)
        self._update_status("Video indiriliyor...", "yellow")

        ydl_opts_video = self._get_video_opts(base_opts)
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            ydl.download([url])

        # Video tamamlandı, ses indirmeye geç
        self.video_downloaded = True
        self._update_progress(0.5)
        self._update_status("Ses indiriliyor...", "yellow")

        # Ses dosyası için farklı isim kullan
        audio_opts = self._get_audio_opts(base_opts)
        audio_opts['outtmpl'] = os.path.join(output_path, '%(title)s_audio.%(ext)s')

        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])

        self._update_progress(1.0)
        self._update_status("İndirme tamamlandı!", "green")


class FFmpegInstaller:
    """FFmpeg otomatik kurulum işlemlerini yönetir"""

    def __init__(self, progress_callback=None, status_callback=None):
        """
        Args:
            progress_callback: İlerleme güncellemeleri için callback (0.0-1.0 arası değer)
            status_callback: Durum mesajları için callback (message, color)
        """
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self._last_progress_update = 0

    def _update_progress(self, value):
        """İlerleme çubuğunu günceller (throttle ile)"""
        current_time = time.time()
        if current_time - self._last_progress_update >= 0.1:
            if self.progress_callback:
                self.progress_callback(max(0.0, min(1.0, float(value))))
            self._last_progress_update = current_time

    def _update_status(self, message, color="gray"):
        """Durum mesajını günceller"""
        if self.status_callback:
            self.status_callback(message, color)

    def install(self):
        """
        FFmpeg'i indirir ve kurar

        Returns:
            True: Başarılı
            False: Hata oluştu

        Raises:
            Exception: Kurulum hatası
        """
        if platform.system() != "Windows":
            raise Exception("Otomatik kurulum şu anda sadece Windows için desteklenmektedir.")

        # Geçici klasörü hazırla
        temp_dir = os.path.join(os.path.dirname(__file__), "temp_ffmpeg")
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

        try:
            self._update_status("Başlatılıyor...", "blue")
            self._update_progress(0.05)

            # Geçici klasörü oluştur
            os.makedirs(temp_dir, exist_ok=True)
            zip_path = os.path.join(temp_dir, "ffmpeg.zip")

            # İndirme
            self._download_ffmpeg(zip_path)

            # Çıkarma
            self._update_status("FFmpeg çıkarılıyor...", "blue")
            self._update_progress(0.7)
            self._extract_ffmpeg(zip_path, temp_dir)

            # Kopyalama
            self._update_progress(0.95)
            target_path = self._copy_ffmpeg_exe(temp_dir)

            # Temizlik
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

            self._update_progress(1.0)
            self._update_status("FFmpeg başarıyla kuruldu!", "green")
            return True

        except Exception as e:
            self._update_status(f"Kurulum hatası: {str(e)}", "red")
            raise

        finally:
            self._update_progress(0)

    def _download_ffmpeg(self, zip_path):
        """FFmpeg'i indir"""
        self._update_status("FFmpeg indiriliyor... (Bu biraz zaman alabilir)", "blue")

        for url_idx, ffmpeg_url in enumerate(FFMPEG_URLS):
            try:
                self._update_status(f"İndirme deneniyor... ({url_idx + 1}/{len(FFMPEG_URLS)})", "blue")
                response = requests.get(ffmpeg_url, stream=True, timeout=180, allow_redirects=True)
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                self._update_progress(0.1)

                with open(zip_path, 'wb') as f:
                    last_progress = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = 0.1 + (downloaded / total_size) * 0.6
                                if progress - last_progress >= 0.01 or progress >= 0.7:
                                    self._update_progress(min(progress, 0.7))
                                    last_progress = progress
                return  # Başarılı, döngüden çık

            except Exception as e:
                if url_idx < len(FFMPEG_URLS) - 1:
                    continue
                raise Exception(f"Tüm indirme kaynakları başarısız. Son hata: {str(e)}")

    def _extract_ffmpeg(self, zip_path, temp_dir):
        """ZIP dosyasını çıkar"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile:
            raise Exception("İndirilen dosya bozuk ZIP dosyası. Lütfen tekrar deneyin.")

    def _copy_ffmpeg_exe(self, temp_dir):
        """ffmpeg.exe'yi bul ve kopyala"""
        ffmpeg_exe_path = None

        for root, dirs, files in os.walk(temp_dir):
            if 'ffmpeg.exe' in files:
                ffmpeg_exe_path = os.path.join(root, "ffmpeg.exe")
                break

        if not ffmpeg_exe_path or not os.path.exists(ffmpeg_exe_path):
            raise Exception("ffmpeg.exe bulunamadı")

        target_path = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")

        try:
            shutil.copy2(ffmpeg_exe_path, target_path)
        except Exception as e:
            raise Exception(f"ffmpeg.exe kopyalanamadı: {str(e)}")

        if not os.path.exists(target_path):
            raise Exception("ffmpeg.exe kopyalandı ancak hedef konumda bulunamadı")

        return target_path
