"""
DHE Dashboard - Data Loader (Core)
==================================
Google Sheets veri kaynağı ile uygulama arasındaki köprü.
Verileri Google Sheets API üzerinden çeker -> core.gsheets ile
Verileri İşler -> core.transforms ile
Önbelleğe alır ve dağıtır -> load_data ile
"""
import pandas as pd
import streamlit as st
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Google Sheets API
import gspread

# Core Imports
from config.constants import PERSONEL_MAP, EXCEL_CONFIG, YEARS_TO_FETCH
from core.gsheets import get_gspread_client, open_spreadsheet, fetch_sheet_data, safe_read_gsheet
from core.transforms import process_finance_dataframe, prepare_crm_data, normalize_personel_name, determine_saha_status
from core.utils import tr_upper, clean_money_text, retry_on_exception
from core.validator import validate_dataframe

# Logger Yapılandırması
logger = logging.getLogger(__name__)

# Google Sheets Ayarları
GOOGLE_SHEETS_NAME = "DHE_Data"

@st.cache_data(show_spinner="Google Sheets'ten veri yükleniyor...")
def load_saha_data() -> pd.DataFrame:
    """
    Google Sheets'ten saha ekibi verilerini çeker.
    Dosya: "2025 SERVİS PROGRAMI"
    """
    try:
        client = get_gspread_client()
        
        # 1. Dosyayı aç
        sh = open_spreadsheet(client, "2025 SERVİS PROGRAMI")
        
        # 2. Tüm sekmeleri çek ve birleştir
        all_dfs = []
        sheets_to_fetch = YEARS_TO_FETCH
        
        for sheet_name in sheets_to_fetch:
            try:
                data = fetch_sheet_data(sh, sheet_name)
                if len(data) > 2:
                    headers = data[1]
                    rows = data[2:]
                    df_sheet = pd.DataFrame(rows, columns=headers)
                    all_dfs.append(df_sheet)
                    logger.info(f"[Saha] {sheet_name}: {len(df_sheet)} satır")
            except Exception as e:
                logger.warning(f"'{sheet_name}' sekmesi çekilirken hata (muhtemelen bulunamadı): {e}")
                continue
        
        if not all_dfs:
            return pd.DataFrame(), pd.DataFrame()
        
        # Birleştirme ve Temizlik
        cleaned_dfs = [df.loc[:, ~df.columns.duplicated()] for df in all_dfs]
        df = pd.concat(cleaned_dfs, ignore_index=True)
        
        # Boş sütunları temizle
        df = df.loc[:, df.columns.str.strip() != '']
        
        # Tarih temizliği
        if 'Tarih' in df.columns:
            df = df[df['Tarih'].str.strip() != ''].copy()
            df['Tarih'] = pd.to_datetime(df['Tarih'], dayfirst=True, errors='coerce')
            df['Ay'] = df['Tarih'].dt.month
            df['Yil'] = df['Tarih'].dt.year

        # Teknisyen İsimleri Normalize
        for col in ['Teknisyen 1', 'Teknisyen 2']:
            if col in df.columns:
                df[col] = df[col].apply(normalize_personel_name)

        if 'Teknisyen 1' in df.columns:
            df = df[df['Teknisyen 1'] != ''].copy()
        
        # Durum Belirleme
        df['Durum'] = df.apply(determine_saha_status, axis=1)
        
        logger.info(f"[Saha] Toplam: {len(df)} satır")
        
        # === 2. PERSONEL LİSTESİ ===
        try:
            sh_dhe = open_spreadsheet(client, GOOGLE_SHEETS_NAME) 
            target_sheet = EXCEL_CONFIG["SHEETS"].get("PERSONEL", "Personel")
            
            df_personel = safe_read_gsheet(
                client, 
                sh_dhe, 
                sheet_name=target_sheet,
                column_mapping=EXCEL_CONFIG["COLUMN_MAPPINGS"].get("PERSONEL")
            )
            
            if not df_personel.empty:
                df_personel["Ad_Soyad"] = df_personel["Ad_Soyad"].apply(normalize_personel_name)
                df_personel = df_personel[df_personel["Ad_Soyad"] != ""]
                
                for date_col in ["Ise_Giris", "Isten_Cikis"]:
                    if date_col in df_personel.columns:
                        df_personel[date_col] = pd.to_datetime(df_personel[date_col], dayfirst=True, errors='coerce')

                if "Departman" in df_personel.columns:
                    df_personel["Departman"] = df_personel["Departman"].astype(str).str.strip().str.title()
            
        except Exception as e:
            logger.warning(f"Personel listesi yüklenemedi: {e}")
            df_personel = pd.DataFrame()
            
        return df, df_personel
        
    except Exception as e:
        logger.error(f"Saha verileri yüklenirken hata: {e}")
        return pd.DataFrame(), pd.DataFrame()


