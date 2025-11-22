@echo off
REM ========================================
REM YouT Video Mp3 Downloader
REM Otomatik Build ve Installer Scripti
REM ========================================

echo.
echo ========================================
echo   YouT Video Mp3 Downloader Builder
echo ========================================
echo.

REM Renkli output için
setlocal EnableDelayedExpansion

REM 1. Eski dosyalari temizle
echo [1/5] Eski build dosyalari temizleniyor...
if exist "build" (
    rmdir /s /q build
    echo   - build/ klasoru silindi
)
if exist "dist" (
    rmdir /s /q dist
    echo   - dist/ klasoru silindi
)
if exist "YouT-Video-Mp3-Downloader.spec" (
    del /q YouT-Video-Mp3-Downloader.spec
    echo   - .spec dosyasi silindi
)
echo   ^> Temizlik tamamlandi!
echo.

REM 2. Icon dosyasi kontrolu
echo [2/5] Icon dosyasi kontrol ediliyor...
if not exist "icon.ico" (
    echo   ! icon.ico bulunamadi, olusturuluyor...
    python -c "from PIL import Image; img = Image.open('YouT_Image.png').convert('RGBA'); sizes = [(256,256),(128,128),(96,96),(64,64),(48,48),(32,32),(24,24),(16,16)]; icons = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]; icons[0].save('icon.ico', format='ICO', append_images=icons[1:]); print('  + Icon olusturuldu (8 boyut)')"
    if errorlevel 1 (
        echo   X Icon olusturulamadi!
        pause
        exit /b 1
    )
) else (
    REM Icon boyutunu kontrol et
    for %%A in (icon.ico) do set size=%%~zA
    if !size! LSS 50000 (
        echo   ! Mevcut icon cok kucuk ^(!size! bytes^), yeniden olusturuluyor...
        python -c "from PIL import Image; img = Image.open('YouT_Image.png').convert('RGBA'); sizes = [(256,256),(128,128),(96,96),(64,64),(48,48),(32,32),(24,24),(16,16)]; icons = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]; icons[0].save('icon.ico', format='ICO', append_images=icons[1:]); print('  + Icon yenilendi')"
    ) else (
        echo   ^> Icon dosyasi mevcut ^(!size! bytes^)
    )
)
echo.

REM 3. PyInstaller ile build
echo [3/5] PyInstaller ile EXE olusturuluyor...
echo   Bu islem 2-5 dakika surebilir...
echo.
python build_exe.py
if errorlevel 1 (
    echo.
    echo   X Build basarisiz!
    pause
    exit /b 1
)
echo   ^> PyInstaller build tamamlandi!
echo.

REM 4. Build test
echo [4/5] Build test ediliyor...
if exist "dist\YouT-Video-Mp3-Downloader\YouT-Video-Mp3-Downloader.exe" (
    echo   ^> EXE dosyasi basariyla olusturuldu
    for %%A in ("dist\YouT-Video-Mp3-Downloader\YouT-Video-Mp3-Downloader.exe") do (
        echo   - Boyut: %%~zA bytes
    )
) else (
    echo   X EXE dosyasi bulunamadi!
    pause
    exit /b 1
)
echo.

REM 5. Inno Setup ile installer olustur
echo [5/5] Inno Setup ile installer olusturuluyor...

REM Inno Setup konumunu bul
set "INNO_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if defined INNO_PATH (
    echo   - Inno Setup bulundu: !INNO_PATH!
    "!INNO_PATH!" installer_script.iss
    if errorlevel 1 (
        echo   X Installer olusturulamadi!
        pause
        exit /b 1
    )
    echo   ^> Installer basariyla olusturuldu!
) else (
    echo   ! Inno Setup bulunamadi
    echo   - Inno Setup'i indirin: https://jrsoftware.org/isdl.php
    echo   - Veya manuel olarak calistirin: iscc installer_script.iss
)
echo.

REM 6. Sonuc raporu
echo ========================================
echo   BUILD TAMAMLANDI!
echo ========================================
echo.
echo Olusturulan dosyalar:
echo.
if exist "dist\YouT-Video-Mp3-Downloader\YouT-Video-Mp3-Downloader.exe" (
    for %%A in ("dist\YouT-Video-Mp3-Downloader\YouT-Video-Mp3-Downloader.exe") do (
        echo   [EXE] %%~nxA
        echo         Konum: dist\YouT-Video-Mp3-Downloader\
        echo         Boyut: %%~zA bytes
    )
    echo.
)

if exist "installer\YouT-Video-Mp3-Downloader-Setup-v1.0.0.exe" (
    for %%A in ("installer\YouT-Video-Mp3-Downloader-Setup-v1.0.0.exe") do (
        echo   [INSTALLER] %%~nxA
        echo               Konum: installer\
        echo               Boyut: %%~zA bytes
    )
    echo.
)

echo ========================================
echo   SONRAKI ADIMLAR:
echo ========================================
echo.
echo 1. Test Edin:
echo    cd dist\YouT-Video-Mp3-Downloader
echo    YouT-Video-Mp3-Downloader.exe
echo.
echo 2. Installer'i Test Edin:
echo    installer\YouT-Video-Mp3-Downloader-Setup-v1.0.0.exe
echo.
echo 3. GitHub Release Olusturun:
echo    - EXE klasorunu ZIP'leyin
echo    - Installer'i yukleyin
echo.
echo ========================================
echo.

pause
