@echo off
REM ========================================
REM Windows Icon Cache Temizleme
REM Bulanik ikonlari duzeltmek icin
REM ========================================

echo.
echo ========================================
echo   Windows Icon Cache Temizleme
echo ========================================
echo.
echo Bu islem Windows icon cache'ini temizleyecek.
echo Bulanik veya eski ikonlari duzelten bir islemdir.
echo.
pause

echo.
echo [1/4] Explorer kapatiliyor...
taskkill /f /im explorer.exe >nul 2>&1

echo [2/4] Icon cache dosyalari siliniyor...

REM Windows 10/11 icon cache lokasyonlari
del /f /s /q /a %localappdata%\IconCache.db >nul 2>&1
del /f /s /q /a %localappdata%\Microsoft\Windows\Explorer\iconcache*.db >nul 2>&1
del /f /s /q /a %localappdata%\Microsoft\Windows\Explorer\thumbcache*.db >nul 2>&1

REM Windows 7/8 uyumlulugu
del /f /s /q /a "%userprofile%\AppData\Local\IconCache.db" >nul 2>&1

echo [3/4] Thumbnail cache temizleniyor...
del /f /s /q /a "%localappdata%\Microsoft\Windows\Explorer\*.db" >nul 2>&1

echo [4/4] Explorer yeniden baslatiliyor...
start explorer.exe

echo.
echo ========================================
echo   Islem Tamamlandi!
echo ========================================
echo.
echo Icon cache temizlendi.
echo Artik yeni ikonu gorebilmelisiniz.
echo.
echo Sonraki adimlar:
echo 1. Installer'i yeniden olusturun
echo 2. Eski uygulamayi kaldir in
echo 3. Yeni installer ile kurun
echo 4. Bilgisayari yeniden baslatin (opsiyonel)
echo.

pause
