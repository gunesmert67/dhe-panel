
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, Any
from core.utils import clean_currency_code, get_exchange_rate, tr_upper, clean_money_text, clean_money_series

logger = logging.getLogger(__name__)

def process_finance_dataframe(df: pd.DataFrame, id_col: str, monthly_rates: Dict, personel_dict: Dict) -> pd.DataFrame:
    """
    Teklif ve Sipariş DataFrameleri için ortak işleme mantığı.
    Para birimi dönüştürme, tarih ayrıştırma ve hesaplamaları yapar.
    """
    if df.empty:
        return df

    # ID Temizliği
    df[id_col] = df[id_col].astype(str).str.strip()
    
    # Para Birimi Temizliği
    df["Para_Birimi"] = df["Para_Birimi"].apply(clean_currency_code)
    df = df.dropna(subset=["Para_Birimi"]).copy()
    
    # Tarih İşlemleri (Standart format: DD.MM.YYYY - örn: 02.01.2017)
    df["Tarih"] = pd.to_datetime(df["Tarih"], format='%d.%m.%Y', errors='coerce')
    df = df.dropna(subset=["Tarih"]).copy()
    
    df["Yil"] = df["Tarih"].dt.year
    df["Ay"] = df["Tarih"].dt.month
    df["Ay_Sira"] = df["Ay"]
    
    # Tutar Temizliği (1.000,50 formatı) - VEKTÖRIZE
    df["Tutar_Ham"] = clean_money_series(df["Tutar_Ham"])
    df["Maliyet_Ham"] = clean_money_series(df["Maliyet_Ham"])
    
    # Kur Çevrimi Helper
    def get_rate(yil, ay, pb):
        # 1. Aylık tabloya bak
        rate = monthly_rates.get((yil, ay, pb))
        if rate is not None:
            return rate
        # 2. Yıllık ortalamaya bak (fallback)
        return get_exchange_rate(pb, yil)
    
    # Kur Hesaplama
    unique_combinations = df[["Yil", "Ay", "Para_Birimi"]].drop_duplicates()
    rates_map = {}
    for _, row in unique_combinations.iterrows():
        rates_map[(row["Yil"], row["Ay"], row["Para_Birimi"])] = get_rate(row["Yil"], row["Ay"], row["Para_Birimi"])
    
    df["_Rate_Key"] = list(zip(df["Yil"], df["Ay"], df["Para_Birimi"]))
    df["Exchange_Rate"] = df["_Rate_Key"].map(rates_map).fillna(1.0)
    
    # EUR Dönüşümleri
    df["Tutar_EUR"] = df["Tutar_Ham"] * df["Exchange_Rate"]
    df["Maliyet_EUR"] = df["Maliyet_Ham"] * df["Exchange_Rate"]
    df["Kar_EUR"] = df["Tutar_EUR"] - df["Maliyet_EUR"]
    
    df.drop(columns=["_Rate_Key", "Exchange_Rate"], inplace=True)
    
    # Personel Eşleştirme
    df["Personel_Kodu"] = df["Personel"].astype(str).str.strip().apply(tr_upper)
    df["Personel_Adi"] = df["Personel_Kodu"].map(personel_dict).fillna(df["Personel_Kodu"])
    
    return df


