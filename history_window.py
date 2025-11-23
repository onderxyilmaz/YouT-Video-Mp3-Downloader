"""
İndirme geçmişi penceresi
"""
import customtkinter as ctk
from database import DownloadHistory
from datetime import datetime
import os


class HistoryWindow:
    """İndirme geçmişi penceresi sınıfı"""

    def __init__(self, parent):
        """
        Args:
            parent: Ana pencere
        """
        self.parent = parent
        self.window = None
        self.db = DownloadHistory()

    def show(self):
        """İndirme geçmişi penceresini gösterir"""
        if self.window is not None and self.window.winfo_exists():
            self.window.focus()
            return

        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("İndirme Geçmişi")

        # Pencere boyutu
        window_width = 800
        window_height = 600

        self.window.geometry(f"{window_width}x{window_height}")
        self.window.resizable(True, True)
        self.window.transient(self.parent)

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
        # Pencere kenarlarından içeriye genel padding
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Başlık ve istatistikler
        self._create_header(main_frame)

        # Filtre ve arama
        self._create_filter_section(main_frame)

        # Geçmiş listesi
        self._create_history_list(main_frame)

        # Butonlar
        self._create_buttons(main_frame)

        # Geçmişi yükle
        self.load_history()

    def _create_header(self, parent):
        """Başlık ve istatistikler"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        # İçerik ile pencere kenarı arasında yatay padding
        header_frame.pack(fill="x", pady=(0, 15), padx=10)

        title_label = ctk.CTkLabel(
            header_frame,
            text="İndirme Geçmişi",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left")

        # İstatistikler
        stats = self.db.get_statistics()

        stats_text = f"Toplam: {stats['total_downloads']} | Başarılı: {stats['successful']} | Başarısız: {stats['failed']}"
        if stats['total_size'] > 0:
            size_mb = stats['total_size'] / (1024 * 1024)
            stats_text += f" | Boyut: {size_mb:.1f} MB"

        stats_label = ctk.CTkLabel(
            header_frame,
            text=stats_text,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        stats_label.pack(side="right")

    def _create_filter_section(self, parent):
        """Filtre ve arama bölümü"""
        filter_frame = ctk.CTkFrame(parent, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 10), padx=10)

        # Arama
        search_label = ctk.CTkLabel(filter_frame, text="Ara:", font=ctk.CTkFont(size=12))
        search_label.pack(side="left", padx=(0, 5))

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            placeholder_text="Video başlığı veya URL...",
            width=300
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_history())

        # Filtre
        filter_label = ctk.CTkLabel(filter_frame, text="Filtre:", font=ctk.CTkFont(size=12))
        filter_label.pack(side="left", padx=(10, 5))

        self.filter_var = ctk.StringVar(value="Tümü")
        self.filter_menu = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.filter_var,
            values=["Tümü", "Başarılı", "Başarısız"],
            command=lambda _: self.load_history(),
            width=120
        )
        self.filter_menu.pack(side="left")

    def _create_history_list(self, parent):
        """Geçmiş listesi"""
        # Scrollable frame
        self.history_frame = ctk.CTkScrollableFrame(parent, height=400)
        self.history_frame.pack(fill="both", expand=True, pady=(0, 10), padx=10)

    def _create_buttons(self, parent):
        """Alt butonlar"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        # Alt tarafta, başlıktaki üst boşlukla uyumlu olacak şekilde padding
        button_frame.pack(fill="x", padx=10, pady=(10, 10))

        refresh_button = ctk.CTkButton(
            button_frame,
            text="Yenile",
            command=self.load_history,
            width=100,
            height=32
        )
        refresh_button.pack(side="left", padx=5)

        clear_button = ctk.CTkButton(
            button_frame,
            text="Geçmişi Temizle",
            command=self.clear_history,
            width=120,
            height=32,
            fg_color="#8b4513",
            hover_color="#654321"
        )
        clear_button.pack(side="left", padx=5)

        close_button = ctk.CTkButton(
            button_frame,
            text="Kapat",
            command=self.window.destroy,
            width=100,
            height=32,
            fg_color="gray",
            hover_color="darkgray"
        )
        close_button.pack(side="right", padx=5)

    def load_history(self):
        """Geçmişi yükler"""
        # Önceki widget'ları temizle
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        # Filtreye göre veri çek
        filter_value = self.filter_var.get()
        if filter_value == "Başarılı":
            downloads = self.db.get_successful_downloads(100)
        elif filter_value == "Başarısız":
            downloads = self.db.get_failed_downloads(100)
        else:
            downloads = self.db.get_all_downloads(100)

        if not downloads:
            no_data_label = ctk.CTkLabel(
                self.history_frame,
                text="Henüz indirme geçmişi yok",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_data_label.pack(pady=50)
            return

        # Her indirme için card oluştur
        for download in downloads:
            self._create_download_card(download)

    def _create_download_card(self, download):
        """Tek bir indirme için card oluşturur"""
        card = ctk.CTkFrame(self.history_frame)
        card.pack(fill="x", padx=5, pady=5)

        # Durum rengi
        status_color = "#2d8659" if download['status'] == 'başarılı' else "#8b4513"

        # Sol çizgi (durum göstergesi)
        status_bar = ctk.CTkFrame(card, width=5, fg_color=status_color)
        status_bar.pack(side="left", fill="y", padx=(0, 8))

        # İçerik ve butonları aynı hizada tutmak için grid kullanan frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(side="left", fill="both", expand=True, pady=4, padx=(0, 8))

        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=0)

        # Başlık
        title = download['title'] or "Başlık alınamadı"
        title_label = ctk.CTkLabel(
            content_frame,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w")

        # Detaylar
        details = []
        if download['download_type']:
            type_map = {'video': 'Video', 'audio': 'Ses', 'both': 'Video + Ses'}
            details.append(f"Tip: {type_map.get(download['download_type'], download['download_type'])}")
        if download['quality']:
            details.append(f"Kalite: {download['quality']}")
        if download['file_size']:
            size_mb = download['file_size'] / (1024 * 1024)
            details.append(f"Boyut: {size_mb:.1f} MB")

        if details:
            details_text = " | ".join(details)
            details_label = ctk.CTkLabel(
                content_frame,
                text=details_text,
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            details_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Tarih
        try:
            date_obj = datetime.fromisoformat(download['download_date'])
            date_text = date_obj.strftime("%d.%m.%Y %H:%M")
        except:
            date_text = download['download_date']

        date_label = ctk.CTkLabel(
            content_frame,
            text=date_text,
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        date_label.grid(row=2, column=0, sticky="w", pady=(2, 0))

        # Hata mesajı (varsa)
        if download['error_message']:
            error_label = ctk.CTkLabel(
                content_frame,
                text=f"⚠ {download['error_message'][:100]}",
                font=ctk.CTkFont(size=10),
                text_color="#ff6b6b",
                anchor="w"
            )
            error_label.grid(row=3, column=0, sticky="w", pady=(4, 0))

        # Butonlar (başlık satırıyla aynı hizada, en sağda)
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=0, column=1, rowspan=2, sticky="ne", padx=(10, 0))

        if download['file_path'] and os.path.exists(download['file_path']):
            open_button = ctk.CTkButton(
                button_frame,
                text="Aç",
                command=lambda: self.open_file(download['file_path']),
                width=60,
                height=26,
                font=ctk.CTkFont(size=11)
            )
            open_button.pack(side="top", pady=(0, 2))

        delete_button = ctk.CTkButton(
            button_frame,
            text="Sil",
            command=lambda: self.delete_download(download['id']),
            width=60,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color="#8b4513",
            hover_color="#654321"
        )
        delete_button.pack(side="top")

    def search_history(self):
        """Geçmişte arama yapar"""
        query = self.search_var.get().strip()

        # Widget'ları temizle
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        if not query:
            self.load_history()
            return

        # Arama yap
        downloads = self.db.search_downloads(query, 100)

        if not downloads:
            no_result_label = ctk.CTkLabel(
                self.history_frame,
                text=f"'{query}' için sonuç bulunamadı",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_result_label.pack(pady=50)
            return

        # Sonuçları göster
        for download in downloads:
            self._create_download_card(download)

    def open_file(self, file_path):
        """Dosyayı açar"""
        try:
            os.startfile(file_path)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Hata", f"Dosya açılamadı:\n{e}")

    def delete_download(self, download_id):
        """İndirme kaydını siler"""
        from tkinter import messagebox
        result = messagebox.askyesno(
            "Onay",
            "Bu kaydı silmek istediğinize emin misiniz?",
            icon="question"
        )

        if result:
            self.db.delete_download(download_id)
            self.load_history()

    def clear_history(self):
        """Tüm geçmişi temizler"""
        from tkinter import messagebox
        result = messagebox.askyesno(
            "Onay",
            "Tüm indirme geçmişini silmek istediğinize emin misiniz?\n\nBu işlem geri alınamaz!",
            icon="warning"
        )

        if result:
            self.db.clear_history()
            self.load_history()
            messagebox.showinfo("Başarılı", "Geçmiş temizlendi!")
