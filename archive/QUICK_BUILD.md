# ⚡ Hızlı Build Komutu Referansı

Deneyimli kullanıcılar için hızlı komut listesi.

---

## 🎯 Tam Build Süreci (Tek Seferde)

### Windows CMD/PowerShell:
```batch
:: 1. Temizlik
rmdir /s /q build dist & del YouT-Video-Mp3-Downloader.spec 2>nul

:: 2. İkon kontrolü (isteğe bağlı - sadece ilk kez)
python -c "from PIL import Image; img = Image.open('YouT_Image.png').convert('RGBA'); sizes = [(256,256),(128,128),(96,96),(64,64),(48,48),(32,32),(24,24),(16,16)]; icons = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]; icons[0].save('icon.ico', format='ICO', append_images=icons[1:])"

:: 3. PyInstaller Build
python build_exe.py

:: 4. Test
cd dist\YouT-Video-Mp3-Downloader && YouT-Video-Mp3-Downloader.exe

:: 5. Geri dön
cd ..\..

:: 6. Installer oluştur (Inno Setup kurulu ise)
iscc installer_script.iss
```

### PowerShell (Tek Satır):
```powershell
Remove-Item -Recurse -Force build,dist -ErrorAction SilentlyContinue; Remove-Item YouT-Video-Mp3-Downloader.spec -ErrorAction SilentlyContinue; python build_exe.py; iscc installer_script.iss
```

---

## 📦 Sadece EXE Oluştur

```bash
python build_exe.py
```

**Çıktı:** `dist/YouT-Video-Mp3-Downloader/YouT-Video-Mp3-Downloader.exe`

---

## 🔧 Sadece Installer Oluştur

```bash
iscc installer_script.iss
```

**Çıktı:** `installer/YouT-Video-Mp3-Downloader-Setup-v1.0.0.exe`

**Not:** Önce PyInstaller build yapılmış olmalı!

---

## 🎨 Sadece İkon Yenile

```bash
python -c "from PIL import Image; img = Image.open('YouT_Image.png').convert('RGBA'); sizes = [(256,256),(128,128),(96,96),(64,64),(48,48),(32,32),(24,24),(16,16)]; icons = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]; icons[0].save('icon.ico', format='ICO', append_images=icons[1:]); print('Icon created with 8 sizes:', ', '.join([f'{s[0]}x{s[1]}' for s in sizes]))"
```

**Çıktı:** `icon.ico` (102 KB, 8 boyut)

---

## 🧹 Temizlik

```batch
:: Windows
rmdir /s /q build
rmdir /s /q dist
rmdir /s /q installer
del YouT-Video-Mp3-Downloader.spec
del icon.ico
```

```bash
# Linux/macOS
rm -rf build dist installer
rm -f YouT-Video-Mp3-Downloader.spec icon.ico
```

---

## 🔍 İkon Doğrulama

```bash
:: Dosya boyutu (102 KB olmalı)
dir icon.ico

:: Detaylı bilgi
python -c "from PIL import Image; ico = Image.open('icon.ico'); print(f'Format: {ico.format}, Size: {ico.size}, Mode: {ico.mode}')"
```

**Beklenen:** `Format: ICO, Size: (256, 256), Mode: RGBA`

---

## 📊 Versiyon Güncelleme

```bash
# 1. Versiyon numarasını değiştir
# youtube_downloader.py: APP_VERSION = "v1.0.1"
# installer_script.iss: #define MyAppVersion "1.0.1"

# 2. Git commit
git add .
git commit -m "chore: bump version to v1.0.1"
git tag v1.0.1

# 3. Build yap
python build_exe.py
iscc installer_script.iss

# 4. Push
git push origin master --tags
```

---

## 🚨 Hata Durumunda

### PyInstaller hatası:
```bash
# Console modunda test et
pyinstaller --console --icon=icon.ico youtube_downloader.py
cd dist\youtube_downloader
youtube_downloader.exe
```

### Inno Setup bulunamıyor:
```bash
# Tam yol kullan
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
```

### İkon hatası:
```bash
# İkonu yeniden oluştur
python create_high_quality_icon.py YouT_Image.png
```

---

**İpucu:** Bu komutları sık kullanıyorsanız, bir `.bat` veya `.ps1` dosyası oluşturun!

Örnek `build_all.bat`:
```batch
@echo off
echo Temizlik yapiliyor...
rmdir /s /q build dist 2>nul

echo Build baslatiliyor...
python build_exe.py

echo Installer olusturuluyor...
iscc installer_script.iss

echo Bitti!
pause
```
