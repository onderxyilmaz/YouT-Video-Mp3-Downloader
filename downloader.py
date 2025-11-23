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
from config import FFMPEG_URLS, DEFAULT_AUDIO_QUALITY, MAX_RETRY_ATTEMPTS, RETRY_DELAY, VIDEO_QUALITY_OPTIONS, AUDIO_QUALITY_OPTIONS
from utils import get_ffmpeg_location, check_ffmpeg, get_ffmpeg_path, format_speed


# Gelişmiş hata mesajları
ERROR_MESSAGES = {
    'network': 'İnternet bağlantısı hatası. Lütfen bağlantınızı kontrol edin.',
    'video_unavailable': 'Video bulunamadı veya kullanılamıyor.',
    'private_video': 'Bu video özel veya kısıtlı. Erişim izniniz yok.',
    'age_restricted': 'Bu video yaş kısıtlamalı. İndirilemedi.',
    'copyright': 'Telif hakkı nedeniyle video kullanılamıyor.',
    'geo_restricted': 'Bu video bölgenizde kullanılamıyor.',
    'live_stream': 'Canlı yayınlar şu anda desteklenmiyor.',
    'unknown': 'Bilinmeyen bir hata oluştu.'
}


def get_friendly_error_message(exception):
    """Kullanıcı dostu hata mesajı döndürür"""
    error_str = str(exception).lower()

    if 'network' in error_str or 'connection' in error_str or 'timeout' in error_str:
        return ERROR_MESSAGES['network']
    elif 'requested format is not available' in error_str or 'format is not available' in error_str:
        return 'Video formatı bulunamadı. Bu video için uygun format mevcut değil. Lütfen farklı bir video deneyin veya yt-dlp\'yi güncelleyin.'
    elif 'only images are available' in error_str:
        return 'Bu video için sadece görseller mevcut, video formatı bulunamadı. Lütfen farklı bir video deneyin.'
    elif 'unavailable' in error_str or 'not available' in error_str:
        return ERROR_MESSAGES['video_unavailable']
    elif 'private' in error_str:
        return ERROR_MESSAGES['private_video']
    elif 'age' in error_str:
        return ERROR_MESSAGES['age_restricted']
    elif 'copyright' in error_str:
        return ERROR_MESSAGES['copyright']
    elif 'geo' in error_str or 'region' in error_str:
        return ERROR_MESSAGES['geo_restricted']
    elif 'live' in error_str:
        return ERROR_MESSAGES['live_stream']
    else:
        return f"{ERROR_MESSAGES['unknown']}\nDetay: {str(exception)[:100]}"


