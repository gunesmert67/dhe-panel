"""
DHE Dashboard - Yardımcı Fonksiyonlar
=====================================
Dönüşüm, temizleme ve formatlama fonksiyonları.
"""
import pandas as pd
from typing import Union, Optional

from config.constants import YEARLY_EXCHANGE_RATES
import time
import functools
import logging

def retry_on_exception(max_retries=3, delay=2, exceptions=(Exception,)):
    """
    Fonksiyonu hata durumunda belirtilen sayıda tekrar dener.
    
    Args:
        max_retries (int): Maksimum deneme sayısı
        delay (int): Denemeler arası bekleme süresi (saniye)
        exceptions (tuple): Yakalanacak hata tipleri
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(__name__)
            last_err = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_err = e
                    logger.warning(f"Hata ({attempt + 1}/{max_retries}): {e}. {delay} sn sonra yeniden deneniyor... [{func.__name__}]")
                    time.sleep(delay)
            
            logger.error(f"{func.__name__} fonksiyonu {max_retries} deneme sonunda başarısız oldu.")
            raise last_err
        return wrapper
    return decorator


def get_exchange_rate(currency: str, year: int) -> float:
    """
    Belirtilen para birimi ve yıl için EUR dönüşüm oranını döndürür.
    
    Args:
        currency: Para birimi kodu (EUR, USD, GBP, TL, TRY)
        year: Yıl
        
    Returns:
        float: Dönüşüm oranı
    """
    if pd.isna(currency) or str(currency).strip() == "":
        return 0.0
    
    currency = str(currency).strip().upper()
    if currency not in ["EUR", "USD", "GBP", "TL", "TRY"]:
        return 0.0

    max_year = max(YEARLY_EXCHANGE_RATES.keys())
    target_year = year if year in YEARLY_EXCHANGE_RATES else max_year
    
    return YEARLY_EXCHANGE_RATES[target_year].get(currency, 0.0)


def calculate_delta(current: float, previous: float) -> float:
    """
    İki değer arasındaki yüzdesel değişimi hesaplar.
    
    Args:
        current: Güncel değer
        previous: Önceki değer
        
    Returns:
        float: Yüzdesel değişim
    """
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    
    return ((current - previous) / previous) * 100.0


def tr_upper(text: str) -> str:
    """
    Türkçe karakterleri doğru büyüten uppercase fonksiyonu.
    i -> İ, ı -> I dönüşümlerini yapar.
    """
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    trans_table = str.maketrans({
        "i": "İ", "ı": "I", "ğ": "Ğ", "ü": "Ü",
        "ş": "Ş", "ö": "Ö", "ç": "Ç", "I": "I", "İ": "İ"
    })
    
    return text.translate(trans_table).upper()


def tr_lower(text: str) -> str:
    """
    Türkçe karakterleri doğru küçülten lowercase fonksiyonu.
    İ -> i, I -> ı dönüşümlerini yapar.
    """
    if not isinstance(text, str):
        return str(text) if text is not None else ""
        
    trans_table = str.maketrans({
        "İ": "i", "I": "ı", "Ğ": "ğ", "Ü": "ü",
        "Ş": "ş", "Ö": "ö", "Ç": "ç"
    })
    
    return text.translate(trans_table).lower()


def clean_money_text(val: Union[str, float, int]) -> float:
    """
    Para değerini temizler ve float'a çevirir. 
    Hem TR (1.000,50) hem US (1,000.50) formatlarını akıllıca algılar.
    """
    if pd.isna(val): 
        return 0.0
    if isinstance(val, (int, float)): 
        return float(val)
    
    s = str(val).strip().split(' ')[0]
    if not s:
        return 0.0

    # Sadece rakam, nokta ve virgülleri tut
    s = "".join([c for c in s if c.isdigit() or c in ".,"])
    
    if not s:
        return 0.0

    # Hem nokta hem virgül varsa: Sonuncusu ondalıktır
    if "." in s and "," in s:
        dot_idx = s.rfind(".")
        comma_idx = s.rfind(",")
        if dot_idx > comma_idx: # US: 1,000.50
            s = s.replace(",", "").replace(".", ".") # Noktayı tut, virgülü sil
        else: # TR: 1.000,50
            s = s.replace(".", "").replace(",", ".") # Virgülü nokta yap, noktayı sil
    # Sadece virgül varsa: Kesinlikle ondalıktır (TR)
    elif "," in s:
        s = s.replace(",", ".")
    # Sadece nokta varsa: Eğer 3 basamaklı bir binlik ayıracı gibiyse (örn: 1.234) TR binliktir
    # Ancak 1.23 gibi bir durum varsa ondalıktır.
    elif "." in s:
        # Basit kural: Noktadan sonra tam 3 rakam varsa ve başka nokta yoksa binlik olabilir.
        # Ancak bu riskli. Genelde bu dashboard TR verisi beklediği için 
        # "1.000" -> 1000, "1.23" -> 1.23 mantığını koruyoruz.
        parts = s.split(".")
        if len(parts) == 2 and len(parts[1]) == 3:
            s = s.replace(".", "") # Binlik kabul et
        else:
            pass # Ondalık kalsın
            
    try: 
        return float(s)
    except: 
        return 0.0


def clean_money_series(series: pd.Series) -> pd.Series:
    """
    Pandas serisindeki para değerlerini vektörize (hızlı) şekilde temizler.
    """
    if series.empty:
        return series
        
    # Önce numeric olanları ayır (bozulmasınlar)
    # String'e çevir, boşlukları temizle, birimlerden (EUR, TL vb) kurtul
    s = series.astype(str).str.strip().str.split(" ").str[0]
    
    # Karakter temizliği (Hızlı regex)
    s = s.str.replace(r"[^0-9.,]", "", regex=True)
    
    # Boşları 0 yap
    s = s.replace("", "0")
    
    # Akıllı Dönüşüm (Vektörize regex/replace)
    # 1. Hem nokta hem virgül olanlar
    mask_both = s.str.contains(r"\.") & s.str.contains(r",")
    # TR: 1.000,50 -> noktayı sil, virgülü nokta yap
    # US: 1,000.50 -> virgülü sil, nokta kalsın
    # rfind mantığını vektörize etmek yerine basitleştirelim: 
    # Genelde TR verisi ağırlıklı olduğu için sonuncusu virgülse TR'dir.
    is_tr = s.str.match(r".*\..*,.*") # Nokta virgülden önceyse TR
    
    # İşlemleri uygula
    # TR formatı olanları ve sadece virgül içerenleri temizle
    s = s.where(~((mask_both & is_tr) | (~mask_both & s.str.contains(","))), s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False))
    # US formatı olanları temizle (virgülleri sil)
    s = s.where(~(mask_both & ~is_tr), s.str.replace(",", "", regex=False))
    
    # 2. Sadece nokta içerenlerde "binlik" kontrolü (örn: 1.234)
    mask_dot_only = ~s.str.contains(",") & s.str.contains(r"\.")
    # Noktadan sonra 3 hane varsa binliktir varsayıyoruz (1.000 -> 1000)
    # Not: 1.2345 gibi durumlarda ondalık kalsın.
    s = s.where(~(mask_dot_only & s.str.match(r"^\d+\.\d{3}$")), s.str.replace(".", "", regex=False))
    
    return pd.to_numeric(s, errors="coerce").fillna(0.0)


def clean_currency_code(val: Union[str, float]) -> Optional[str]:
    """Para birimi kodunu temizler. Geçersiz veya tanınmayan değerler için None döndürür."""
    if pd.isna(val):
        return None
    s = str(val).strip().upper()
    # Sadece tanınan para birimlerini kabul et
    VALID_CURRENCIES = {"EUR", "USD", "GBP", "TL", "TRY"}
    if s not in VALID_CURRENCIES:
        return None
    return s


def format_currency_eur(val: float) -> str:
    """Float değeri EUR formatında string'e çevirir."""
    if pd.isna(val): 
        return "€0"
    return f"€{val:,.0f}".replace(",", ".")


