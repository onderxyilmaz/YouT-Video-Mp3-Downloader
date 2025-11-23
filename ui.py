"""
Kullanıcı arayüzü modülü
"""
import customtkinter as ctk
import os
import threading
import platform
from tkinter import filedialog, messagebox
from config import APP_VERSION, APP_NAME, DEVELOPER_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, URL_CHECK_DEBOUNCE, Config
from utils import validate_url, get_default_downloads_folder, check_ffmpeg, get_ffmpeg_path
from downloader import DownloadManager, FFmpegInstaller
from settings_window import SettingsWindow
from history_window import HistoryWindow
from database import DownloadHistory


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class YouTubeDownloaderUI:
    """YouTube Downloader arayüzü"""

    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)

        # Pencere ayarları
        self._setup_window()

        # Durum değişkenleri
        self.downloading = False
        self.installing_ffmpeg = False
        self.has_ffmpeg = check_ffmpeg()
        self.ffmpeg_path = get_ffmpeg_path()

        # Config
        self.config = Config()

        # Database
        self.db = DownloadHistory()

        # URL kontrolü için debounce timer
        self.url_check_timer = None

        # Widget'ları oluştur
        self.create_widgets()

    def _setup_window(self):
        """Pencere boyutu ve konumunu ayarlar"""
        # Masaüstünün ortasını hesapla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (WINDOW_WIDTH // 2)
        y = (screen_height // 2) - (WINDOW_HEIGHT // 2)

        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.maxsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.root.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)

    def create_widgets(self):
        """Tüm widget'ları oluşturur"""
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        # Başlık
        self._create_header(main_frame)

        # FFmpeg durumu
        self._create_ffmpeg_section(main_frame)

        # URL girişi
        self._create_url_section(main_frame)

        # İndirme tipi
        self._create_download_type_section(main_frame)

        # Klasör seçimi
        self._create_folder_section(main_frame)

        # İndirme butonu
        self._create_download_button(main_frame)

        # Durum ve ilerleme
        self._create_progress_section(main_frame)

        # Footer
        self._create_footer(main_frame)

        # İlk kontrol
        self.root.after(100, self.check_url_and_update_button)

    def _create_header(self, parent):
        """Başlık bölümünü oluşturur"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))

        # Üst satır: Başlık (ortada) ve sağda butonlar
        top_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 0))

        # Başlık ortada
        title_label = ctk.CTkLabel(
            top_row,
            text=APP_NAME,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="top", pady=(8, 2))

        # Alt satır: Versiyon yazısı başlığın hemen altında ortalı
        version_label = ctk.CTkLabel(
            header_frame,
            text=APP_VERSION,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        version_label.pack(pady=(0, 10))

        # Sağ üst köşe: Geçmiş ve Ayarlar butonları
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        # Butonları versiyon yazısından biraz daha aşağıya al
        buttons_frame.place(relx=1.0, rely=0.0, x=-30, y=45, anchor="ne")

        history_button = ctk.CTkButton(
            buttons_frame,
            text="📋 Geçmiş",
            command=self.show_history,
            width=90,
            height=32,
            font=ctk.CTkFont(size=12)
        )
        history_button.pack(side="left", padx=5)

        settings_button = ctk.CTkButton(
            buttons_frame,
            text="⚙ Ayarlar",
            command=self.show_settings,
            width=90,
            height=32,
            font=ctk.CTkFont(size=12)
        )
        settings_button.pack(side="left")

    def _create_ffmpeg_section(self, parent):
        """FFmpeg durum ve kurulum bölümünü oluşturur"""
        self.ffmpeg_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.ffmpeg_frame.pack(pady=(5, 20))

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

    def _create_url_section(self, parent):
        """URL giriş bölümünü oluşturur"""
        url_frame = ctk.CTkFrame(parent)
        url_frame.pack(fill="x", padx=20, pady=10)

        url_label = ctk.CTkLabel(url_frame, text="YouTube URL:", font=ctk.CTkFont(size=14))
        url_label.pack(anchor="w", padx=10, pady=(10, 5))

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
        self.url_entry.bind("<KeyRelease>", lambda e: self.debounced_check_url())
        self.url_entry.bind("<FocusOut>", lambda e: self.check_url_and_update_button())

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
        self.clear_url_button.pack_forget()

    def _create_download_type_section(self, parent):
        """İndirme tipi seçim bölümünü oluşturur"""
        download_type_frame = ctk.CTkFrame(parent)
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

    def _create_folder_section(self, parent):
        """Klasör seçim bölümünü oluşturur"""
        folder_frame = ctk.CTkFrame(parent)
        folder_frame.pack(fill="x", padx=20, pady=10)

        folder_label = ctk.CTkLabel(folder_frame, text="İndirme Klasörü:", font=ctk.CTkFont(size=14))
        folder_label.pack(anchor="w", padx=10, pady=(10, 5))

        folder_select_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        folder_select_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Kaydedilmiş klasörü yükle veya varsayılanı kullan
        default_folder = get_default_downloads_folder()
        saved_folder = self.config.get_last_download_folder()
        initial_folder = saved_folder if saved_folder and os.path.exists(saved_folder) else default_folder

        self.folder_path = ctk.StringVar(value=initial_folder)

        self.folder_entry = ctk.CTkEntry(
            folder_select_frame,
            textvariable=self.folder_path,
            height=35,
            font=ctk.CTkFont(size=11),
            state="readonly"
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

    def _create_download_button(self, parent):
        """İndirme butonunu oluşturur"""
        self.download_button = ctk.CTkButton(
            parent,
            text="İndirmeyi Başlat",
            command=self.start_download,
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#1f538d",
            hover_color="#14375e",
            state="disabled"
        )
        self.download_button.pack(pady=25, padx=20, fill="x")

    def _create_progress_section(self, parent):
        """Durum ve ilerleme bölümünü oluşturur"""
        self.status_label = ctk.CTkLabel(
            parent,
            text="Hazır",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.status_label.pack(pady=(5, 5))

        self.progress_bar = ctk.CTkProgressBar(parent)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 20))
        self.progress_bar.set(0)

    def _create_footer(self, parent):
        """Footer bölümünü oluşturur"""
        self.developer_label = ctk.CTkLabel(
            parent,
            text=f"Developed by {DEVELOPER_NAME}",
            font=ctk.CTkFont(size=11, underline=True),
            text_color="#4a9eff",
            cursor="hand2"
        )
        self.developer_label.pack(pady=(0, 10))
        self.developer_label.bind("<Button-1>", lambda e: self.show_feedback_window())

        def on_enter(e):
            if self.developer_label.cget("state") != "disabled":
                self.developer_label.configure(text_color="#6bb3ff")

        def on_leave(e):
            if self.developer_label.cget("state") != "disabled":
                self.developer_label.configure(text_color="#4a9eff")

        self.developer_label.bind("<Enter>", on_enter)
        self.developer_label.bind("<Leave>", on_leave)

    def select_folder(self):
        """Klasör seçim dialogunu gösterir"""
        folder = filedialog.askdirectory(initialdir=self.folder_path.get())
        if folder:
            self.folder_path.set(folder)
            self.config.set_last_download_folder(folder)

    def clear_url(self):
        """URL alanını temizler"""
        self.url_entry.delete(0, "end")
        self.url_entry.focus()
        self.check_url_and_update_button()

    def debounced_check_url(self):
        """Debounce ile URL kontrolü"""
        if self.url_check_timer:
            self.root.after_cancel(self.url_check_timer)
        self.url_check_timer = self.root.after(URL_CHECK_DEBOUNCE, self.check_url_and_update_button)

    def check_url_and_update_button(self):
        """URL'yi kontrol eder ve buton durumunu günceller"""
        url = self.url_entry.get().strip()
        is_valid = validate_url(url)

        # Temizleme butonunu göster/gizle
        if url:
            self.clear_url_button.pack(side="right")
        else:
            self.clear_url_button.pack_forget()

        # İndirme butonunu aktif/pasif yap
        if is_valid:
            self.download_button.configure(state="normal")
        else:
            self.download_button.configure(state="disabled")

    def update_status(self, message, color="gray"):
        """Durum mesajını günceller"""
        try:
            self.status_label.configure(text=message, text_color=color)
        except:
            pass

    def update_progress(self, value):
        """İlerleme çubuğunu günceller"""
        try:
            value = max(0.0, min(1.0, float(value)))
            self.progress_bar.set(value)
        except:
            pass

    def disable_inputs(self):
        """İndirme sırasında input'ları devre dışı bırakır"""
        self.url_entry.configure(state="disabled")
        self.video_radio.configure(state="disabled")
        self.audio_radio.configure(state="disabled")
        self.both_radio.configure(state="disabled")
        self.folder_button.configure(state="disabled")
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
        self.developer_label.bind("<Button-1>", lambda e: self.show_feedback_window())
        self.developer_label.configure(cursor="hand2", text_color="#4a9eff")

        def on_enter(e):
            self.developer_label.configure(text_color="#6bb3ff")

        def on_leave(e):
            self.developer_label.configure(text_color="#4a9eff")

        self.developer_label.bind("<Enter>", on_enter)
        self.developer_label.bind("<Leave>", on_leave)

    def start_download(self):
        """İndirmeyi başlatır"""
        if self.downloading:
            return

        url = self.url_entry.get().strip()

        if not url:
            messagebox.showwarning("Uyarı", "Lütfen bir YouTube URL'si girin!")
            self.url_entry.focus()
            return

        if not validate_url(url):
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
        self.disable_inputs()

        # İndirmeyi ayrı thread'de başlat
        thread = threading.Thread(
            target=self._download_thread,
            args=(url, output_path, download_type),
            daemon=True
        )
        thread.start()

    def _download_thread(self, url, output_path, download_type):
        """İndirme thread'i"""
        video_title = None
        file_path = None
        file_size = None

        try:
            # Kalite ayarlarını al
            video_quality = self.config.get_video_quality()
            audio_quality = self.config.get_audio_quality()

            # Progress ve status callback'leri ile manager oluştur
            max_retries = self.config.get_max_retries()
            auto_retry = self.config.get_auto_retry()

            manager = DownloadManager(
                progress_callback=lambda v: self.root.after_idle(lambda: self.update_progress(v)),
                status_callback=lambda m, c: self.root.after_idle(lambda: self.update_status(m, c)),
                max_retries=max_retries
            )

            # Video bilgilerini al
            try:
                import yt_dlp
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_title = info.get('title', 'Başlık alınamadı')
            except:
                video_title = "Başlık alınamadı"

            # Kalite ayarlarını downloader'a geç
            manager.download(url, output_path, download_type, auto_retry=auto_retry,
                           video_quality=video_quality, audio_quality=audio_quality)

            # İndirilen dosya bilgilerini al
            try:
                # En son oluşturulan dosyayı bul
                files = [os.path.join(output_path, f) for f in os.listdir(output_path)]
                files = [f for f in files if os.path.isfile(f)]
                if files:
                    file_path = max(files, key=os.path.getctime)
                    file_size = os.path.getsize(file_path)
            except:
                pass

            # Veritabanına kaydet
            quality = self.config.get_video_quality() if download_type == "video" else self.config.get_audio_quality()
            self.db.add_download(
                url=url,
                title=video_title,
                download_type=download_type,
                quality=quality,
                file_path=file_path,
                file_size=file_size,
                status='başarılı'
            )

            def on_success():
                messagebox.showinfo("Başarılı", "İndirme tamamlandı!")
                self.update_status("Hazır", "gray")
                self.update_progress(0)

            self.root.after_idle(on_success)

        except Exception as e:
            error_msg = str(e)

            # Hatalı indirmeyi veritabanına kaydet
            self.db.add_download(
                url=url,
                title=video_title,
                download_type=download_type,
                quality=self.config.get_video_quality() if download_type == "video" else self.config.get_audio_quality(),
                status='başarısız',
                error_message=error_msg
            )

            def on_error():
                self.update_status(f"Hata: {error_msg[:50]}...", "red")
                messagebox.showerror("Hata", f"İndirme sırasında bir hata oluştu:\n{error_msg}")
                self.update_progress(0)

            self.root.after_idle(on_error)

        finally:
            def cleanup():
                self.downloading = False
                self.download_button.configure(text="İndirmeyi Başlat")
                self.enable_inputs()
                self.check_url_and_update_button()

            self.root.after_idle(cleanup)

    def install_ffmpeg(self):
        """FFmpeg kurulumunu başlatır"""
        if self.installing_ffmpeg:
            return

        if platform.system() != "Windows":
            messagebox.showinfo("Bilgi", "Otomatik kurulum şu anda sadece Windows için desteklenmektedir.")
            return

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

        self.update_progress(0)
        self.update_status("Başlatılıyor...", "blue")

        thread = threading.Thread(target=self._install_ffmpeg_thread, daemon=True)
        thread.start()

    def _install_ffmpeg_thread(self):
        """FFmpeg kurulum thread'i"""
        try:
            installer = FFmpegInstaller(
                progress_callback=lambda v: self.root.after_idle(lambda: self.update_progress(v)),
                status_callback=lambda m, c: self.root.after_idle(lambda: self.update_status(m, c))
            )

            installer.install()

            # FFmpeg durumunu güncelle
            self.has_ffmpeg = check_ffmpeg()
            self.ffmpeg_path = get_ffmpeg_path()

            def on_success():
                self._update_ffmpeg_ui()
                messagebox.showinfo("Başarılı", "FFmpeg başarıyla kuruldu!\n\nUygulamayı yeniden başlatmanız önerilir.")

            self.root.after_idle(on_success)

        except Exception as e:
            error_msg = str(e)

            def on_error():
                self.update_status(f"Kurulum hatası: {error_msg}", "red")
                messagebox.showerror("Hata", f"FFmpeg kurulumu sırasında bir hata oluştu:\n{error_msg}")

            self.root.after_idle(on_error)

        finally:
            def cleanup():
                self.installing_ffmpeg = False
                self.update_progress(0)
                if hasattr(self, 'install_ffmpeg_button'):
                    self.install_ffmpeg_button.configure(state="normal", text="FFmpeg'i Otomatik Kur")

            self.root.after_idle(cleanup)

    def _update_ffmpeg_ui(self):
        """FFmpeg kurulduktan sonra UI'ı günceller"""
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

        if hasattr(self, 'install_ffmpeg_button'):
            if self.has_ffmpeg:
                self.install_ffmpeg_button.pack_forget()
            else:
                self.install_ffmpeg_button.configure(state="normal", text="FFmpeg'i Otomatik Kur")

    def show_feedback_window(self):
        """Geri bildirim penceresini gösterir"""
        feedback_window = ctk.CTkToplevel(self.root)
        feedback_window.title("Geri Bildirim")

        window_width = 400
        window_height = 330

        feedback_window.geometry(f"{window_width}x{window_height}")
        feedback_window.resizable(False, False)
        feedback_window.transient(self.root)
        feedback_window.grab_set()
        feedback_window.maxsize(window_width, window_height)
        feedback_window.minsize(window_width, window_height)

        # Ana pencerenin ortasına yerleştir
        feedback_window.update_idletasks()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()

        x = main_x + (main_width // 2) - (window_width // 2)
        y = main_y + (main_height // 2) - (window_height // 2)

        feedback_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        main_frame = ctk.CTkFrame(feedback_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Başlık
        title_label = ctk.CTkLabel(
            main_frame,
            text=APP_NAME,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 5))

        version_label = ctk.CTkLabel(
            main_frame,
            text=APP_VERSION,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        version_label.pack(pady=(0, 5))

        dev_label = ctk.CTkLabel(
            main_frame,
            text=f"Developed by {DEVELOPER_NAME}",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        dev_label.pack(pady=(0, 20))

        question_label = ctk.CTkLabel(
            main_frame,
            text="Bu uygulamayı beğendiniz mi?",
            font=ctk.CTkFont(size=14)
        )
        question_label.pack(pady=(0, 20))

        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 10))

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

        close_button = ctk.CTkButton(
            main_frame,
            text="Kapat",
            command=feedback_window.destroy,
            width=100,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="gray",
            hover_color="darkgray"
        )
        close_button.pack(pady=(10, 0))

    def show_settings(self):
        """Ayarlar penceresini gösterir"""
        settings = SettingsWindow(self.root, self.config)
        settings.show()

    def show_history(self):
        """İndirme geçmişi penceresini gösterir"""
        history = HistoryWindow(self.root)
        history.show()