def prepare_crm_data(df_teklif: pd.DataFrame, df_siparis: pd.DataFrame, df_musteri: pd.DataFrame) -> pd.DataFrame:
    """CRM modülü için müşteri segmentasyonu ve metrik analizleri."""
    try:
        # ÖNEMLİ: CRM Analizinde "Toplam Teklif Hacmi" hesaplanırken, 
        # aynı teklifin 5 revizyonunu alt alta toplarsak müşterinin hacmi şişer.
        # Bu yüzden önce "Net" teklif listesini çıkarıp onun üzerinden ciro/hacim hesabı yapmalıyız.
        df_teklif_unique = filter_latest_revisions(df_teklif, "Teklif_No")
        df_siparis_unique = filter_latest_revisions(df_siparis, "Siparis_No")

        # Sipariş Özeti
        cust_sip = df_siparis_unique.groupby("Musteri").agg(
            Total_Ciro_EUR=('Tutar_EUR', 'sum'),
            Siparis_Adedi=('Siparis_No', 'nunique'),
            Son_Siparis_Tarihi=('Tarih', 'max'),
            Ilk_Siparis_Tarihi=('Tarih', 'min'),
        ).reset_index()
        
        # Sıklık Hesabı
        cust_sip["Gun_Farki"] = (cust_sip["Son_Siparis_Tarihi"] - cust_sip["Ilk_Siparis_Tarihi"]).dt.days
        # Eğer birden fazla sipariş varsa, (Son-İlk) / (Adet-1)
        cust_sip["Purchase_Frequency"] = cust_sip.apply(
            lambda x: x["Gun_Farki"] / (x["Siparis_Adedi"] - 1) if x["Siparis_Adedi"] > 1 else 0, axis=1
        )
        
        # Teklif Özeti
        # Son Teklif Detayları
        last_quotes = df_teklif_unique.sort_values("Tarih").drop_duplicates("Musteri", keep="last")
        last_quotes = last_quotes[["Musteri", "Teklif_No", "Tutar_EUR"]].rename(
            columns={
                "Teklif_No": "Son_Teklif_No",
                "Tutar_EUR": "Son_Teklif_Tutar"
            }
        )

        cust_teklif = df_teklif_unique.groupby("Musteri").agg(
            Total_Teklif_EUR=('Tutar_EUR', 'sum'),
            Teklif_Sayisi=('Teklif_No', 'nunique'),
            Son_Teklif_Tarihi=('Tarih', 'max'),
            Ilk_Teklif_Tarihi=('Tarih', 'min')
        ).reset_index()
        
        # Detayları birleştir
        cust_teklif = pd.merge(cust_teklif, last_quotes, on="Musteri", how="left")
        
        # Ana Müşteri Listesi Oluşturma
        if df_musteri.empty:
            all_customers = pd.DataFrame(cust_sip["Musteri"].unique(), columns=["Musteri"])
            all_customers["Uzun_Ad"] = all_customers["Musteri"]
            all_customers["Sorumlu_Clean"] = "Genel"
        else:
            all_customers = df_musteri[['Kisa_Ad', 'Uzun_Ad', 'Sorumlu_Clean']].rename(columns={'Kisa_Ad': 'Musteri'})
            
        # 3 Tabloyu Birleştirme
        df_crm = pd.merge(all_customers, cust_sip, on="Musteri", how="left")
        df_crm = pd.merge(df_crm, cust_teklif, on="Musteri", how="left")
        
        # NaN Doldurma
        df_crm["Total_Teklif_EUR"] = df_crm["Total_Teklif_EUR"].fillna(0)
        df_crm["Total_Ciro_EUR"] = df_crm["Total_Ciro_EUR"].fillna(0)
        df_crm["Siparis_Adedi"] = df_crm["Siparis_Adedi"].fillna(0)
        df_crm["Teklif_Sayisi"] = df_crm["Teklif_Sayisi"].fillna(0)
        
        # Pareto Analizi
        df_crm = df_crm.sort_values("Total_Teklif_EUR", ascending=False)
        total_quote_vol = df_crm["Total_Teklif_EUR"].sum()
        df_crm["Cum_Quote"] = df_crm["Total_Teklif_EUR"].cumsum()
        df_crm["Revenue_Share"] = df_crm["Cum_Quote"] / total_quote_vol if total_quote_vol > 0 else 0
        
        # Segmentasyon Kuralları
        def assign_segment(row):
            if row["Total_Teklif_EUR"] == 0:
                return "Pasif"
            elif row["Revenue_Share"] <= 0.80:
                return "🥇 VIP"
            elif row["Revenue_Share"] <= 0.95:
                return "🥈 Gold"
            else:
                return "🥉 Standart"
                
        df_crm["Segment"] = df_crm.apply(assign_segment, axis=1)
        
        # Recency
        now = datetime.now()
        df_crm["Recency_Days"] = (now - df_crm["Son_Teklif_Tarihi"]).dt.days.fillna(9999).astype(int)
        
        # Risk Analizi
        def check_risk(row):
            return "VIP" in row["Segment"] and row["Recency_Days"] > 90
            
        df_crm["Riskli"] = df_crm.apply(check_risk, axis=1)

        return df_crm
        
    except Exception as e:
        logger.error(f"CRM veri hazırlama hatası: {e}")
        return pd.DataFrame()

def normalize_personel_name(name):
    """Saha personeli adı normalizasyonu."""
    if pd.isna(name) or name is None:
        return ""
    # String'e çevir, boşlukları temizle, tr_upper ile çevir
    s = tr_upper(str(name).strip())
    # Çift boşlukları tek boşluğa indir
    s = " ".join(s.split())
    if s == "NAN":
        return ""
    return s

