
import pandas as pd
import streamlit as st
from collections import Counter
from components.charts import render_chartjs, get_themed_chart_options
from config.constants import AY_MAP, COLORS

def render_field_charts(df_monthly: pd.DataFrame, df_cities: pd.DataFrame, year: int, selected_person: str = "Tümü", allowed_personnel: list = None):
    """
    Saha operasyonları için grafik setini render eder.
    Args:
        df_monthly: Aylık dağılım grafiği için
        df_cities: Şehir analizi için
        year: Seçili yıl
        selected_person: Seçili teknisyen ismi (veya "Tümü")
        allowed_personnel: Sadece bu listedeki kişilerin günlerini say (None ise hepsini say)
    """
    
    # ... (HTML Header aynı kalır, kodda gösterilmediği için buraya almıyorum, sadece gerekli yerler)
    from components.layout import section_title
    section_title("OPERASYONEL ANALİZ", margin_top="1rem", show_border=False)
    
    col1, col2 = st.columns(2, gap="medium")
    
    # --- GRAFİK 1: AYLIK SERVİS DAĞILIMI (Tüm aylar görünmeli) ---
    with col1:
        st.markdown(f"**{year} Yılı Aylık Servis Günü Dağılımı**", unsafe_allow_html=True)
        
        if df_monthly.empty or 'Ay' not in df_monthly.columns:
            st.info("Veri bulunamadı.")
        else:
            # Sadece AKTİF kayıtları ve Tarih verisi olanları baz al
            df_active = df_monthly[df_monthly['Durum'] == 'AKTİF'].copy() if 'Durum' in df_monthly.columns else df_monthly.copy()
            
            # Aylara göre "Adam-Gün" sayısını hesapla
            if 'Tarih' in df_active.columns and not df_active.empty:
                # 1. Teknisyen 1 için veriler
                t1_data = df_active[['Ay', 'Tarih', 'Teknisyen 1']].rename(columns={'Teknisyen 1': 'Teknisyen'})
                
                # 2. Teknisyen 2 için veriler (varsa)
                combined = t1_data
                if 'Teknisyen 2' in df_active.columns:
                    t2_data = df_active[['Ay', 'Tarih', 'Teknisyen 2']].rename(columns={'Teknisyen 2': 'Teknisyen'})
                    t2_data = t2_data[t2_data['Teknisyen'].notna() & (t2_data['Teknisyen'] != '')]
                    combined = pd.concat([t1_data, t2_data], ignore_index=True)
                
                # PERSONEL LİSTESİ FİLTRESİ (Saha Ekibi Kontrolü)
                if allowed_personnel:
                    combined = combined[combined['Teknisyen'].isin(allowed_personnel)]

                # KRİTİK DÜZELTME: Eğer tek bir kişi seçildiyse, SADECE onun günlerini saymalıyız.
                # Aksi takdirde yanındaki kişiyi de sayar (Örn: Enes seçiliyken, Enes+Ali işini 2 gün sayar).
                if selected_person and selected_person != "Tümü":
                    combined = combined[combined['Teknisyen'] == selected_person]

                # Her teknisyen-ay kombinasyonu için benzersiz tarih sayısını bul
                monthly_counts = combined.groupby(['Ay', 'Teknisyen'])['Tarih'].nunique().groupby('Ay').sum().sort_index()
            else:
                monthly_counts = pd.Series()
            
            # Tüm ayları (1-12) doldur
            labels = []
            data_points = []
            for i in range(1, 13):
                labels.append(AY_MAP.get(i, str(i)))
                data_points.append(int(monthly_counts.get(i, 0)))
            
            chart_data = {
                "labels": labels,
                "datasets": [{
                    "label": "Saha Günü Sayısı",
                    "data": data_points,
                    "backgroundColor": COLORS["INFO"],  # Mavi
                    "borderRadius": 4
                }]
            }
            
            options = get_themed_chart_options("bar")
            options["plugins"]["legend"]["display"] = False
            
            render_chartjs("bar", chart_data, options, height=300)

    # --- GRAFİK 2: ŞEHİR ANALİZİ (Seçili döneme göre) ---
    with col2:
        st.markdown(f"**En Çok Gidilen Şehirler**", unsafe_allow_html=True)
        
        if df_cities.empty or 'Şehir' not in df_cities.columns:
            st.info("Şehir verisi bulunamadı.")
        else:
            # Şehirleri temizle ve say
            cities_raw = df_cities['Şehir'].dropna().astype(str).tolist()
            # Basit temizlik (boşlukları al, büyük harf)
            cities = [c.strip().upper() for c in cities_raw if c.strip() != '']
            
            if not cities:
                st.info("Şehir verisi mevcut değil.")
            else:
                city_counts = Counter(cities).most_common(10) # İlk 10 şehir
                
                labels = [c[0] for c in city_counts]
                data_points = [c[1] for c in city_counts]
                
                chart_data = {
                    "labels": labels,
                    "datasets": [{
                        "label": "Ziyaret Sayısı",
                        "data": data_points,
                        "backgroundColor": COLORS["WARNING"], # Turuncu
                        "borderRadius": 4
                    }]
                }
                
                options = get_themed_chart_options("bar")
                options["indexAxis"] = 'y' # Yatay bar
                options["plugins"]["legend"]["display"] = False
                
                render_chartjs("bar", chart_data, options, height=300)
    
    st.markdown("---")
