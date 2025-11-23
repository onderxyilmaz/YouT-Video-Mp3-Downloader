"""
Ayarlar penceresi
"""
import customtkinter as ctk
from tkinter import filedialog
from config import Config, VIDEO_QUALITY_OPTIONS, AUDIO_QUALITY_OPTIONS, APP_NAME, APP_VERSION


class SettingsWindow:
    """Ayarlar penceresi sınıfı"""

    def __init__(self, parent, config):
        """
        Args:
            parent: Ana pencere
            config: Config instance
        """
        self.parent = parent
        self.config = config
        self.window = None

    def show(self):
        """Ayarlar penceresini gösterir"""
        if self.window is not None and self.window.winfo_exists():
            self.window.focus()
            return

        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Ayarlar")

        # Pencere boyutu
        window_width = 500
        window_height = 620

        self.window.geometry(f"{window_width}x{window_height}")
        # Kullanıcı pencere boyutunu değiştiremesin
        self.window.resizable(False, False)
        self.window.transient(self.parent)
        self.window.grab_set()

        # Ana pencerenin ortasına yerleştir
        self.window.update_idletasks()
        main_x = self.parent.winfo_x()
        main_y = self.parent.winfo_y()
        main_width = self.parent.winfo_width()
        main_height = self.parent.winfo_height()

        x = main_x + (main_width // 2) - (window_width // 2)
        y = main_y + (main_height // 2) - (window_height // 2)

        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Ana frame
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Başlık
        title_label = ctk.CTkLabel(
            main_frame,
            text="Ayarlar",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(10, 20))

        # İçerik frame'i (scroll olmadan)
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        # Anasayfadaki gibi içeriğe biraz iç padding ver
        content_frame.pack(fill="both", expand=True, pady=(0, 10), padx=10)

        # İndirme klasörü
        self._create_folder_setting(content_frame)

        # Video kalitesi
        self._create_video_quality_setting(content_frame)

        # Ses kalitesi
        self._create_audio_quality_setting(content_frame)

        # Varsayılan indirme tipi
        self._create_download_type_setting(content_frame)

        # Retry ayarları
        self._create_retry_settings(content_frame)

        # Butonlar
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))

        save_button = ctk.CTkButton(
            buttons_frame,
            text="Kaydet",
            command=self.save_settings,
            width=120,
            height=40,
            fg_color="#2d8659",
            hover_color="#1f5c3f"
        )
        save_button.pack(side="right", padx=5, pady=(0, 10))

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="İptal",
            command=self.window.destroy,
            width=120,
            height=40,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_button.pack(side="right", padx=5, pady=(0, 10))

    def _create_folder_setting(self, parent):
        """İndirme klasörü ayarı"""
        folder_frame = ctk.CTkFrame(parent, fg_color="transparent")
        folder_frame.pack(fill="x", pady=10)

        label = ctk.CTkLabel(
            folder_frame,
            text="Varsayılan İndirme Klasörü:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        label.pack(anchor="w", pady=(0, 5))

        input_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        input_frame.pack(fill="x")

        current_folder = self.config.get_last_download_folder() or "Ayarlanmadı"
        self.folder_var = ctk.StringVar(value=current_folder)

        self.folder_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.folder_var,
            state="readonly"
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        browse_button = ctk.CTkButton(
            input_frame,
            text="Gözat",
            command=self.browse_folder,
            width=80
        )
        browse_button.pack(side="right")

    def _create_video_quality_setting(self, parent):
        """Video kalitesi ayarı"""
        quality_frame = ctk.CTkFrame(parent, fg_color="transparent")
        quality_frame.pack(fill="x", pady=10)

        label = ctk.CTkLabel(
            quality_frame,
            text="Varsayılan Video Kalitesi:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        label.pack(anchor="w", pady=(0, 5))

        current_quality = self.config.get_video_quality()
        self.video_quality_var = ctk.StringVar(value=current_quality)

        self.video_quality_menu = ctk.CTkOptionMenu(
            quality_frame,
            variable=self.video_quality_var,
            values=list(VIDEO_QUALITY_OPTIONS.keys())
        )
        self.video_quality_menu.pack(fill="x")

    def _create_audio_quality_setting(self, parent):
        """Ses kalitesi ayarı"""
        quality_frame = ctk.CTkFrame(parent, fg_color="transparent")
        quality_frame.pack(fill="x", pady=10)

        label = ctk.CTkLabel(
            quality_frame,
            text="Varsayılan Ses Kalitesi (MP3):",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        label.pack(anchor="w", pady=(0, 5))

        current_quality = self.config.get_audio_quality()
        self.audio_quality_var = ctk.StringVar(value=current_quality)

        self.audio_quality_menu = ctk.CTkOptionMenu(
            quality_frame,
            variable=self.audio_quality_var,
            values=list(AUDIO_QUALITY_OPTIONS.keys())
        )
        self.audio_quality_menu.pack(fill="x")

    def _create_download_type_setting(self, parent):
        """Varsayılan indirme tipi ayarı"""
        type_frame = ctk.CTkFrame(parent, fg_color="transparent")
        type_frame.pack(fill="x", pady=10)

        label = ctk.CTkLabel(
            type_frame,
            text="Varsayılan İndirme Tipi:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        label.pack(anchor="w", pady=(0, 5))

        current_type = self.config.get_default_download_type()
        self.download_type_var = ctk.StringVar(value=current_type)

        type_options = {
            "Video (MP4)": "video",
            "Sadece Ses (MP3)": "audio",
            "Video ve Ses (Her İkisi)": "both"
        }

        # Değeri display text'e çevir
        display_text = [k for k, v in type_options.items() if v == current_type][0]
        self.download_type_var.set(display_text)

        self.download_type_menu = ctk.CTkOptionMenu(
            type_frame,
            variable=self.download_type_var,
            values=list(type_options.keys())
        )
        self.download_type_menu.pack(fill="x")

        self.type_options_map = type_options

    def _create_retry_settings(self, parent):
        """Retry ayarları"""
        retry_frame = ctk.CTkFrame(parent, fg_color="transparent")
        retry_frame.pack(fill="x", pady=10)

        label = ctk.CTkLabel(
            retry_frame,
            text="Otomatik Yeniden Deneme:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        label.pack(anchor="w", pady=(0, 5))

        # Auto retry switch
        self.auto_retry_var = ctk.BooleanVar(value=self.config.get_auto_retry())

        self.auto_retry_switch = ctk.CTkSwitch(
            retry_frame,
            text="Hata durumunda otomatik yeniden dene",
            variable=self.auto_retry_var
        )
        self.auto_retry_switch.pack(anchor="w", pady=5)

        # Max retry count
        retry_count_frame = ctk.CTkFrame(retry_frame, fg_color="transparent")
        retry_count_frame.pack(fill="x", pady=(10, 0))

        retry_count_label = ctk.CTkLabel(
            retry_count_frame,
            text="Maksimum Deneme Sayısı:",
            font=ctk.CTkFont(size=12)
        )
        retry_count_label.pack(side="left")

        self.retry_count_var = ctk.IntVar(value=self.config.get_max_retries())

        self.retry_count_slider = ctk.CTkSlider(
            retry_count_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            variable=self.retry_count_var
        )
        self.retry_count_slider.pack(side="left", fill="x", expand=True, padx=10)

        self.retry_count_value_label = ctk.CTkLabel(
            retry_count_frame,
            text=str(self.retry_count_var.get()),
            width=30
        )
        self.retry_count_value_label.pack(side="right")

        # Slider değiştiğinde label'ı güncelle
        self.retry_count_var.trace_add("write", lambda *args: self.retry_count_value_label.configure(
            text=str(int(self.retry_count_var.get()))
        ))

    def browse_folder(self):
        """Klasör seçim dialogunu gösterir"""
        current_folder = self.folder_var.get()
        if current_folder == "Ayarlanmadı":
            current_folder = ""

        folder = filedialog.askdirectory(initialdir=current_folder)
        if folder:
            self.folder_var.set(folder)

    def save_settings(self):
        """Ayarları kaydeder"""
        # Klasör
        folder = self.folder_var.get()
        if folder and folder != "Ayarlanmadı":
            self.config.set_last_download_folder(folder)

        # Video kalitesi
        self.config.set_video_quality(self.video_quality_var.get())

        # Ses kalitesi
        self.config.set_audio_quality(self.audio_quality_var.get())

        # İndirme tipi
        display_text = self.download_type_var.get()
        download_type = self.type_options_map[display_text]
        self.config.set_default_download_type(download_type)

        # Retry ayarları
        self.config.set_auto_retry(self.auto_retry_var.get())
        self.config.set_max_retries(int(self.retry_count_var.get()))

        # Pencereyi kapat
        from tkinter import messagebox
        messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")
        self.window.destroy()
