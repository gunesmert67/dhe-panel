@echo off
TITLE DHE Dashboard - Localhost
color 0A

:: ---------------------------------------------------------
:: AYARLAR VE DİZİN
:: ---------------------------------------------------------
SET "PROJE_DIZINI=%~dp0"
:: Sondaki ters slas'i kaldir
IF %PROJE_DIZINI:~-1%==\ SET PROJE_DIZINI=%PROJE_DIZINI:~0,-1%

echo.
echo ========================================================
echo   DHE DISTRIBUTED DASHBOARD v2 - LOCALHOST
echo ========================================================
echo   Sunucu: http://localhost:8501
echo ========================================================
echo.

:: ---------------------------------------------------------
:: STREAMLIT SUNUCUSU
:: ---------------------------------------------------------
echo Streamlit sunucusu baslatiliyor...
cd /d "%PROJE_DIZINI%"

:: Streamlit'i yeni pencerede başlat
start "DHE Streamlit Server" cmd /k "python -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --theme.base=light"

:: Sunucunun ayağa kalkması için bekleme
echo ...Sunucu hazirlaniyor (5 saniye bekleniyor)...
timeout /t 5 /nobreak >nul

:: Yerel tarayıcıyı aç
echo Tarayici aciliyor...
start http://localhost:8501

echo.
echo ========================================================
echo   Sunucu calisiyor! Kapatmak icin pencereyi kapatin.
echo ========================================================
pause