def get_monthly_rates_map_gsheet(spreadsheet) -> Dict[tuple, float]:
    """Google Sheets'ten aylık kur tablosunu okur."""
    rates_map = {}
    try:
        sheet_name = EXCEL_CONFIG["SHEETS"]["KURLAR"]
        data = fetch_sheet_data(spreadsheet, sheet_name)
        
        if len(data) < 2:
            return rates_map
            
        logger.info(f"[GSheets] {sheet_name}: {len(data)-1} satır")
        
        headers = [str(c).lower().strip() for c in data[0]]
        rows = data[1:]
        df_kurlar = pd.DataFrame(rows, columns=headers)
        
        # Basit kolon normalizasyonu
        def normalize_col(col):
            col = col.lower().strip()
            col = col.replace('ı', 'i').replace('İ', 'i').replace('ş', 's').replace('ğ', 'g')
            return col
        
        df_kurlar.columns = [normalize_col(c) for c in df_kurlar.columns]
        df_kurlar = df_kurlar.rename(columns={'year': 'yil', 'month': 'ay'})
        
        for _, row in df_kurlar.iterrows():
            try:
                # , -> . dönüşümü ve float parsing
                def parse(v): return float(str(v).replace(',', '.')) if v else 1.0
                
                yil = int(parse(row.get('yil', 0)))
                ay = int(parse(row.get('ay', 0)))
                
                if yil > 0 and ay > 0:
                    rates_map[(yil, ay, 'EUR')] = parse(row.get('eur'))
                    rates_map[(yil, ay, 'USD')] = parse(row.get('usd'))
                    rates_map[(yil, ay, 'GBP')] = parse(row.get('gbp'))
                    rates_map[(yil, ay, 'TL')] = parse(row.get('tl'))
                    rates_map[(yil, ay, 'TRY')] = parse(row.get('tl'))
            except:
                continue
    except Exception as e:
        logger.warning(f"Kurlar okunamadı: {e}")
    
    return rates_map


