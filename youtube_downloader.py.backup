import customtkinter as ctk
import yt_dlp
import os
import threading
import subprocess
import shutil
import requests
import zipfile
import platform
import time
import json
import re
from pathlib import Path
from tkinter import filedialog, messagebox

# CustomTkinter tema ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Uygulama versiyonu
APP_VERSION = "v1.0.0"

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouT Video Mp3 Downloader")
        
        # Pencere boyutu
        window_width = 745
        window_height = 745
        
        # Masaüstünün ortasını hesapla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)  # Pencere boyutu sabit
        
        # Maximize'i engelle - maxsize ve minsize aynı yaparak
        self.root.maxsize(window_width, window_height)
        self.root.minsize(window_width, window_height)
        
        # İndirme durumu
        self.downloading = False
        self.installing_ffmpeg = False
        self.current_download_type = None  # "video", "audio", "both"
        self.video_downloaded = False  # "both" durumunda video indirildi mi?
        
        # FFmpeg kontrolü
        self.has_ffmpeg = self.check_ffmpeg()
        self.ffmpeg_path = self.get_ffmpeg_path()
        
        # Config dosyası yolu
        self.config_file = os.path.join(os.path.dirname(__file__), "config.json")
        
        # URL kontrolü için debounce timer
        self.url_check_timer = None
        
        self.create_widgets()
    
    def get_default_downloads_folder(self):
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
    
    def load_last_folder(self):
        """Son seçilen klasörü config dosyasından yükler"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    last_folder = config.get('last_download_folder', None)
                    if last_folder and os.path.exists(last_folder):
                        return last_folder
        except Exception as e:
            print(f"Config dosyası okunamadı: {e}")
        return None
    
    def save_last_folder(self, folder_path):
        """Seçilen klasörü config dosyasına kaydeder"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                except:
                    config = {}
            
            config['last_download_folder'] = folder_path
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Config dosyası yazılamadı: {e}")
        
    def create_widgets(self):
        # Ana frame (scroll olmadan)
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ctk.CTkLabel(
            main_frame, 
            text="YouT Video Mp3 Downloader",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # Versiyon bilgisi
        version_label = ctk.CTkLabel(
            main_frame,
            text=APP_VERSION,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        version_label.pack(pady=(0, 10))
        
        # FFmpeg durumu ve kurulum butonu
        self.ffmpeg_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.ffmpeg_frame.pack(pady=(0, 20))
        
        if self.has_ffmpeg:
            self.ffmpeg_status_label = ctk.CTkLabel(
                self.ffmpeg_frame,
                text="✓ FFmpeg bulundu - Tüm özellikler aktif",
                font=ctk.CTkFont(size=11),
                text_color="green"
            )
            self.ffmpeg_status_label.pack()
        else:
            self.ffmpeg_status_label = ctk.CTkLabel(
                self.ffmpeg_frame,
                text="⚠ FFmpeg bulunamadı - Bazı özellikler sınırlı olabilir",
                font=ctk.CTkFont(size=11),
                text_color="orange"
            )
            self.ffmpeg_status_label.pack(pady=(0, 5))
            
            # FFmpeg kurulum butonu (sadece Windows için)
            if platform.system() == "Windows":
                self.install_ffmpeg_button = ctk.CTkButton(
                    self.ffmpeg_frame,
                    text="FFmpeg'i Otomatik Kur",
                    command=self.install_ffmpeg,
                    height=30,
                    font=ctk.CTkFont(size=11),
                    fg_color="#2d8659",
                    hover_color="#1f5c3f"
                )
                self.install_ffmpeg_button.pack(pady=(5, 0))
        
        # URL girişi
        url_frame = ctk.CTkFrame(main_frame)
        url_frame.pack(fill="x", padx=20, pady=10)
        
        url_label = ctk.CTkLabel(url_frame, text="YouTube URL:", font=ctk.CTkFont(size=14))
        url_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # URL entry ve temizleme butonu için frame
        url_input_frame = ctk.CTkFrame(url_frame, fg_color="transparent")
        url_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.url_entry = ctk.CTkEntry(
            url_input_frame,
            placeholder_text="https://www.youtube.com/watch?v=...",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.url_entry.focus()
        self.url_entry.bind("<Control-a>", lambda e: self.url_entry.select_range(0, "end"))
        # URL değiştiğinde debounce ile kontrol et (500ms bekle)
        self.url_entry.bind("<KeyRelease>", lambda e: self.debounced_check_url())
        self.url_entry.bind("<FocusOut>", lambda e: self.check_url_and_update_button())
        
        # Temizleme butonu (X ikonu)
        self.clear_url_button = ctk.CTkButton(
            url_input_frame,
            text="✕",
            command=self.clear_url,
            width=40,
            height=40,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color="#3a3a3a",
            text_color="gray"
        )
        self.clear_url_button.pack(side="right")
        self.clear_url_button.pack_forget()  # Başlangıçta gizli
        
        # İndirme tipi seçimi
        download_type_frame = ctk.CTkFrame(main_frame)
        download_type_frame.pack(fill="x", padx=20, pady=10)
        
        type_label = ctk.CTkLabel(download_type_frame, text="İndirme Tipi:", font=ctk.CTkFont(size=14))
        type_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.download_type = ctk.StringVar(value="video")
        
        self.video_radio = ctk.CTkRadioButton(
            download_type_frame,
            text="Video (MP4)",
            variable=self.download_type,
            value="video",
            font=ctk.CTkFont(size=12)
        )
        self.video_radio.pack(anchor="w", padx=20, pady=5)
        
        self.audio_radio = ctk.CTkRadioButton(
            download_type_frame,
            text="Sadece Ses (MP3)",
            variable=self.download_type,
            value="audio",
            font=ctk.CTkFont(size=12)
        )
        self.audio_radio.pack(anchor="w", padx=20, pady=5)
        
        self.both_radio = ctk.CTkRadioButton(
            download_type_frame,
            text="Video ve Ses (Her İkisi)",
            variable=self.download_type,
            value="both",
            font=ctk.CTkFont(size=12)
        )
        self.both_radio.pack(anchor="w", padx=20, pady=(5, 10))
        
        # Klasör seçimi
        folder_frame = ctk.CTkFrame(main_frame)
        folder_frame.pack(fill="x", padx=20, pady=10)
        
        folder_label = ctk.CTkLabel(folder_frame, text="İndirme Klasörü:", font=ctk.CTkFont(size=14))
        folder_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        folder_select_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        folder_select_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Son seçilen klasörü yükle veya varsayılanı kullan
        default_folder = self.get_default_downloads_folder()
        saved_folder = self.load_last_folder()
        
        if saved_folder and os.path.exists(saved_folder):
            initial_folder = saved_folder
        else:
            initial_folder = default_folder
        
        self.folder_path = ctk.StringVar(value=initial_folder)
        
        self.folder_entry = ctk.CTkEntry(
            folder_select_frame,
            textvariable=self.folder_path,
            height=35,
            font=ctk.CTkFont(size=11),
            state="readonly"  # Manuel yazılamaz, sadece butonla seçilebilir
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.folder_button = ctk.CTkButton(
            folder_select_frame,
            text="Klasör Seç",
            command=self.select_folder,
            width=100,
            height=35
        )
        self.folder_button.pack(side="right")
        
        # İndirme butonu
        self.download_button = ctk.CTkButton(
            main_frame,
            text="İndirmeyi Başlat",
            command=self.start_download,
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#1f538d",
            hover_color="#14375e",
            state="disabled"  # Başlangıçta pasif
        )
        self.download_button.pack(pady=25, padx=20, fill="x")
        
        # Durum çubuğu
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Hazır",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.status_label.pack(pady=(5, 5))
        
        # İlerleme çubuğu
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 20))
        self.progress_bar.set(0)
        
        # Başlangıçta buton durumunu ve temizleme ikonunu kontrol et
        self.root.after(100, self.check_url_and_update_button)
        
        # Geliştirici bilgisi
        self.developer_label = ctk.CTkLabel(
            main_frame,
            text="Developed by UnderSpeed",
            font=ctk.CTkFont(size=11, underline=True),
            text_color="#4a9eff",
            cursor="hand2"
        )
        self.developer_label.pack(pady=(0, 10))
        self.developer_label.bind("<Button-1>", lambda e: self.show_feedback_window())
        
        # Hover efekti için
        def on_enter(e):
            if self.developer_label.cget("state") != "disabled":
                self.developer_label.configure(text_color="#6bb3ff")
        
        def on_leave(e):
            if self.developer_label.cget("state") != "disabled":
                self.developer_label.configure(text_color="#4a9eff")
        
        self.developer_label.bind("<Enter>", on_enter)
        self.developer_label.bind("<Leave>", on_leave)
        
    def check_ffmpeg(self):
        """FFmpeg'in kurulu olup olmadığını kontrol eder"""
        # Önce sistem PATH'inde kontrol et
        if shutil.which("ffmpeg") is not None:
            return True
        # Sonra proje klasöründe kontrol et
        local_ffmpeg = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
        return os.path.exists(local_ffmpeg)
    
    def get_ffmpeg_path(self):
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
    
    def install_ffmpeg(self):
        """FFmpeg'i otomatik olarak indirip kurar"""
        if self.installing_ffmpeg:
            return
        
        if platform.system() != "Windows":
            messagebox.showinfo("Bilgi", "Otomatik kurulum şu anda sadece Windows için desteklenmektedir.")
            return
        
        # Önceki başarısız kurulum denemelerinden kalan geçici dosyaları temizle
        temp_dir = os.path.join(os.path.dirname(__file__), "temp_ffmpeg")
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass  # Temizlenemezse devam et
        
        # Kullanıcıya onay al
        result = messagebox.askyesno(
            "FFmpeg Kurulumu",
            "FFmpeg indirilecek ve proje klasörüne kurulacak (~50 MB).\n\nDevam etmek istiyor musunuz?",
            icon="question"
        )
        
        if not result:
            return
        
        self.installing_ffmpeg = True
        if hasattr(self, 'install_ffmpeg_button'):
            self.install_ffmpeg_button.configure(state="disabled", text="Kuruluyor...")
        
        # İlerleme çubuğunu sıfırla
        self.update_progress(0)
        self.update_status("Başlatılıyor...", "blue")
        
        # İlerleme throttle değişkenini sıfırla
        if hasattr(self, '_last_progress_update'):
            self._last_progress_update = 0
        
        # Arka planda kurulum yap
        thread = threading.Thread(target=self._download_and_install_ffmpeg, daemon=True)
        thread.start()
    
    def _safe_update_status(self, message, color="gray"):
        """Thread-safe durum güncelleme"""
        def update():
            self.update_status(message, color)
        self.root.after_idle(update)
    
    def _safe_update_progress(self, value):
        """Thread-safe ilerleme güncelleme - throttle ile"""
        # Son güncellemeden bu yana yeterince zaman geçtiyse güncelle
        if not hasattr(self, '_last_progress_update'):
            self._last_progress_update = 0
        
        current_time = time.time()
        # En fazla 10 kez/saniye güncelle (100ms throttle)
        if current_time - self._last_progress_update >= 0.1:
            def update():
                self.update_progress(value)
            self.root.after_idle(update)
            self._last_progress_update = current_time
    
    def _safe_messagebox(self, title, message, type="info"):
        """Thread-safe messagebox"""
        def show_info():
            messagebox.showinfo(title, message)
        def show_error():
            messagebox.showerror(title, message)
        
        if type == "info":
            self.root.after_idle(show_info)
        elif type == "error":
            self.root.after_idle(show_error)
    
    def _download_and_install_ffmpeg(self):
        """FFmpeg'i indirip kurar (arka plan thread'inde çalışır)"""
        try:
            self._safe_update_status("FFmpeg indiriliyor...", "blue")
            self._safe_update_progress(0.05)
            
            # FFmpeg Windows essentials build URL'leri (alternatifler)
            ffmpeg_urls = [
                "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
                "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            ]
            
            # Geçici dosya yolu
            temp_dir = os.path.join(os.path.dirname(__file__), "temp_ffmpeg")
            zip_path = os.path.join(temp_dir, "ffmpeg.zip")
            
            # Geçici klasörü oluştur
            try:
                os.makedirs(temp_dir, exist_ok=True)
            except Exception as e:
                raise Exception(f"Geçici klasör oluşturulamadı: {str(e)}")
            
            # İndirme - alternatif URL'leri dene
            self._safe_update_status("FFmpeg indiriliyor... (Bu biraz zaman alabilir)", "blue")
            response = None
            last_error = None
            
            for url_idx, ffmpeg_url in enumerate(ffmpeg_urls):
                try:
                    self._safe_update_status(f"İndirme deneniyor... ({url_idx + 1}/{len(ffmpeg_urls)})", "blue")
                    response = requests.get(ffmpeg_url, stream=True, timeout=180, allow_redirects=True)
                    response.raise_for_status()
                    break  # Başarılı, döngüden çık
                except Exception as e:
                    last_error = e
                    if url_idx < len(ffmpeg_urls) - 1:
                        continue  # Sonraki URL'yi dene
                    else:
                        raise Exception(f"Tüm indirme kaynakları başarısız. Son hata: {str(e)}")
            
            if not response:
                raise Exception("İndirme başlatılamadı")
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            self._safe_update_progress(0.1)
            
            with open(zip_path, 'wb') as f:
                last_progress_update = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = 0.1 + (downloaded / total_size) * 0.6
                            # Sadece %1'lik değişikliklerde güncelle
                            if progress - last_progress_update >= 0.01 or progress >= 0.7:
                                self._safe_update_progress(min(progress, 0.7))
                                last_progress_update = progress
                        else:
                            # Boyut bilgisi yoksa sadece bir kez güncelle
                            if downloaded == len(chunk):
                                self._safe_update_progress(0.3)
            
            self._safe_update_status("FFmpeg çıkarılıyor...", "blue")
            self._safe_update_progress(0.7)
            
            # ZIP'i çıkar
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            except zipfile.BadZipFile:
                raise Exception("İndirilen dosya bozuk ZIP dosyası. Lütfen tekrar deneyin.")
            
            self._safe_update_progress(0.8)
            
            # ffmpeg.exe'yi bul ve kopyala
            extracted_dir = None
            ffmpeg_exe_path = None
            
            for root, dirs, files in os.walk(temp_dir):
                if 'ffmpeg.exe' in files:
                    extracted_dir = root
                    ffmpeg_exe_path = os.path.join(root, "ffmpeg.exe")
                    break
            
            if not ffmpeg_exe_path or not os.path.exists(ffmpeg_exe_path):
                # ZIP içeriğini listele (debug için)
                zip_contents = []
                try:
                    with zipfile.ZipFile(zip_path, 'r') as z:
                        zip_contents = z.namelist()[:10]  # İlk 10 dosya
                except:
                    pass
                raise Exception(f"ffmpeg.exe bulunamadı. ZIP içeriği: {zip_contents}")
            
            target_path = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
            
            # ffmpeg.exe'yi kopyala
            try:
                shutil.copy2(ffmpeg_exe_path, target_path)
            except Exception as e:
                raise Exception(f"ffmpeg.exe kopyalanamadı: {str(e)}")
            
            # Kopyalanan dosyanın varlığını kontrol et
            if not os.path.exists(target_path):
                raise Exception("ffmpeg.exe kopyalandı ancak hedef konumda bulunamadı")
            
            self._safe_update_progress(0.95)
            
            # Geçici dosyaları temizle
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                # Temizleme hatası kritik değil, sadece log
                print(f"Geçici dosyalar temizlenemedi: {e}")
            
            # FFmpeg durumunu güncelle
            self.has_ffmpeg = True
            self.ffmpeg_path = target_path
            
            self._safe_update_progress(1.0)
            self._safe_update_status("FFmpeg başarıyla kuruldu!", "green")
            
            # UI'ı güncelle
            self.root.after_idle(self._update_ffmpeg_ui)
            
            self._safe_messagebox("Başarılı", "FFmpeg başarıyla kuruldu!\n\nUygulamayı yeniden başlatmanız önerilir.", "info")
            
        except requests.exceptions.Timeout:
            error_msg = "İndirme zaman aşımına uğradı. Lütfen internet bağlantınızı kontrol edin ve tekrar deneyin."
            self._safe_update_status(error_msg, "red")
            self._safe_messagebox("Hata", f"FFmpeg indirilemedi:\n{error_msg}", "error")
        except requests.exceptions.RequestException as e:
            error_msg = f"İndirme hatası: {str(e)}"
            self._safe_update_status(error_msg, "red")
            self._safe_messagebox("Hata", f"FFmpeg indirilemedi:\n{error_msg}\n\nLütfen internet bağlantınızı kontrol edin.", "error")
        except Exception as e:
            import traceback
            error_msg = str(e)
            error_details = traceback.format_exc()
            print(f"FFmpeg kurulum hatası: {error_details}")  # Console'a yazdır
            self._safe_update_status(f"Kurulum hatası: {error_msg}", "red")
            self._safe_messagebox("Hata", f"FFmpeg kurulumu sırasında bir hata oluştu:\n{error_msg}\n\nDetaylar için konsolu kontrol edin.", "error")
        finally:
            self.installing_ffmpeg = False
            self._safe_update_progress(0)
            if hasattr(self, 'install_ffmpeg_button'):
                def reset_button():
                    self.install_ffmpeg_button.configure(state="normal", text="FFmpeg'i Otomatik Kur")
                self.root.after_idle(reset_button)
    
    def _update_ffmpeg_ui(self):
        """FFmpeg kurulduktan sonra UI'ı günceller"""
        # FFmpeg durumunu tekrar kontrol et
        self.has_ffmpeg = self.check_ffmpeg()
        self.ffmpeg_path = self.get_ffmpeg_path()
        
        # Durum label'ını güncelle
        if hasattr(self, 'ffmpeg_status_label'):
            if self.has_ffmpeg:
                self.ffmpeg_status_label.configure(
                    text="✓ FFmpeg bulundu - Tüm özellikler aktif",
                    text_color="green"
                )
            else:
                self.ffmpeg_status_label.configure(
                    text="⚠ FFmpeg bulunamadı - Bazı özellikler sınırlı olabilir",
                    text_color="orange"
                )
        
        # Kurulum butonunu gizle veya güncelle
        if hasattr(self, 'install_ffmpeg_button'):
            if self.has_ffmpeg:
                self.install_ffmpeg_button.pack_forget()
            else:
                self.install_ffmpeg_button.configure(state="normal", text="FFmpeg'i Otomatik Kur")
    
    def select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_path.get())
        if folder:
            self.folder_path.set(folder)
            # Seçilen klasörü kaydet
            self.save_last_folder(folder)
    
    def show_feedback_window(self):
        """Geliştirici geri bildirim penceresini gösterir"""
        # Modal pencere oluştur
        feedback_window = ctk.CTkToplevel(self.root)
        feedback_window.title("Geri Bildirim")
        
        # Pencere boyutu
        window_width = 400
        window_height = 330  # Yükseklik artırıldı
        
        feedback_window.geometry(f"{window_width}x{window_height}")
        feedback_window.resizable(False, False)  # Boyut değiştirilemez
        feedback_window.transient(self.root)  # Ana pencereye bağlı
        feedback_window.grab_set()  # Modal yap
        
        # Maximize'i engelle
        feedback_window.maxsize(window_width, window_height)
        feedback_window.minsize(window_width, window_height)
        
        # Ana pencerenin ortasını hesapla
        feedback_window.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        
        # Ana pencerenin tam ortasına yerleştir
        x = main_x + (main_width // 2) - (window_width // 2)
        y = main_y + (main_height // 2) - (window_height // 2)
        
        feedback_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Ana frame
        main_frame = ctk.CTkFrame(feedback_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ctk.CTkLabel(
            main_frame,
            text="YouT Video Mp3 Downloader",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # Versiyon bilgisi
        version_label = ctk.CTkLabel(
            main_frame,
            text=APP_VERSION,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        version_label.pack(pady=(0, 5))
        
        # Geliştirici bilgisi
        dev_label = ctk.CTkLabel(
            main_frame,
            text="Developed by UnderSpeed",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        dev_label.pack(pady=(0, 20))
        
        # Soru
        question_label = ctk.CTkLabel(
            main_frame,
            text="Bu uygulamayı beğendiniz mi?",
            font=ctk.CTkFont(size=14)
        )
        question_label.pack(pady=(0, 20))
        
        # Butonlar frame'i
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 10))
        
        # Like butonu
        def on_like():
            messagebox.showinfo("Teşekkürler!", "Beğeniniz için teşekkür ederiz! ❤️")
            feedback_window.destroy()
        
        like_button = ctk.CTkButton(
            buttons_frame,
            text="👍 Beğen",
            command=on_like,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#2d8659",
            hover_color="#1f5c3f"
        )
        like_button.pack(side="left", padx=10)
        
        # Dislike butonu
        def on_dislike():
            messagebox.showinfo("Geri Bildirim", "Görüşleriniz için teşekkürler! Geliştirmeler için çalışıyoruz. 💪")
            feedback_window.destroy()
        
        dislike_button = ctk.CTkButton(
            buttons_frame,
            text="👎 Beğenmedim",
            command=on_dislike,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="#8b4513",
            hover_color="#654321"
        )
        dislike_button.pack(side="left", padx=10)
        
        # Kapat butonu
        def on_close():
            feedback_window.destroy()
        
        close_button = ctk.CTkButton(
            main_frame,
            text="Kapat",
            command=on_close,
            width=100,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="gray",
            hover_color="darkgray"
        )
        close_button.pack(pady=(10, 0))
    
    def validate_url(self, url):
        """URL'nin geçerli bir YouTube video URL'si olup olmadığını kontrol eder"""
        if not url or not url.strip():
            return False
        
        url = url.strip()
        
        # YouTube domain kontrolü
        youtube_domains = ['youtube.com', 'youtu.be']
        has_youtube_domain = any(domain in url for domain in youtube_domains)
        
        if not has_youtube_domain:
            return False
        
        # Video ID pattern'lerini kontrol et
        
        # Pattern 1: youtube.com/watch?v=VIDEO_ID
        pattern1 = r'(?:youtube\.com/watch\?v=|youtube\.com/embed/|youtube\.com/v/)([a-zA-Z0-9_-]{11})'
        # Pattern 2: youtu.be/VIDEO_ID
        pattern2 = r'youtu\.be/([a-zA-Z0-9_-]{11})'
        # Pattern 3: youtube.com/watch?list=...&v=VIDEO_ID veya &v=VIDEO_ID
        pattern3 = r'[?&]v=([a-zA-Z0-9_-]{11})'
        
        # Herhangi bir pattern eşleşiyorsa geçerli
        if re.search(pattern1, url) or re.search(pattern2, url) or re.search(pattern3, url):
            return True
        
        # Eğer sadece domain varsa ama video ID yoksa geçersiz
        # Örnek: "http://www.youtube.com" geçersiz olmalı
        return False
    
    def debounced_check_url(self):
        """Debounce ile URL kontrolü yapar (kullanıcı yazmayı bitirdikten sonra)"""
        # Önceki timer'ı iptal et
        if self.url_check_timer:
            self.root.after_cancel(self.url_check_timer)
        
        # Yeni timer başlat (500ms sonra kontrol et)
        self.url_check_timer = self.root.after(500, self.check_url_and_update_button)
    
    def clear_url(self):
        """URL alanını temizler"""
        self.url_entry.delete(0, "end")
        self.url_entry.focus()
        self.check_url_and_update_button()
    
    def disable_inputs(self):
        """İndirme sırasında input'ları devre dışı bırakır"""
        self.url_entry.configure(state="disabled")
        self.video_radio.configure(state="disabled")
        self.audio_radio.configure(state="disabled")
        self.both_radio.configure(state="disabled")
        self.folder_button.configure(state="disabled")
        # Developer label'ı tıklanamaz yap
        self.developer_label.unbind("<Button-1>")
        self.developer_label.unbind("<Enter>")
        self.developer_label.unbind("<Leave>")
        self.developer_label.configure(cursor="arrow", text_color="gray")
    
    def enable_inputs(self):
        """İndirme bittiğinde input'ları tekrar aktif eder"""
        self.url_entry.configure(state="normal")
        self.video_radio.configure(state="normal")
        self.audio_radio.configure(state="normal")
        self.both_radio.configure(state="normal")
        self.folder_button.configure(state="normal")
        # Developer label'ı tekrar tıklanabilir yap
        self.developer_label.bind("<Button-1>", lambda e: self.show_feedback_window())
        self.developer_label.configure(cursor="hand2", text_color="#4a9eff")
        # Hover efektlerini tekrar ekle
        def on_enter(e):
            self.developer_label.configure(text_color="#6bb3ff")
        def on_leave(e):
            self.developer_label.configure(text_color="#4a9eff")
        self.developer_label.bind("<Enter>", on_enter)
        self.developer_label.bind("<Leave>", on_leave)
    
    def check_url_and_update_button(self):
        """URL'yi kontrol eder ve buton durumunu günceller"""
        url = self.url_entry.get().strip()
        is_valid = self.validate_url(url)
        
        # Temizleme butonunu göster/gizle
        if url:
            self.clear_url_button.pack(side="right")
        else:
            self.clear_url_button.pack_forget()
        
        if is_valid:
            self.download_button.configure(state="normal")
        else:
            self.download_button.configure(state="disabled")
    
    def update_status(self, message, color="gray"):
        """Durum mesajını günceller"""
        try:
            self.status_label.configure(text=message, text_color=color)
        except:
            pass  # Widget henüz oluşturulmamış olabilir
    
    def update_progress(self, value):
        """İlerleme çubuğunu günceller"""
        try:
            # Değeri 0-1 aralığına sınırla
            value = max(0.0, min(1.0, float(value)))
            self.progress_bar.set(value)
        except:
            pass  # Widget henüz oluşturulmamış olabilir
    
    def download_hook(self, d):
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
                        self.update_progress(mapped_progress)
                        speed = d.get('speed', 0)
                        if speed:
                            speed_mb = speed / (1024 * 1024)
                            self.update_status(f"Video indiriliyor... {speed_mb:.2f} MB/s", "yellow")
                    else:
                        # Ses indiriliyor: 0.5-1.0 aralığı
                        mapped_progress = 0.5 + (progress * 0.5)
                        self.update_progress(mapped_progress)
                        speed = d.get('speed', 0)
                        if speed:
                            speed_mb = speed / (1024 * 1024)
                            self.update_status(f"Ses indiriliyor... {speed_mb:.2f} MB/s", "yellow")
                else:
                    # Normal durum (video veya audio tek başına)
                    self.update_progress(progress)
                    speed = d.get('speed', 0)
                    if speed:
                        speed_mb = speed / (1024 * 1024)
                        self.update_status(f"İndiriliyor... {speed_mb:.2f} MB/s", "yellow")
        elif d['status'] == 'finished':
            if self.current_download_type == "both":
                if not self.video_downloaded:
                    # Video tamamlandı
                    self.update_progress(0.5)
                    self.update_status("Video tamamlandı, ses indiriliyor...", "yellow")
                    self.video_downloaded = True
                else:
                    # Her ikisi de tamamlandı
                    self.update_progress(1.0)
                    self.update_status("İndirme tamamlandı!", "green")
            else:
                self.update_progress(1.0)
                self.update_status("İndirme tamamlandı!", "green")
    
    def get_ffmpeg_location(self):
        """yt-dlp için FFmpeg konumunu döndürür"""
        if self.ffmpeg_path and os.path.exists(self.ffmpeg_path):
            # Sadece dizin yolunu döndür (dosya adı değil)
            return os.path.dirname(self.ffmpeg_path)
        return None
    
    def download_video(self, url, output_path, download_type):
        """Video/ses indirme fonksiyonu"""
        # FFmpeg durumunu tekrar kontrol et (kurulum sonrası güncellenmiş olabilir)
        if not self.has_ffmpeg:
            self.has_ffmpeg = self.check_ffmpeg()
            self.ffmpeg_path = self.get_ffmpeg_path()
        
        # İndirme tipini ve durumunu ayarla
        self.current_download_type = download_type
        self.video_downloaded = False
        
        try:
            # Ortak ayarlar
            base_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.download_hook],
                'noplaylist': True,
                'quiet': False,  # İlerleme bilgisini göster
                'no_warnings': False,  # Uyarıları göster ama daha temiz
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],  # JavaScript runtime uyarısını azaltır
                    }
                },
            }
            
            # FFmpeg konumunu ayarla
            ffmpeg_location = self.get_ffmpeg_location()
            if ffmpeg_location:
                base_opts['ffmpeg_location'] = ffmpeg_location
            
            if download_type == "video":
                if self.has_ffmpeg:
                    # FFmpeg varsa en iyi kaliteyi birleştir
                    ydl_opts = {
                        **base_opts,
                        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    }
                else:
                    # FFmpeg yoksa tek format kullan (birleştirme gerektirmeyen)
                    ydl_opts = {
                        **base_opts,
                        'format': 'best[ext=mp4]/best',
                    }
            elif download_type == "audio":
                if self.has_ffmpeg:
                    # FFmpeg varsa MP3'e dönüştür
                    ydl_opts = {
                        **base_opts,
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    }
                else:
                    # FFmpeg yoksa mevcut ses formatını indir
                    ydl_opts = {
                        **base_opts,
                        'format': 'bestaudio/best',
                    }
            else:  # both
                if not self.has_ffmpeg:
                    # FFmpeg yoksa uyarı ver ve sadece video indir
                    self.update_status("FFmpeg bulunamadı! Sadece video indiriliyor...", "orange")
                
                # Önce video indir
                self.video_downloaded = False  # Video indirme başlıyor
                self.update_progress(0)
                self.update_status("Video indiriliyor...", "yellow")
                
                if self.has_ffmpeg:
                    ydl_opts_video = {
                        **base_opts,
                        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    }
                else:
                    ydl_opts_video = {
                        **base_opts,
                        'format': 'best[ext=mp4]/best',
                    }
                
                with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                    ydl.download([url])
                
                # Video tamamlandı, ses indirmeye geç
                self.video_downloaded = True
                self.update_progress(0.5)
                self.update_status("Ses indiriliyor...", "yellow")
                
                # Sonra ses indir (sadece FFmpeg varsa MP3'e dönüştür)
                if self.has_ffmpeg:
                    ydl_opts_audio = {
                        **base_opts,
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join(output_path, '%(title)s_audio.%(ext)s'),
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    }
                else:
                    ydl_opts_audio = {
                        **base_opts,
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join(output_path, '%(title)s_audio.%(ext)s'),
                    }
                ydl_opts = ydl_opts_audio
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.downloading = False
            self.current_download_type = None
            self.video_downloaded = False
            self.download_button.configure(text="İndirmeyi Başlat")
            # Input'ları tekrar aktif et
            self.enable_inputs()
            messagebox.showinfo("Başarılı", "İndirme tamamlandı!")
            self.update_status("Hazır", "gray")
            self.update_progress(0)
            # URL'yi kontrol edip buton durumunu güncelle
            self.check_url_and_update_button()
            
        except Exception as e:
            self.downloading = False
            self.current_download_type = None
            self.video_downloaded = False
            self.download_button.configure(text="İndirmeyi Başlat")
            # Input'ları tekrar aktif et
            self.enable_inputs()
            error_msg = str(e)
            self.update_status(f"Hata: {error_msg[:50]}...", "red")
            messagebox.showerror("Hata", f"İndirme sırasında bir hata oluştu:\n{error_msg}")
            self.update_progress(0)
            # URL'yi kontrol edip buton durumunu güncelle
            self.check_url_and_update_button()
    
    def start_download(self):
        """İndirmeyi başlatır"""
        if self.downloading:
            return
        
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Uyarı", "Lütfen bir YouTube URL'si girin!")
            self.url_entry.focus()
            return
        
        if not self.validate_url(url):
            messagebox.showwarning("Uyarı", "Geçerli bir YouTube URL'si girin!")
            self.url_entry.focus()
            return
        
        output_path = self.folder_path.get()
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except Exception as e:
                messagebox.showerror("Hata", f"Klasör oluşturulamadı:\n{e}")
                return
        
        download_type = self.download_type.get()
        
        self.downloading = True
        self.download_button.configure(state="disabled", text="İndiriliyor...")
        self.update_status("Başlatılıyor...", "yellow")
        self.update_progress(0)
        
        # Input'ları devre dışı bırak
        self.disable_inputs()
        
        # İndirmeyi ayrı thread'de başlat
        thread = threading.Thread(
            target=self.download_video,
            args=(url, output_path, download_type),
            daemon=True
        )
        thread.start()

def main():
    root = ctk.CTk()
    app = YouTubeDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()

