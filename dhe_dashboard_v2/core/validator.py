"""
DHE Dashboard - Veri Doğrulama Modülü
=====================================
Excel/Google Sheets'ten gelen ham verilerin kalitesini kontrol eder.
Hatalı formatları (örn: Tarih yerine yazı, Tutar yerine metin) tespit eder.
"""
import pandas as pd
import logging
from typing import Tuple, List, Dict

logger = logging.getLogger(__name__)

def validate_dataframe(df: pd.DataFrame, required_columns: List[str], date_columns: List[str] = [], numeric_columns: List[str] = []) -> Tuple[bool, pd.DataFrame]:
    """
    DataFrame'in beklenen formata uygunluğunu kontrol eder.
    
    Args:
        df: Kontrol edilecek DataFrame
        required_columns: Boş olmaması gereken sütunlar
        date_columns: Tarih formatında olması gereken sütunlar
        numeric_columns: Sayısal olması gereken sütunlar
        
    Returns:
        (is_valid, error_report_df): 
        - is_valid: Veri seti kullanılabilir durumda mı?
        - error_report_df: Hatalı satırları içeren rapor
    """
    if df.empty:
        return True, pd.DataFrame()
    
    errors = []
    
    # 1. Zorunlu Alan Kontrolü
    for col in required_columns:
        if col in df.columns:
            # Boş veya sadece boşluk olanları bul
            invalid_rows = df[df[col].astype(str).str.strip() == ""].index
            if not invalid_rows.empty:
                for idx in invalid_rows:
                    errors.append({
                        "Satir_No": idx + 2, # Header + 1-index
                        "Sutun": col,
                        "Hata": "Zorunlu alan boş",
                        "Deger": "(Boş)"
                    })
        else:
            logger.warning(f"Validasyon uyarısı: '{col}' sütunu veri setinde bulunamadı.")

    # 2. Tarih Format Kontrolü
    for col in date_columns:
        if col in df.columns:
            # pd.to_datetime ile hatalı olanları coerce yapıp NaT olanları bulalım
            converted = pd.to_datetime(df[col], format='%d.%m.%Y', errors='coerce')
            
            # Orjinalde boş olmayıp, çevrim sonrası NaT olanlar hatalıdır
            # Not: Boş tarihleri zorunlu alan kontrolünde yakalıyoruz zaten, burası FORMAT kontrolü
            non_empty_mask = df[col].astype(str).str.strip() != ""
            invalid_mask = non_empty_mask & converted.isna()
            
            invalid_rows = df[invalid_mask].index
            if not invalid_rows.empty:
                 for idx in invalid_rows:
                    errors.append({
                        "Satir_No": idx + 2,
                        "Sutun": col,
                        "Hata": "Geçersiz tarih formatı (Beklenen: GG.AA.YYYY)",
                        "Deger": str(df.loc[idx, col])
                    })

    # 3. Sayısal Format Kontrolü (Tutar, Maliyet vb.)
    for col in numeric_columns:
        if col in df.columns:
            def is_clean_number(val):
                if pd.isna(val) or str(val).strip() == "":
                    return True # Boşlara sayısal kontrolü yapma (Zorunlu değilse)
                
                # Standart temizlik: "1.000,50 TL" -> "1000.50"
                s = str(val).strip().split(' ')[0].replace('.', '').replace(',', '.')
                s = "".join([c for c in s if c.isdigit() or c == '.'])
                try:
                    float(s)
                    return True
                except:
                    return False
            
            # Apply biraz yavaş olabilir ama veri seti küçük, güvenli okuma önemli
            mask = ~df[col].apply(is_clean_number)
            invalid_rows = df[mask].index
            
            if not invalid_rows.empty:
                for idx in invalid_rows:
                    errors.append({
                        "Satir_No": idx + 2,
                        "Sutun": col,
                        "Hata": "Sayısal değer bekleniyor",
                        "Deger": str(df.loc[idx, col])
                    })

    if errors:
        error_df = pd.DataFrame(errors)
        logger.warning(f"Veri validasyonunda {len(errors)} hata tespit edildi.")
        return False, error_df
    
    return True, pd.DataFrame()