def get_theme_colors() -> dict:
    """
    Streamlit session state'e göre tema renklerini döndürür.
    Tüm view dosyalarında tutarlı tema kullanımı sağlar.
    
    Returns:
        dict: Tema renkleri içeren sözlük
    """
    try:
        import streamlit as st
        theme = st.session_state.get("theme", "light")
    except:
        theme = "light"
    
    is_dark = theme == "dark"
    
    if is_dark:
        return {
            "theme": "dark",
            "is_dark": True,
            "text_color": "#9CA3AF",
            "text_primary": "#F3F4F6",
            "text_secondary": "#9CA3AF",
            "grid_color": "rgba(255, 255, 255, 0.05)",
            "chart_color": "#60A5FA",
            "chart_bg": "rgba(59, 130, 246, 0.2)",
            "tooltip_bg": "rgba(0, 0, 0, 0.9)",
            "tooltip_text": "#fff",
            "bar_bg": "rgba(59, 130, 246, 0.2)",
            "bar_border": "#60A5FA",
            "badge_bg": "rgba(255, 255, 255, 0.05)",
            "badge_border": "rgba(255, 255, 255, 0.1)",
            "badge_text": "#F3F4F6",
        }
    else:
        return {
            "theme": "light",
            "is_dark": False,
            "text_color": "#6B7280",
            "text_primary": "#374151",
            "text_secondary": "#6B7280",
            "grid_color": "#E5E7EB",
            "chart_color": "#3B82F6",
            "chart_bg": "rgba(59, 130, 246, 0.1)",
            "tooltip_bg": "rgba(255, 255, 255, 0.95)",
            "tooltip_text": "#000",
            "bar_bg": "rgba(59, 130, 246, 0.7)",
            "bar_border": "#3B82F6",
            "badge_bg": "white",
            "badge_border": "#E5E7EB",
            "badge_text": "#374151",
        }
