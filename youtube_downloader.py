"""
YouTube Video Mp3 Downloader
Ana giriş noktası
"""
import customtkinter as ctk
from ui import YouTubeDownloaderUI


def main():
    """Uygulamayı başlatır"""
    root = ctk.CTk()
    app = YouTubeDownloaderUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
