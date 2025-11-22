# 🔨 YouT Video Mp3 Downloader - Build ve Installer Rehberi

Bu rehber, uygulamanızın Windows executable (.exe) ve installer dosyalarını oluşturmanız için adım adım talimatlar içerir.

---

## 📋 Ön Gereksinimler

### 1. Python ve Bağımlılıklar
```bash
# Python 3.7+ gerekli
python --version

# Gerekli paketleri yükleyin
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Inno Setup (Installer için)
- [Inno Setup İndirin](https://jrsoftware.org/isdl.php) (6.x veya üzeri)
- Kurulum sonrası PATH'e ekleyin veya tam yolu kullanın
- Türkçe dil desteği için "Languages" klasörünü kontrol edin

---

## 🎯 Adım 1: Eski Build Dosyalarını Temizleme

Temiz bir build için eski dosyaları silin:

```bash
# Windows PowerShell veya CMD'de:
rmdir /s /q build
rmdir /s /q dist
del YouT-Video-Mp3-Downloader.spec

# Veya manuel olarak:
# - build/ klasörünü silin
# - dist/ klasörünü silin
# - YouT-Video-Mp3-Downloader.spec dosyasını silin
```

**Not:** Her build öncesi bu temizliği yapmanız önerilir.

---

## 🏗️ Adım 2: PyInstaller ile EXE Oluşturma

### Otomatik Yöntem (Önerilen):
```bash
python build_exe.py
```

Bu script:
- ✅ PyInstaller'ı otomatik yükler (yoksa)
- ✅ icon.ico dosyasını kontrol eder
- ✅ Tüm bağımlılıkları paketler
- ✅ `dist/YouT-Video-Mp3-Downloader/` klasörü oluşturur

### Manuel Yöntem:
```bash
pyinstaller --name=YouT-Video-Mp3-Downloader ^
            --onedir ^
            --windowed ^
            --icon=icon.ico ^
            --hidden-import=customtkinter ^
            --hidden-import=PIL ^
            --hidden-import=PIL._tkinter_finder ^
            --hidden-import=yt_dlp ^
            --hidden-import=requests ^
            --collect-all=customtkinter ^
            --collect-data=customtkinter ^
            --collect-all=PIL ^
            --collect-all=yt_dlp ^
            --copy-metadata=customtkinter ^
            --copy-metadata=yt-dlp ^
            youtube_downloader.py
```

### Build Çıktısı:
```
dist/
└── YouT-Video-Mp3-Downloader/
    ├── YouT-Video-Mp3-Downloader.exe  ← Ana uygulama
    ├── _internal/                      ← Bağımlılıklar
    │   ├── customtkinter/
    │   ├── PIL/
    │   ├── yt_dlp/
    │   └── ... (diğer kütüphaneler)
    └── ... (diğer dosyalar)
```

### Test Edin:
```bash
# EXE'yi çalıştırın ve test edin
cd dist\YouT-Video-Mp3-Downloader
YouT-Video-Mp3-Downloader.exe
```

**Önemli Kontroller:**
- ✅ Uygulama başlıyor mu?
- ✅ İkon net görünüyor mu?
- ✅ Video indirme çalışıyor mu?
- ✅ FFmpeg otomatik kurulumu çalışıyor mu?

---

## 📦 Adım 3: Inno Setup ile Installer Oluşturma

### Gerekli Dosyalar:
Installer oluşturmadan önce şunları kontrol edin:
```
✓ dist/YouT-Video-Mp3-Downloader/  (PyInstaller çıktısı)
✓ icon.ico                          (102 KB, multi-size)
✓ LICENSE                           (MIT lisansı)
✓ README.md                         (dokümantasyon)
✓ installer_script.iss              (Inno Setup scripti)
```

### Installer Oluşturma:

#### Yöntem 1: Inno Setup GUI ile
1. Inno Setup Compiler'ı açın
2. `File` → `Open` → `installer_script.iss` dosyasını seçin
3. `Build` → `Compile` (veya F9)
4. Installer `installer/` klasöründe oluşacak

#### Yöntem 2: Komut Satırı ile
```bash
# Inno Setup PATH'te ise:
iscc installer_script.iss

