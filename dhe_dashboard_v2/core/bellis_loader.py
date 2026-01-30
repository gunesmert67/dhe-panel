"""
DHE Dashboard - Bellis Data Loader
==================================
Bellis.xlsx ve şehir verilerini yükleyen modül.
"""
import pandas as pd
import streamlit as st
import logging
from typing import Dict, Tuple
import os

# Core Imports
from config.constants import EXCEL_CONFIG
from config.city_coordinates import CITY_COORDINATES
from core.gsheets import get_gspread_client, open_spreadsheet, safe_read_gsheet
from core.utils import tr_upper

logger = logging.getLogger(__name__)

# Google Sheets adı
GOOGLE_SHEETS_NAME = "DHE_Data"


def normalize_city_name(city: str) -> str:
    """
    Şehir adını normalize eder (büyük harf, Türkçe karakter uyumlu).
    Örn: "Mersin", "MERSİN", "mersın" -> "MERSİN"
    """
    if pd.isna(city) or city is None:
        return ""
    
    # String'e çevir ve boşlukları temizle
    city = str(city).strip()
    
    # Türkçe büyük harfe çevir
    city = tr_upper(city)
    
    # Bazı yaygın düzeltmeler
    corrections = {
        "KOCAELI": "KOCAELİ",
        "IZMIR": "İZMİR",
        "ISTANBUL": "İSTANBUL",
        "MERSIN": "MERSİN",
        "ELAZIG": "ELAZIĞ",
        "OSMANIYE": "OSMANİYE",
        "RIZE": "RİZE",
        "DIYARBAKIR": "DİYARBAKIR",
        "GAZIANTEP": "GAZİANTEP",
        "SANLIURFA": "ŞANLIURFA",
        "KAHRAMANMARAS": "KAHRAMANMARAŞ",
        "TEKIRDAG": "TEKİRDAĞ",
        "ESKISEHIR": "ESKİŞEHİR",
        "NEVSEHIR": "NEVŞEHİR",
        "KIRSEHIR": "KIRŞEHİR",
        "AFYON": "AFYONKARAHISAR",
    }
    
    return corrections.get(city, city)


@st.cache_data(show_spinner="Şehir verileri yükleniyor...")
def load_sehirler_data() -> pd.DataFrame:
    """
    Google Sheets'ten sehirler sheet'ini çeker.
    Kolonlar: Sehir_Ad, Bolge_Id, Bolge_Ad
    """
    try:
        client = get_gspread_client()
        spreadsheet = open_spreadsheet(client, GOOGLE_SHEETS_NAME)
        
        df = safe_read_gsheet(
            client,
            spreadsheet,
            sheet_name=EXCEL_CONFIG["SHEETS"]["SEHIRLER"],
            column_mapping=EXCEL_CONFIG["COLUMN_MAPPINGS"]["SEHIRLER"]
        )
        
        if not df.empty:
            # Şehir adını normalize et
            df["Sehir_Ad"] = df["Sehir_Ad"].apply(normalize_city_name)
            # Bölge ID'sini integer yap
            df["Bolge_Id"] = pd.to_numeric(df["Bolge_Id"], errors='coerce').fillna(0).astype(int)
            
            logger.info(f"[GSheets] sehirler: {len(df)} satır")
        
        return df
        
    except Exception as e:
        logger.error(f"Şehir verileri yüklenirken hata: {e}")
        return pd.DataFrame()


@st.cache_data(show_spinner="Bellis verileri yükleniyor...")
def load_bellis_data() -> pd.DataFrame:
    """
    Bellis.xlsx dosyasını okur ve işler.
    Excel yapısı: 6. satır başlıklar, 7. satır filtre, 8+ veri.
    """
    try:
        # Dosya yolunu belirle
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_path, "data", "Bellis.xlsx")
        
        if not os.path.exists(file_path):
            logger.error(f"Bellis.xlsx bulunamadı: {file_path}")
            return pd.DataFrame()
        
        # Excel'i oku (6. satır = header, 7. satır = skip)
        df = pd.read_excel(file_path, header=5, skiprows=[6])
        
        # Kolon isimlerini düzenle
        # Not: Excel'de hem "Machine Model" hem "Model" var, ikisini farklı isimlendirmeliyiz
        df = df.rename(columns={
            "Owner": "Musteri",
            "Lokasyon": "Sehir",
            "Who is servicing the machine?": "Servisci",
            "Machine Model": "Makine_Modeli",
            "Model": "Uretim_Yili",  # Model aslında üretim yılı
            "Serial No": "Seri_No",
            "Is the M/C still running?": "Calisiyor_mu",
            "Maintenance agreement with DHE": "DHE_Sozlesme",
            "Where do they buy Valves?": "Valf_Tedarik",
            "Where do they buy other spare parts?": "Parca_Tedarik"
        })
        
        # Sadece gerekli kolonları tut
        required_cols = ["Musteri", "Sehir", "Servisci", "Makine_Modeli", "Seri_No", "Calisiyor_mu"]
        available_cols = [c for c in required_cols if c in df.columns]
        df = df[available_cols].copy()
        
        # Boş satırları temizle
        df = df.dropna(subset=["Musteri", "Sehir"], how="all")
        
        # Şehir normalizasyonu
        df["Sehir"] = df["Sehir"].apply(normalize_city_name)
        
        # Servisci normalizasyonu
        df["Servisci"] = df["Servisci"].fillna("No information").astype(str).str.strip()
        
        # Koordinat eşleştirmesi
        df["Enlem"] = df["Sehir"].map(lambda x: CITY_COORDINATES.get(x, (None, None))[0])
        df["Boylam"] = df["Sehir"].map(lambda x: CITY_COORDINATES.get(x, (None, None))[1])
        
        # Türkiye içi mi kontrolü (koordinatı olanlar)
        df["Turkiye_Ici"] = df["Enlem"].notna()
        
        logger.info(f"[Bellis] Excel: {len(df)} makine ({df['Turkiye_Ici'].sum()} TR)")
        
        return df
        
    except Exception as e:
        logger.error(f"Bellis verileri yüklenirken hata: {e}")
        return pd.DataFrame()