@st.cache_data(show_spinner=False)
def load_data(_progress_callback=None) -> Dict[str, pd.DataFrame]:
    """Tüm verileri yükleyen ana fonksiyon (İKİ AŞAMALI PARALEL Veri Çekme)."""
    try:
        import concurrent.futures
        
        if _progress_callback: _progress_callback(0.05, "Bağlantı kuruluyor...")
        
        client = get_gspread_client()
        
        # İki farklı spreadsheet
        spreadsheet_dhe = open_spreadsheet(client, GOOGLE_SHEETS_NAME)
        spreadsheet_saha = open_spreadsheet(client, "2025 SERVİS PROGRAMI")
        
        results = {}
        
        # =====================================================================
        # AŞAMA 1: DHE_Data Sheetleri (8 adet) - PARALEL
        # =====================================================================
        if _progress_callback: _progress_callback(0.10, "DHE_Data okunuyor (8 Sheet Paralel)...")
        
        dhe_tasks = {
            "teklif": (EXCEL_CONFIG["SHEETS"]["TEKLIF"], EXCEL_CONFIG["COLUMN_MAPPINGS"]["TEKLIF"]),
            "siparis": (EXCEL_CONFIG["SHEETS"]["SIPARIS"], EXCEL_CONFIG["COLUMN_MAPPINGS"]["SIPARIS"]),
            "musteri": (EXCEL_CONFIG["SHEETS"]["MUSTERI"], EXCEL_CONFIG["COLUMN_MAPPINGS"]["MUSTERI"]),
            "urun": (EXCEL_CONFIG["SHEETS"]["URUN"], EXCEL_CONFIG["COLUMN_MAPPINGS"]["URUN"]),
            "tatiller": (EXCEL_CONFIG["SHEETS"].get("TATILLER", "Tatiller"), EXCEL_CONFIG["COLUMN_MAPPINGS"].get("TATILLER")),
            "kurlar": (EXCEL_CONFIG["SHEETS"].get("KURLAR", "kurlar"), None),
            "personel": (EXCEL_CONFIG["SHEETS"].get("PERSONEL", "Personel"), EXCEL_CONFIG["COLUMN_MAPPINGS"].get("PERSONEL")),
            "sehirler": (EXCEL_CONFIG["SHEETS"].get("SEHIRLER", "sehirler"), EXCEL_CONFIG["COLUMN_MAPPINGS"].get("SEHIRLER")),
        }
        
        def fetch_dhe(key, sheet_name, mapping):
            try:
                if mapping:
                    return key, safe_read_gsheet(client, spreadsheet_dhe, sheet_name, mapping)
                else:
                    data = fetch_sheet_data(spreadsheet_dhe, sheet_name)
                    if len(data) > 1:
                        return key, pd.DataFrame(data[1:], columns=data[0])
                    return key, pd.DataFrame()
            except Exception as e:
                logger.warning(f"DHE çekme hatası ({key}): {e}")
                return key, pd.DataFrame()

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(fetch_dhe, k, v[0], v[1]): k for k, v in dhe_tasks.items()}
            for future in concurrent.futures.as_completed(futures):
                key, df = future.result()
                results[key] = df
                logger.info(f"[DHE] {key}: {len(df)} satır")
        
        # =====================================================================
        # AŞAMA 2: Servis Programı Sheetleri (3 adet) - PARALEL
        # =====================================================================
        if _progress_callback: _progress_callback(0.40, "Servis Programı okunuyor (3 Sheet Paralel)...")
        
        saha_years = ["2024", "2025", "2026"]
        
        def fetch_saha(year):
            try:
                data = fetch_sheet_data(spreadsheet_saha, year)
                if len(data) > 2:
                    # Saha verileri için header 2. satırda
                    headers = data[1]
                    rows = data[2:]
                    logger.info(f"[Saha] {year}: {len(rows)} satır")
                    return year, pd.DataFrame(rows, columns=headers)
                return year, pd.DataFrame()
            except Exception as e:
                logger.warning(f"Saha çekme hatası ({year}): {e}")
                return year, pd.DataFrame()

        saha_results = {}
        # Rate limit önlemek için sıralı (workers=1) -> Kullanıcı isteği ile PARALEL (3)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(fetch_saha, year): year for year in saha_years}
            for future in concurrent.futures.as_completed(futures):
                year, df = future.result()
                saha_results[year] = df
        
        if _progress_callback: _progress_callback(0.60, "Veriler işleniyor...")
        
        # =====================================================================
        # SONUÇLARI AL
        # =====================================================================
        df_raw_teklif = results.get("teklif", pd.DataFrame())
        df_raw_siparis = results.get("siparis", pd.DataFrame())
        df_raw_musteri = results.get("musteri", pd.DataFrame())
        df_urun = results.get("urun", pd.DataFrame())
        df_holidays = results.get("tatiller", pd.DataFrame())
        df_kurlar = results.get("kurlar", pd.DataFrame())
        df_personel = results.get("personel", pd.DataFrame())
        df_sehirler = results.get("sehirler", pd.DataFrame())
        
        # Saha verilerini birleştir (saha_results dict'inden)
        saha_dfs = []
        for year in ["2024", "2025", "2026"]:
            df_year = saha_results.get(year, pd.DataFrame())
            if not df_year.empty:
                saha_dfs.append(df_year)
        
        # =====================================================================
        # KURLAR İŞLEME (Column name normalization)
        # =====================================================================
        monthly_rates = {}
        if not df_kurlar.empty:
            # Sütun isimlerini normalize et (küçük harf, boşluk trim)
            df_kurlar.columns = df_kurlar.columns.str.strip().str.lower()
            
            for _, row in df_kurlar.iterrows():
                try:
                    def parse(v): return float(str(v).replace(',', '.').replace(' ', '')) if v and str(v).strip() else 1.0
                    
                    # Farklı sütun ismi varyasyonlarını dene
                    yil_val = row.get('yil') or row.get('yıl') or row.get('year') or 0
                    ay_val = row.get('ay') or row.get('month') or 0
                    
                    yil = int(parse(yil_val))
                    ay = int(parse(ay_val))
                    
                    if yil > 0 and ay > 0:
                        monthly_rates[(yil, ay, 'EUR')] = parse(row.get('eur') or row.get('euro') or 1)
                        monthly_rates[(yil, ay, 'USD')] = parse(row.get('usd') or row.get('dolar') or 1)
                        monthly_rates[(yil, ay, 'GBP')] = parse(row.get('gbp') or row.get('sterlin') or 1)
                        monthly_rates[(yil, ay, 'TL')] = parse(row.get('tl') or row.get('try') or 1)
                        monthly_rates[(yil, ay, 'TRY')] = parse(row.get('tl') or row.get('try') or 1)
                except:
                    continue
        
        # Tatiller
        holidays = set()
        if not df_holidays.empty and 'Tarih' in df_holidays.columns:
             dates = pd.to_datetime(df_holidays['Tarih'], dayfirst=True, errors='coerce').dt.date.dropna()
             holidays = set(dates.tolist())
        
        # Ürünler
        if not df_urun.empty:
             df_urun["Musteri"] = df_urun["Musteri"].astype(str).str.strip().str.upper()

        if _progress_callback: _progress_callback(0.80, "Finansal veriler işleniyor...")

        # =====================================================================
        # FİNANSAL İŞLEME
        # =====================================================================
        df_teklif_processed = process_finance_dataframe(df_raw_teklif, "Teklif_No", monthly_rates, PERSONEL_MAP)
        df_teklif_processed = df_teklif_processed[df_teklif_processed["Tutar_EUR"] != 0]

        df_siparis_processed = process_finance_dataframe(df_raw_siparis, "Siparis_No", monthly_rates, PERSONEL_MAP)
        df_siparis_processed = df_siparis_processed[df_siparis_processed["Tutar_EUR"] != 0]
        
        # Müşteri Temizliği
        df_raw_musteri["Sorumlu_Clean"] = df_raw_musteri["Sorumlu"].apply(
            lambda x: "BOŞ / SAHİPSİZ" if pd.isna(x) or str(x).strip() == "" else tr_upper(str(x).strip())
        )
        
        # Teklif/Sipariş Ayrımı
        siparis_ids = set(df_siparis_processed["Siparis_No"].unique())
        df_teklif_acik = df_teklif_processed[~df_teklif_processed["Teklif_No"].isin(siparis_ids)].copy()
        df_teklif_acik["Durum"] = "Teklif"
        
        df_siparis_final = df_siparis_processed.copy()
        df_siparis_final["Durum"] = "Sipariş"
        df_siparis_final["Teklif_No"] = df_siparis_final["Siparis_No"]
        
        # CRM
        df_crm = prepare_crm_data(df_teklif_processed, df_siparis_final, df_raw_musteri)
        
        # =====================================================================
        # SAHA VERİSİ İŞLEME (Daha önce load_saha_data'daydı)
        # =====================================================================
        df_saha = pd.DataFrame()
        df_saha_personel = pd.DataFrame()
        
        if saha_dfs:
            # Birleştirme ve Temizlik
            cleaned_dfs = [df.loc[:, ~df.columns.duplicated()] for df in saha_dfs]
            df_saha = pd.concat(cleaned_dfs, ignore_index=True)
            
            # Boş sütunları temizle
            df_saha = df_saha.loc[:, df_saha.columns.str.strip() != '']
            
            # Tarih temizliği
            if 'Tarih' in df_saha.columns:
                df_saha = df_saha[df_saha['Tarih'].astype(str).str.strip() != ''].copy()
                df_saha['Tarih'] = pd.to_datetime(df_saha['Tarih'], dayfirst=True, errors='coerce')
                df_saha['Ay'] = df_saha['Tarih'].dt.month
                df_saha['Yil'] = df_saha['Tarih'].dt.year

            # Teknisyen İsimleri Normalize
            for col in ['Teknisyen 1', 'Teknisyen 2']:
                if col in df_saha.columns:
                    df_saha[col] = df_saha[col].apply(normalize_personel_name)

            if 'Teknisyen 1' in df_saha.columns:
                df_saha = df_saha[df_saha['Teknisyen 1'] != ''].copy()
            
            # Durum Belirleme
            df_saha['Durum'] = df_saha.apply(determine_saha_status, axis=1)
            
            # Personel (Paralel çekildi, burada kullanılıyor)
            df_saha_personel = df_personel
        
        logger.info(f"[load_data] Tüm veriler yüklendi - Paralel 11 sheet")
        
        return {
            "teklif": df_teklif_acik,
            "siparis": df_siparis_final,
            "musteri": df_raw_musteri,
            "all_quotes": df_teklif_processed,
            "crm": df_crm,
            "urun": df_urun,
            "holidays": holidays,
            "saha": df_saha,
            "saha_personel": df_saha_personel,
            "sehirler": df_sehirler,
        }
        
    except Exception as e:
        logger.exception("Veri yükleme hatası")
        st.error(f"Kritik hata: {e}")
        return {}


@st.cache_data(show_spinner=False)
def load_holidays() -> set:
    """Sadece tatilleri yükleyen helper."""
    # ... (Önceki load_holidays mantığı, ama yeni safe_read_gsheet kullanarak) ...
    # Kısa olması için burada tekrar spreadsheet açmaya gerek yok aslında ama
    # Bağımsız çağrılabilir olması isteniyorsa:
    try:
        client = get_gspread_client()
        sh = open_spreadsheet(client, GOOGLE_SHEETS_NAME)
        target = EXCEL_CONFIG["SHEETS"].get("TATILLER", "Tatiller")
        df = safe_read_gsheet(client, sh, target, EXCEL_CONFIG["COLUMN_MAPPINGS"].get("TATILLER"))
        if not df.empty and 'Tarih' in df.columns:
             return set(pd.to_datetime(df['Tarih'], dayfirst=True, errors='coerce').dt.date.dropna().tolist())
    except:
        pass
    return set()
