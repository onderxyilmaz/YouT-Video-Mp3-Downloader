"""
SQLite veritabanı yönetimi - İndirme geçmişi
"""
import sqlite3
import os
from datetime import datetime


class DownloadHistory:
    """İndirme geçmişini yöneten sınıf"""

    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), "download_history.db")
        self._create_table()

    def _create_table(self):
        """Veritabanı tablosunu oluşturur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                download_type TEXT,
                quality TEXT,
                file_path TEXT,
                file_size INTEGER,
                status TEXT,
                error_message TEXT,
                download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def add_download(self, url, title=None, download_type=None, quality=None,
                     file_path=None, file_size=None, status='başarılı', error_message=None):
        """Yeni indirme kaydı ekler"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO downloads (url, title, download_type, quality, file_path, file_size, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (url, title, download_type, quality, file_path, file_size, status, error_message))

        conn.commit()
        download_id = cursor.lastrowid
        conn.close()

        return download_id

    def get_all_downloads(self, limit=100):
        """Tüm indirmeleri döndürür (en yeniden başlayarak)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM downloads
            ORDER BY download_date DESC
            LIMIT ?
        ''', (limit,))

        downloads = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return downloads

    def get_successful_downloads(self, limit=100):
        """Başarılı indirmeleri döndürür"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM downloads
            WHERE status = 'başarılı'
            ORDER BY download_date DESC
            LIMIT ?
        ''', (limit,))

        downloads = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return downloads

    def get_failed_downloads(self, limit=100):
        """Başarısız indirmeleri döndürür"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM downloads
            WHERE status = 'başarısız'
            ORDER BY download_date DESC
            LIMIT ?
        ''', (limit,))

        downloads = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return downloads

    def search_downloads(self, query, limit=100):
        """İndirmelerde arama yapar (title veya URL)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM downloads
            WHERE title LIKE ? OR url LIKE ?
            ORDER BY download_date DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))

        downloads = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return downloads

    def url_exists(self, url):
        """URL daha önce indirilmiş mi kontrol eder"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM downloads
            WHERE url = ? AND status = 'başarılı'
        ''', (url,))

        count = cursor.fetchone()[0]
        conn.close()

        return count > 0

    def get_download_count(self):
        """Toplam indirme sayısını döndürür"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM downloads')
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def get_total_size(self):
        """Toplam indirilen dosya boyutunu döndürür (byte)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT SUM(file_size) FROM downloads
            WHERE status = 'başarılı' AND file_size IS NOT NULL
        ''')

        total = cursor.fetchone()[0]
        conn.close()

        return total if total else 0

    def delete_download(self, download_id):
        """Belirli bir indirme kaydını siler"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM downloads WHERE id = ?', (download_id,))

        conn.commit()
        conn.close()

    def clear_history(self):
        """Tüm geçmişi temizler"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM downloads')

        conn.commit()
        conn.close()

    def get_statistics(self):
        """İstatistikleri döndürür"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Toplam indirme
        cursor.execute('SELECT COUNT(*) FROM downloads')
        total_downloads = cursor.fetchone()[0]

        # Başarılı indirme
        cursor.execute('SELECT COUNT(*) FROM downloads WHERE status = "başarılı"')
        successful = cursor.fetchone()[0]

        # Başarısız indirme
        cursor.execute('SELECT COUNT(*) FROM downloads WHERE status = "başarısız"')
        failed = cursor.fetchone()[0]

        # Toplam boyut
        cursor.execute('SELECT SUM(file_size) FROM downloads WHERE status = "başarılı"')
        total_size = cursor.fetchone()[0] or 0

        conn.close()

        return {
            'total_downloads': total_downloads,
            'successful': successful,
            'failed': failed,
            'total_size': total_size
        }