class DownloadManager:
    """YouTube video/ses indirme işlemlerini yönetir"""

    def __init__(self, progress_callback=None, status_callback=None, max_retries=MAX_RETRY_ATTEMPTS):
        """
        Args:
            progress_callback: İlerleme güncellemeleri için callback (0.0-1.0 arası değer)
            status_callback: Durum mesajları için callback (message, color)
            max_retries: Maksimum deneme sayısı
        """
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.current_download_type = None
        self.video_downloaded = False
        self._last_progress_update = 0
        self.has_ffmpeg = check_ffmpeg()
        self.ffmpeg_path = get_ffmpeg_path()
        self.max_retries = max_retries

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

    def _postprocessor_hook(self, d):
        """yt-dlp postprocessor hook'u"""
        if d['status'] == 'started':
            self._update_status("FFmpeg ile birleştiriliyor...", "blue")
        elif d['status'] == 'finished':
            self._update_status("Birleştirme tamamlandı", "green")

    def _download_hook(self, d):
        """yt-dlp ilerleme hook'u"""
        # Debug: İndirilen format ID'yi logla
        if d['status'] == 'downloading' and 'info_dict' in d:
            try:
                debug_log_path = os.path.join(os.path.dirname(__file__), "download_debug.log")
                with open(debug_log_path, 'a', encoding='utf-8') as f:
                    import datetime
                    format_id = d['info_dict'].get('format_id', 'unknown')
                    format_note = d['info_dict'].get('format_note', 'unknown')
                    resolution = d['info_dict'].get('resolution', 'unknown')
                    f.write(f"\n[{datetime.datetime.now()}] İndirilen format:\n")
                    f.write(f"  - Format ID: {format_id}\n")
                    f.write(f"  - Format note: {format_note}\n")
                    f.write(f"  - Resolution: {resolution}\n")
            except:
                pass

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

    def download(self, url, output_path, download_type="video", auto_retry=True, video_quality=None, audio_quality=None):
        """
        Video/ses indirir (retry mekanizması ile)

        Args:
            url: YouTube video URL'si
            output_path: İndirme klasörü
            download_type: "video", "audio" veya "both"
            auto_retry: Otomatik yeniden deneme aktif mi?
            video_quality: Video kalite ayarı (ör: "En İyi", "1080p")
            audio_quality: Ses kalite ayarı (ör: "192 kbps")

        Returns:
            True: Başarılı

        Raises:
            Exception: İndirme hatası (tüm denemeler başarısız)
        """
        last_exception = None

        for attempt in range(self.max_retries if auto_retry else 1):
            try:
                if attempt > 0:
                    self._update_status(f"Yeniden deneniyor... ({attempt + 1}/{self.max_retries})", "orange")
                    time.sleep(RETRY_DELAY)

                return self._do_download(url, output_path, download_type, video_quality, audio_quality)

            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1 and auto_retry:
                    friendly_message = get_friendly_error_message(e)
                    self._update_status(f"{friendly_message} - Yeniden deneniyor...", "orange")
                else:
                    # Son deneme de başarısız
                    friendly_message = get_friendly_error_message(e)
                    self._update_status(friendly_message, "red")
                    raise Exception(friendly_message) from e

        # Buraya asla gelmemeli ama güvenlik için
        if last_exception:
            raise last_exception

    def _do_download(self, url, output_path, download_type="video", video_quality=None, audio_quality=None):
        """
        Video/ses indirir (asıl indirme işlemi)

        Args:
            url: YouTube video URL'si
            output_path: İndirme klasörü
            download_type: "video", "audio" veya "both"
            video_quality: Video kalite ayarı
            audio_quality: Ses kalite ayarı

        Returns:
            True: Başarılı

        Raises:
            Exception: İndirme hatası
        """
        # FFmpeg durumunu güncelle
        self.has_ffmpeg = check_ffmpeg()
        self.ffmpeg_path = get_ffmpeg_path()

        # Debug: İndirme başlangıcı
        self._update_status(f"İndirme başlıyor... Video Kalite: {video_quality}, FFmpeg: {'Evet' if self.has_ffmpeg else 'Hayır'}", "blue")

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
                'no_warnings': False,  # Uyarıları göster (debug için)
                'verbose': True,
                'postprocessor_hooks': [self._postprocessor_hook],
                'extractor_args': {
                    'youtube': {
                        # Default client kullan - PO Token gerektirmeyen ve en iyi formatları sunan
                        'player_client': ['default'],
                    }
                },
            }

            # FFmpeg konumunu ayarla - dizin yolunu kullan (yt-dlp için)
            if self.ffmpeg_path and os.path.exists(self.ffmpeg_path):
                ffmpeg_dir = os.path.dirname(self.ffmpeg_path)
                base_opts['ffmpeg_location'] = ffmpeg_dir

                # Debug: FFmpeg yolunu logla
                try:
                    debug_log_path = os.path.join(os.path.dirname(__file__), "download_debug.log")
                    with open(debug_log_path, 'a', encoding='utf-8') as f:
                        import datetime
                        f.write(f"\n[{datetime.datetime.now()}] FFmpeg ayarları:\n")
                        f.write(f"  - ffmpeg_path: {self.ffmpeg_path}\n")
                        f.write(f"  - ffmpeg_dir: {ffmpeg_dir}\n")
                        f.write(f"  - ffmpeg.exe exists: {os.path.exists(self.ffmpeg_path)}\n")
                except:
                    pass

            if download_type == "video":
                ydl_opts = self._get_video_opts(base_opts, video_quality)
            elif download_type == "audio":
                ydl_opts = self._get_audio_opts(base_opts, audio_quality)
            else:  # both
                self._download_both(url, output_path, base_opts, video_quality, audio_quality)
                return True

            # Logger ekle - verbose çıktıyı yakalamak için
            import logging
            debug_log_path = os.path.join(os.path.dirname(__file__), "ytdlp_verbose.log")

            # yt-dlp logger'ını yapılandır
            logger = logging.getLogger('yt-dlp')
            logger.setLevel(logging.DEBUG)

            # Uyarı filtreleme sınıfı
            class WarningFilter(logging.Filter):
                def filter(self, record):
                    message = record.getMessage()
                    # JavaScript runtime uyarılarını filtrele
                    if 'JavaScript runtime' in message:
                        return False
                    # SABR streaming uyarılarını filtrele
                    if 'SABR streaming' in message:
                        return False
                    # PO Token uyarılarını filtrele (default client kullanıyoruz, bu uyarılar gelmemeli)
                    if 'PO Token' in message:
                        return False
                    return True

            # Dosya handler ekle
            fh = logging.FileHandler(debug_log_path, encoding='utf-8')
            fh.setLevel(logging.DEBUG)
            fh.addFilter(WarningFilter())  # Filtreyi ekle
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            logger.addHandler(fh)

            # ydl_opts'a logger ekle
            ydl_opts['logger'] = logger

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

    def _get_video_opts(self, base_opts, video_quality=None):
        """Video indirme ayarlarını döndürür"""
        # Kalite ayarını belirle
        if video_quality and video_quality in VIDEO_QUALITY_OPTIONS:
            quality_format = VIDEO_QUALITY_OPTIONS[video_quality]
        else:
            # Varsayılan format: Çalışan örnekteki gibi basit ve etkili
            # bv* = bestvideo (herhangi bir format), ba = bestaudio
            # Son fallback: best (herhangi bir format)
            quality_format = 'bv*+ba/best'

        # Debug log dosyasına yaz
        debug_log_path = os.path.join(os.path.dirname(__file__), "download_debug.log")
        try:
            with open(debug_log_path, 'a', encoding='utf-8') as f:
                import datetime
                f.write(f"\n{'='*60}\n")
                f.write(f"Zaman: {datetime.datetime.now()}\n")
                f.write(f"Kalite ayarı: {video_quality}\n")
                f.write(f"Format string: {quality_format}\n")
                f.write(f"FFmpeg var mı: {self.has_ffmpeg}\n")
                f.write(f"FFmpeg yolu: {self.ffmpeg_path}\n")
                if self.ffmpeg_path and os.path.exists(self.ffmpeg_path):
                    f.write(f"FFmpeg location (base_opts): {os.path.dirname(self.ffmpeg_path)}\n")
                f.write(f"{'='*60}\n")
        except:
            pass

        # Debug: Kullanılan format'ı göster
        self._update_status(f"Kalite: {video_quality or 'Varsayılan'} | Format: {quality_format[:50]}", "blue")

        if self.has_ffmpeg:
            return {
                **base_opts,
                'format': quality_format,
                'merge_output_format': 'mp4',  # FFmpeg ile birleştirirken MP4 kullan
            }
        else:
            # FFmpeg yoksa tek format kullan (birleştirme gerektirmeyen)
            # En iyi formatı seç
            return {
                **base_opts,
                'format': 'best',
            }

    def _get_audio_opts(self, base_opts, audio_quality=None):
        """Ses indirme ayarlarını döndürür"""
        # Kalite ayarını belirle (kbps değerini al)
        if audio_quality and audio_quality in AUDIO_QUALITY_OPTIONS:
            quality_value = AUDIO_QUALITY_OPTIONS[audio_quality]
        else:
            quality_value = DEFAULT_AUDIO_QUALITY

        if self.has_ffmpeg:
            return {
                **base_opts,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality_value,
                }],
            }
        else:
            return {
                **base_opts,
                'format': 'bestaudio/best',
            }

    def _download_both(self, url, output_path, base_opts, video_quality=None, audio_quality=None):
        """Video ve ses'i ayrı ayrı indirir"""
        if not self.has_ffmpeg:
            self._update_status("FFmpeg bulunamadı! Sadece video indiriliyor...", "orange")

        # Logger ekle - verbose çıktıyı yakalamak için
        import logging
        debug_log_path = os.path.join(os.path.dirname(__file__), "ytdlp_verbose.log")
        logger = logging.getLogger('yt-dlp')
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(debug_log_path, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # Önce video indir
        self.video_downloaded = False
        self._update_progress(0)
        self._update_status("Video indiriliyor...", "yellow")

        ydl_opts_video = self._get_video_opts(base_opts, video_quality)
        ydl_opts_video['logger'] = logger
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            ydl.download([url])

        # Video tamamlandı, ses indirmeye geç
        self.video_downloaded = True
        self._update_progress(0.5)
        self._update_status("Ses indiriliyor...", "yellow")

        # Ses dosyası için farklı isim kullan
        audio_opts = self._get_audio_opts(base_opts, audio_quality)
        audio_opts['outtmpl'] = os.path.join(output_path, '%(title)s_audio.%(ext)s')
        audio_opts['logger'] = logger
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