def determine_saha_status(row):
    """Saha takip durumu belirleme iş kuralı."""
    try:
        def safe_str(val):
            if val is None or pd.isna(val):
                return ''
            s = str(val).strip()
            if s.lower() == 'nan':
                return ''
            return s

        teknisyen1 = safe_str(row.get('Teknisyen 1', ''))
        teknisyen2 = safe_str(row.get('Teknisyen 2', ''))
        musteri = tr_upper(safe_str(row.get('Müşteri', '')))
        servis_urunu = safe_str(row.get('Servis Ürünü', ''))
        sorumlu = safe_str(row.get('Sorumlu', ''))
        
        # Atölye/Pasif kontrolü: DHE Endüstriyel ise
        if 'DHE ENDÜSTRİYEL' in musteri:
            # Hafta sonu kontrolü (Mesai sayılması için AKTİF dönmeli)
            tarih = row.get('Tarih')
            is_weekend = False
            
            if pd.notna(tarih):
                # Eğer Timestamp değilse dönüştür
                if not isinstance(tarih, (pd.Timestamp, datetime)):
                    try: 
                        tarih = pd.to_datetime(tarih, dayfirst=True)
                    except: 
                        pass
                
                if hasattr(tarih, 'dayofweek'):
                    is_weekend = tarih.dayofweek >= 5
            
            if is_weekend:
                return 'AKTİF'
            else:
                return 'ATÖLYE'

        # İzinli kontrolü
        if musteri == 'İZİNLİ':
            return 'İZİNLİ'
        
        # Aktif kontrolü
        has_technician = teknisyen1 != '' or teknisyen2 != ''
        has_work_info = musteri != '' or servis_urunu != '' or sorumlu != ''
        
        if has_technician and has_work_info:
            return 'AKTİF'
        else:
            return 'ATÖLYE'
    except Exception:
        return 'ATÖLYE'

import re

def filter_latest_revisions(df: pd.DataFrame, col_name: str = "Teklif_No") -> pd.DataFrame:
    """
    Teklif numaralarındaki revizyonları (R1, R2 vb.) analiz eder ve 
    aynı kök numaraya sahip tekliflerden sadece en sonuncusunu tutar.
    
    Örnek:
    100, 100R1, 100R2 -> Sadece 100R2 kalır.
    """
    if df.empty or col_name not in df.columns:
        return df
        
    # İşlem yapmak için geçici bir kopya al
    df_temp = df.copy()
    
    # 1. Temizlik ve Hazırlık
    # String'e çevir ve boşlukları temizle
    df_temp["_temp_no"] = df_temp[col_name].astype(str).str.strip().str.upper()
    
    # Boş olanları eleme (Orijinal veride kalmalı mı? Genelde boş teklif no olmaz ama varsa da filtrelemeye gerek yok)
    # Ancak revizyon analizi için boş olmayanlar lazım.
    
    def parse_revision(val):
        """
        Teklif numarasını (Kök, Revizyon) olarak ayırır.
        Dönüş: (Kök_String, Revizyon_Int)
        """
        if not val:
            return (val, -1)
            
        # Regex: Başta rakamlar, sonra opsiyonel R ve rakamlar
        # Örnek Pattern: ^(\d+)(?:R(\d+))?$
        # Ancak bazen arada boşluk veya tire olabilir, basit tutalım.
        # Genelde format: 1234, 1234R1, 1234-R1, 1234 R1
        
        # En basit mantık: Sondaki R ve sayıları bulmak.
        match = re.search(r'^(.*?)[\s\-]*(?:R|REV)(\d+)$', val)
        if match:
            root = match.group(1).strip() # R öncesi
            rev = int(match.group(2))     # R sonrası sayı
            # Eğer root boşsa (Örn: R1 diye veri varsa), olduğu gibi kalsın
            if not root: 
                return (val, 0)
            return (root, rev)
        
        # Eğer R formatı yoksa, direkt kendisi köktür, revizyon 0'dır.
        # Ama şuna dikkat: 100A, 100B gibi formatlar varsa?
        # Kullanıcı R1 R2 dediği için sadece R'ye odaklanıyoruz.
        return (val, 0)

    # Apply parse
    # Hız için bu işlemi vektörize edebiliriz ama regex karmaşık. Apply ile yapalım.
    parsed_data = df_temp["_temp_no"].apply(parse_revision)
    
    df_temp["_root_no"] = [x[0] for x in parsed_data]
    df_temp["_rev_no"] = [x[1] for x in parsed_data]
    
    # 2. Sıralama: Kök'e göre ve Revizyon (Büyükten küçüğe)
    # Böylece her grubun en üstünde en son revizyon olacak.
    df_temp = df_temp.sort_values(by=["_root_no", "_rev_no"], ascending=[True, False])
    
    # 3. Tekilleştirme (Keep First = En yüksek revizyon)
    df_filtered = df_temp.drop_duplicates(subset=["_root_no"], keep="first")
    
    # Geçici kolonları temizle
    cols_to_drop = ["_temp_no", "_root_no", "_rev_no"]
    df_filtered = df_filtered.drop(columns=cols_to_drop)
    
    # Sıralamayı (Tarihe göre) tekrar eski haline getirmek gerekebilir ama 
    # genelde dashboard'da zaten tarihe göre sıralanıyor.
    # O yüzden orijinal df'den index ile filtrelemek daha güvenli olabilir.
    
    return df.loc[df_filtered.index].copy()

