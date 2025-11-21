# YouT Video Mp3 Downloader v1.0.0

<div align="center">

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![GitHub stars](https://img.shields.io/github/stars/onderxyilmaz/YouT-Video-Mp3-Downloader?style=social)
![GitHub forks](https://img.shields.io/github/forks/onderxyilmaz/YouT-Video-Mp3-Downloader?style=social)

YouTube videolarını video (MP4) ve/veya ses (MP3) formatında indirmek için modern bir GUI uygulaması.

</div>

## 📸 Ekran Görüntüleri

> *Yakında eklenecek*

## ✨ Özellikler

- 🎥 **Video indirme** (MP4 formatında, en iyi kalitede)
- 🎵 **Ses indirme** (MP3 formatında, 192kbps)
- 🎬 **Video ve ses birlikte indirme**
- 📁 **İndirme klasörü seçimi** (son seçilen klasör hatırlanır)
- 📊 **Gerçek zamanlı ilerleme göstergesi**
- 🎨 **Modern ve kullanıcı dostu dark tema arayüz**
- ⚡ **FFmpeg otomatik kurulumu** (Windows için)
- ✅ **URL validasyonu** (sadece geçerli YouTube linkleri)
- 🔄 **Arka plan indirme** (uygulama donmaz)
- 💾 **Ayarlar hatırlama** (indirme klasörü vb.)

## Gereksinimler

- Python 3.7 veya üzeri
- FFmpeg (opsiyonel ama önerilir - en iyi kalite için gerekli)

### FFmpeg Kurulumu

**FFmpeg olmadan da çalışır**, ancak:
- Video kalitesi biraz düşük olabilir
- MP3 dönüştürme yapılamaz (ses dosyası orijinal formatta indirilir)
- Video ve ses birleştirme yapılamaz

**Otomatik Kurulum (Önerilen - Windows):**
Uygulama içinde FFmpeg yoksa, "FFmpeg'i Otomatik Kur" butonuna tıklayarak FFmpeg'i otomatik olarak indirip kurabilirsiniz. Bu özellik şu anda sadece Windows için desteklenmektedir.

**Manuel Kurulum:**

**Windows:**
1. [FFmpeg Windows Builds](https://www.gyan.dev/ffmpeg/builds/) adresinden indirin
2. ZIP dosyasını açın ve `bin` klasöründeki `ffmpeg.exe` dosyasını:
   - Sistem PATH'ine ekleyin, VEYA
   - Uygulama klasörüne kopyalayın

**Alternatif (Chocolatey ile):**
```bash
choco install ffmpeg
```

**Alternatif (Scoop ile):**
```bash
scoop install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Kurulumu kontrol etmek için:**
```bash
ffmpeg -version
```

## 📦 Kurulum

### 1. Python Kurulumu
Python 3.7 veya üzeri sürüm gereklidir. [Python'u buradan indirin](https://www.python.org/downloads/).

### 2. Projeyi İndirin
```bash
git clone https://github.com/onderxyilmaz/YouT-Video-Mp3-Downloader.git
cd YouT-Video-Mp3-Downloader
```

veya ZIP olarak indirip açın.

### 3. Gerekli Paketleri Yükleyin
```bash
pip install -r requirements.txt
```

**Gerekli paketler:**
- `yt-dlp` - YouTube video indirme
- `customtkinter` - Modern GUI
- `pillow` - Görüntü işleme
- `requests` - FFmpeg indirme

## 🚀 Kullanım

### Uygulamayı Başlatın
```bash
python youtube_downloader.py
```

### Adım Adım:

1. **YouTube URL'sini girin**
   - Video URL'sini yapıştırın
   - URL otomatik olarak doğrulanır
   - Geçersiz URL'lerde indirme butonu pasif kalır

2. **İndirme tipini seçin**
   - 🎥 **Video**: Sadece video (MP4)
   - 🎵 **Ses**: Sadece ses (MP3)
   - 🎬 **Her İkisi**: Hem video hem ses ayrı dosyalar olarak

3. **İndirme klasörünü seçin**
   - Varsayılan: Downloads klasörü
   - Son seçtiğiniz klasör hatırlanır
   - Manuel yazma devre dışı, buton ile seçim yapılır

4. **İndirmeyi başlatın**
   - İlerleme çubuğu gerçek zamanlı güncellenir
   - İndirme sırasında form kilitlenir
   - Tamamlandığında bildirim alırsınız

### 🎯 Desteklenen URL Formatları
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/watch?v=VIDEO_ID&list=...`

## 📝 Notlar

- ✅ İndirme işlemi arka planda çalışır, uygulama donmaz
- 💾 İndirilen dosyalar seçtiğiniz klasöre kaydedilir
- 🎬 FFmpeg varsa: Video MP4, ses MP3 formatında indirilir
- ⚠️ FFmpeg yoksa: Dosyalar orijinal formatlarında indirilir (webm, m4a vb.)
- 📊 Uygulama başlangıçta FFmpeg durumunu gösterir
- ⏱️ Uzun videolar için indirme süresi uzun olabilir
- 🌐 İnternet hızınız indirme süresini etkiler

## 🐛 Bilinen Sorunlar

- Bazı yaş kısıtlamalı videolar indirilemeyebilir
- Çok uzun (>2 saat) videolarda yavaşlama olabilir
- Bazı premium içerikler desteklenmez

## 🔄 Sürüm Geçmişi

### v1.0.0 (2024)
- ✨ İlk stabil sürüm
- 🎥 Video/Ses/Her İkisi indirme desteği
- ⚡ FFmpeg otomatik kurulum (Windows)
- 📁 Klasör seçimi ve hatırlama
- ✅ URL validasyonu
- 🎨 Modern dark tema arayüz

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları izleyin:

1. Bu repo'yu fork edin
2. Feature branch'i oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

Detaylı bilgi için [CONTRIBUTING.md](CONTRIBUTING.md) dosyasına bakın.

## 💝 Destek

Bu proje tamamen ücretsizdir ve açık kaynaklıdır. Eğer yararlı bulduysanız:

- ⭐ GitHub'da yıldız vererek
- 🐛 Hata bildirerek
- 📣 Sosyal medyada paylaşarak
- 💰 Kahve ısmarlayarak destek olabilirsiniz

<!-- [![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-yellow.svg)](https://buymeacoffee.com/onderyilmaz) -->

## ⚖️ Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## ⚠️ Yasal Uyarı

**ÖNEMLİ:** Bu araç yalnızca eğitim amaçlıdır. Kullanıcılar, bu aracı kullanırken YouTube'un [Kullanım Şartları](https://www.youtube.com/t/terms)'na ve telif hakkı yasalarına uymakla yükümlüdür.

- ✅ Sadece kendi içeriklerinizi indirin
- ✅ Telif hakkı izniniz olan videoları indirin
- ✅ Eğitim ve kişisel kullanım için kullanın
- ❌ Ticari amaçla kullanmayın
- ❌ Başkalarının telif haklarını ihlal etmeyin

**Sorumluluk Reddi:** Geliştirici, bu aracın yanlış kullanımından kaynaklanan herhangi bir yasal sorundan sorumlu değildir.

## 📧 İletişim

UnderSpeed - Onder Yilmaz

Proje Linki: [https://github.com/onderxyilmaz/YouT-Video-Mp3-Downloader](https://github.com/onderxyilmaz/YouT-Video-Mp3-Downloader)

## 🙏 Teşekkürler

Bu proje şu harika açık kaynak projeleri kullanmaktadır:

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube indirme motoru
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI framework
- [FFmpeg](https://ffmpeg.org/) - Medya işleme

---

<div align="center">

**⭐ Beğendiyseniz yıldız vermeyi unutmayın! ⭐**

Made with ❤️ by UnderSpeed

</div>

