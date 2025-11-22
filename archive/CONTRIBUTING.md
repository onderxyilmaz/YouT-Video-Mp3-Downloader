# Katkıda Bulunma Rehberi

YouT Video Mp3 Downloader projesine katkıda bulunmak istediğiniz için teşekkür ederiz! 🎉

## 🚀 Nasıl Katkıda Bulunabilirim?

### 1. Hata Bildirimi (Bug Report)

Bir hata bulduysanız:

1. Önce [Issues](https://github.com/onderxyilmaz/YouT-Video-Mp3-Downloader/issues) sayfasından benzer bir hatanın bildirilip bildirilmediğini kontrol edin
2. Yoksa yeni bir Issue açın
3. Hatayı detaylı açıklayın:
   - Ne yaptınız?
   - Ne bekliyordunuz?
   - Ne oldu?
   - Hata mesajı (varsa)
   - İşletim sistemi ve Python versiyonu

### 2. Özellik Önerisi (Feature Request)

Yeni bir özellik öneriniz varsa:

1. [Issues](https://github.com/onderxyilmaz/YouT-Video-Mp3-Downloader/issues) sayfasından "Feature Request" etiketi ile yeni bir Issue açın
2. Özelliği detaylı açıklayın
3. Neden yararlı olacağını belirtin
4. Mümkünse örnek kullanım senaryoları verin

### 3. Kod Katkısı (Pull Request)

Kod katkısında bulunmak için:

1. **Fork edin**
   ```bash
   # GitHub'da "Fork" butonuna tıklayın
   ```

2. **Clone edin**
   ```bash
   git clone https://github.com/YOUR-USERNAME/YouT-Video-Mp3-Downloader.git
   cd YouT-Video-Mp3-Downloader
   ```

3. **Branch oluşturun**
   ```bash
   git checkout -b feature/amazing-feature
   # veya
   git checkout -b fix/bug-fix
   ```

4. **Değişikliklerinizi yapın**
   - Kod yazarken Python PEP 8 standardına uyun
   - Kodunuza yorum ekleyin
   - Değişikliklerinizi test edin

5. **Commit edin**
   ```bash
   git add .
   git commit -m "feat: amazing new feature"
   # veya
   git commit -m "fix: fixed bug in download function"
   ```

6. **Push edin**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Pull Request açın**
   - GitHub'da repo sayfanıza gidin
   - "Pull Request" butonuna tıklayın
   - Değişikliklerinizi açıklayın
   - Pull Request gönderin

## 📋 Commit Mesajı Kuralları

Commit mesajları şu formatta olmalı:

```
<tip>: <açıklama>

[opsiyonel detaylı açıklama]
```

**Tipler:**
- `feat`: Yeni özellik
- `fix`: Hata düzeltme
- `docs`: Dokümantasyon değişikliği
- `style`: Kod formatı (kodun çalışmasını etkilemeyen)
- `refactor`: Kod yeniden yapılandırma
- `test`: Test ekleme/düzeltme
- `chore`: Bakım işleri

**Örnekler:**
```bash
git commit -m "feat: add playlist download support"
git commit -m "fix: resolve FFmpeg installation error on Windows 11"
git commit -m "docs: update installation instructions"
```

## 🎨 Kod Standartları

### Python Stil Rehberi

- PEP 8 standardına uyun
- Satır uzunluğu: maksimum 100 karakter
- Fonksiyonlara docstring ekleyin
- Değişken isimleri açıklayıcı olsun

```python
def download_video(url: str, output_path: str) -> bool:
    """
    YouTube videosunu indirir.
    
    Args:
        url: YouTube video URL'si
        output_path: İndirme klasörü yolu
        
    Returns:
        bool: İndirme başarılı ise True
    """
    pass
```

### GUI Kuralları

- CustomTkinter bileşenlerini kullanın
- Dark tema uyumlu renkler seçin
- Tutarlı padding/margin değerleri (10, 20 katları)
- Her widget için açıklayıcı değişken isimleri

## 🧪 Test Etme

Değişikliklerinizi test edin:

1. **Manuel Test:**
   ```bash
   python youtube_downloader.py
   ```

2. **Farklı senaryoları test edin:**
   - Farklı YouTube URL formatları
   - Farklı indirme tipleri (video/ses/her ikisi)
   - FFmpeg var/yok durumları
   - Uzun/kısa videolar

3. **Hata durumlarını test edin:**
   - Geçersiz URL
   - İnternet bağlantısı kesilmesi
   - Disk dolu
   - İzin sorunları

## 📝 Dokümantasyon

Eğer yeni bir özellik ekliyorsanız:

- README.md'yi güncelleyin
- Gerekirse kullanım örnekleri ekleyin
- Kodunuza yeterli yorum ekleyin

## ❓ Sorularınız mı Var?

- [Issue](https://github.com/onderxyilmaz/YouT-Video-Mp3-Downloader/issues) açın
- Veya [Discussions](https://github.com/onderxyilmaz/YouT-Video-Mp3-Downloader/discussions) sayfasını kullanın

## 📜 Davranış Kuralları

- Saygılı olun
- Yapıcı eleştiri yapın
- Yardımcı olun
- Öğrenmeye açık olun

## 🙏 Teşekkürler

Her türlü katkı değerlidir:
- Kod
- Dokümantasyon
- Hata bildirimi
- Özellik önerisi
- Testler
- Çeviriler

Katkılarınız için teşekkür ederiz! ❤️

