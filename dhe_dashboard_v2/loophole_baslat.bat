@echo off
setlocal EnableDelayedExpansion
TITLE DHE Dashboard - Loophole Tunnel
color 0B

:: ---------------------------------------------------------
:: AYARLAR VE DİZİN
:: ---------------------------------------------------------
SET "PROJE_DIZINI=%~dp0"
:: Sondaki ters slas'i kaldir
IF %PROJE_DIZINI:~-1%==\ SET PROJE_DIZINI=%PROJE_DIZINI:~0,-1%

echo.
echo ========================================================
echo   DHE DISTRIBUTED DASHBOARD v2 - LOOPHOLE TUNNEL
echo ========================================================
echo   Erisim: https://dhe-endustriyel.loophole.site
echo ========================================================
echo.

:: ---------------------------------------------------------
:: 1. STREAMLIT SUNUCUSU (Arka Planda)
:: ---------------------------------------------------------
echo [1/2] Streamlit sunucusu baslatiliyor...
cd /d "%PROJE_DIZINI%"

:: Streamlit'i yeni pencerede başlat
start "DHE Streamlit Server" cmd /k "python -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --theme.base=light"

:: Sunucunun ayağa kalkması için bekleme
echo      ...Sunucu hazirlaniyor (8 saniye bekleniyor)...
timeout /t 8 /nobreak >nul

:: ---------------------------------------------------------
:: 2. LOOPHOLE TÜNELİ
:: ---------------------------------------------------------
echo [2/2] Loophole tuneli kuruluyor...

:: Loophole'u birden fazla konumda ara
SET "LOOPHOLE_PATH="

:: 1. Masaustu
if exist "%USERPROFILE%\Desktop\loophole.exe" (
    SET "LOOPHOLE_PATH=%USERPROFILE%\Desktop\loophole.exe"
    echo      ...Loophole masaustunde bulundu.
)

:: 2. Downloads
if "%LOOPHOLE_PATH%"=="" if exist "%USERPROFILE%\Downloads\loophole.exe" (
    SET "LOOPHOLE_PATH=%USERPROFILE%\Downloads\loophole.exe"
    echo      ...Loophole Downloads klasorunde bulundu.
)

:: 3. Proje dizini
if "%LOOPHOLE_PATH%"=="" if exist "%PROJE_DIZINI%\loophole.exe" (
    SET "LOOPHOLE_PATH=%PROJE_DIZINI%\loophole.exe"
    echo      ...Loophole proje dizininde bulundu.
)

:: 4. PATH'de
if "%LOOPHOLE_PATH%"=="" (
    where loophole.exe >nul 2>&1
    if !errorlevel! equ 0 (
        SET "LOOPHOLE_PATH=loophole.exe"
        echo      ...Loophole PATH'de bulundu.
    )
)

:: Loophole bulunduysa calistir
if not "%LOOPHOLE_PATH%"=="" (
    echo.
    echo ========================================================
    echo   TUNEL ACILIYOR...
    echo   URL: https://dhe-endustriyel.loophole.site
    echo ========================================================
    echo.
    echo   [NOT] Bu pencereyi KAPATMAYIN! Tunel kapanir.
    echo   [NOT] Ctrl+C ile tuneli durdurabilirsiniz.
    echo.
    "%LOOPHOLE_PATH%" http 8501 --hostname dhe-endustriyel
    echo.
    echo ========================================================
    echo   Tunel kapandi veya hata olustu.
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo   [HATA] Loophole.exe bulunamadi!
    echo ========================================================
    echo.
    echo   Aranan konumlar:
    echo   - %USERPROFILE%\Desktop\loophole.exe
    echo   - %USERPROFILE%\Downloads\loophole.exe
    echo   - %PROJE_DIZINI%\loophole.exe
    echo.
    echo   Loophole'u indirmek icin:
    echo   https://loophole.cloud/download
    echo.
)

echo.
echo Cikmak icin bir tusa basin...
pause >nul