def prepare_bellis_summary(df_bellis: pd.DataFrame, df_sehirler: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Bellis verisini bölge bilgisiyle zenginleştirir ve özet istatistikler hesaplar.
    
    Returns:
        Tuple[pd.DataFrame, Dict]: Zenginleştirilmiş DataFrame ve KPI dictionary
    """
    if df_bellis.empty:
        return df_bellis, {}
    
    # Şehir-Bölge eşleştirmesi
    # Şehir-Bölge eşleştirmesi
    if not df_sehirler.empty:
        # Gelen veri normalize edilmemiş olabilir (load_data'dan geliyorsa),
        # bu yüzden burada tekrar garantiye alıyoruz.
        df_sehirler = df_sehirler.copy()
        if "Sehir_Ad" in df_sehirler.columns:
            df_sehirler["Sehir_Ad"] = df_sehirler["Sehir_Ad"].apply(normalize_city_name)
        
        if "Bolge_Id" in df_sehirler.columns:
            df_sehirler["Bolge_Id"] = pd.to_numeric(df_sehirler["Bolge_Id"], errors='coerce').fillna(0).astype(int)

        sehir_bolge_map = df_sehirler.set_index("Sehir_Ad")[["Bolge_Id", "Bolge_Ad"]].to_dict("index")
        
        def get_bolge_info(sehir):
            info = sehir_bolge_map.get(sehir, {})
            return info.get("Bolge_Id", 0), info.get("Bolge_Ad", "Yurt Dışı")
        
        df_bellis[["Bolge_Id", "Bolge_Ad"]] = df_bellis["Sehir"].apply(
            lambda x: pd.Series(get_bolge_info(x))
        )
    else:
        df_bellis["Bolge_Id"] = 0
        df_bellis["Bolge_Ad"] = "Yurt Dışı"
    
    # Türkiye Kontrolü (Bölge ID'si varsa Türkiye'dir)
    # df_sehirler 81 ili içerdiği için, orada olmayanlar (Yurt Dışı) ID=0 olur.
    df_bellis["Is_Turkey"] = df_bellis["Bolge_Id"] > 0

    # KPI Hesaplamaları
    total_machines = len(df_bellis)
    dhe_machines = (df_bellis["Servisci"] == "DHE").sum()
    market_share = (dhe_machines / total_machines * 100) if total_machines > 0 else 0
    
    # Türkiye'deki Makine Sayısı
    is_turkey_count = df_bellis["Is_Turkey"].sum()

    # Servis dağılımı
    service_dist = df_bellis["Servisci"].value_counts().to_dict()
    
    # Bölge dağılımı
    region_dist = df_bellis.groupby("Bolge_Ad").size().to_dict()
    
    # Şehir bazlı özet (harita için)
    # DİKKAT: Haritada görünmesi için koordinatı olması yeterli ("Turkiye_Ici" flag'i coordinates.py'dan geliyor)
    # Yani Irak, Kıbrıs da burada olacak.
    city_summary = df_bellis[df_bellis["Turkiye_Ici"]].groupby("Sehir").agg(
        Toplam=("Musteri", "count"),
        DHE=("Servisci", lambda x: (x == "DHE").sum()),
        Enlem=("Enlem", "first"),
        Boylam=("Boylam", "first")
    ).reset_index()
    
    city_summary["DHE_Oran"] = (city_summary["DHE"] / city_summary["Toplam"] * 100).round(1)
    
    kpis = {
        "total": total_machines,
        "dhe": dhe_machines,
        "is_turkey": is_turkey_count, # Yeni KPI
        "market_share": round(market_share, 1),
        "service_distribution": service_dist,
        "region_distribution": region_dist,
        "city_summary": city_summary
    }
    
    return df_bellis, kpis