# Tam yol ile:
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
```

### Installer Çıktısı:
```
installer/
└── YouT-Video-Mp3-Downloader-Setup-v1.0.0.exe  (~35-50 MB)
```

### Test Edin:
1. Installer'ı çalıştırın
2. Kurulum adımlarını takip edin
3. **ÖNEMLİ:** Masaüstü ikonunu kontrol edin:
   - ✅ İkon net ve keskin mi?
   - ✅ Farklı DPI ayarlarında test edin
4. Uygulamayı başlatın ve test edin
5. Kaldırma işlemini test edin

---

## 🔧 Sorun Giderme

### Problem 1: İkon Bulanık Görünüyor
**Çözüm:** icon.ico dosyasını yeniden oluşturun:
```bash
python -c "from PIL import Image; img = Image.open('YouT_Image.png').convert('RGBA'); sizes = [(256,256),(128,128),(96,96),(64,64),(48,48),(32,32),(24,24),(16,16)]; icons = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]; icons[0].save('icon.ico', format='ICO', append_images=icons[1:]); print('Icon created')"
```
Ardından build'i tekrar yapın.

### Problem 2: PyInstaller "Module not found" Hatası
**Çözüm:** Eksik modülü ekleyin:
```bash
pyinstaller --hidden-import=MODUL_ADI ...
```

### Problem 3: Uygulama Açılmıyor (EXE Hemen Kapanıyor)
**Çözüm:** Console ile test edin:
```bash
# --windowed yerine --console kullanın
pyinstaller --console --icon=icon.ico youtube_downloader.py
```
Hata mesajlarını okuyup düzeltin.

### Problem 4: FFmpeg Otomatik Kurulum Çalışmıyor
**Kontrol:**
- İnternet bağlantısı var mı?
- Windows Defender veya Antivirus engelliyor mu?
- `temp_ffmpeg/` klasörü oluşturuluyor mu?

### Problem 5: Inno Setup Türkçe Dil Bulunamıyor
**Çözüm:**
```bash
# Inno Setup kurulum dizininde:
C:\Program Files (x86)\Inno Setup 6\Languages\Turkish.isl
```
Dosyanın var olduğundan emin olun.

---

## 📊 Dosya Boyutları (Yaklaşık)

| Dosya | Boyut |
|-------|-------|
| icon.ico | 102 KB |
| YouT-Video-Mp3-Downloader.exe | ~10-15 MB |
| dist/ klasörü (tümü) | ~60-80 MB |
| Installer (.exe) | ~35-50 MB |

---

## 🚀 Dağıtım

### Portable Versiyon:
```bash
# dist/YouT-Video-Mp3-Downloader/ klasörünü ZIP'leyin
# Kullanıcılar açıp direkt çalıştırabilir
```

### Installer Versiyonu:
```bash
# installer/YouT-Video-Mp3-Downloader-Setup-v1.0.0.exe
# Kullanıcılar kurulum yaparak kullanır
# Program Files'a yüklenir, Start Menu kısayolu oluşturulur
```

### GitHub Release:
1. Her iki versiyonu da Release'e ekleyin
2. Release notları yazın
3. Assets olarak yükleyin:
   - `YouT-Video-Mp3-Downloader-v1.0.0-Portable.zip`
   - `YouT-Video-Mp3-Downloader-Setup-v1.0.0.exe`

---

## 🔄 Versiyon Güncellemesi

Yeni versiyon için:

1. **Versiyon numarasını güncelleyin:**
   - `youtube_downloader.py` → `APP_VERSION = "v1.0.1"`
   - `installer_script.iss` → `#define MyAppVersion "1.0.1"`

2. **Değişiklikleri commit edin:**
   ```bash
   git add .
   git commit -m "chore: bump version to v1.0.1"
   git tag v1.0.1
   git push origin master --tags
   ```

3. **Build sürecini tekrarlayın**

---

## ✅ Checklist (Her Build Öncesi)

- [ ] icon.ico dosyası 102 KB ve multi-size (7 boyut)
- [ ] Eski build/ ve dist/ klasörleri temizlendi
- [ ] requirements.txt güncel
- [ ] APP_VERSION doğru
- [ ] LICENSE ve README güncel
- [ ] Git commit'lendi
- [ ] PyInstaller build başarılı
- [ ] EXE test edildi (çalışıyor)
- [ ] İkon net görünüyor
- [ ] Inno Setup build başarılı
- [ ] Installer test edildi
- [ ] Masaüstü ikonu net
- [ ] Kaldırma çalışıyor

---

## 📞 Yardım

Sorun yaşarsanız:
1. Bu rehberdeki sorun giderme bölümünü kontrol edin
2. Build log'larını inceleyin
3. GitHub Issues'da sorun açın

---

**Son Güncelleme:** 2024-11-22
**Versiyon:** 1.0.0
