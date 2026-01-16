"""
Saha Ekibi (Field Operations) Views
====================================
Google Sheets'ten çekilen canlı servis verilerini görselleştirir.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
from config.constants import AY_MAP, FIELD_TECHNICIANS
from components.layout import spacer, section_title
from core.data_loader import load_saha_data, load_holidays
from core.date_utils import get_weekday_count, calculate_effective_workdays
from components.field_stats import render_daily_tracking, render_period_stats
from components.field_tables import render_technician_performance_table, render_other_workers_table
from components.field_charts import render_field_charts

def render_saha(holidays=None):
    # DHE Saha Operasyonları Görünümü
    # Verileri Yükle
    df_raw = load_saha_data()
    
    # Unpack
    if isinstance(df_raw, tuple):
        df_raw, df_personel = df_raw
    else: 
        df_personel = pd.DataFrame() 
    
    if holidays is None:
        holidays = load_holidays()
        
    if df_raw.empty:
        st.error("❌ Google Sheets'ten veri çekilemedi. Lütfen bağlantıyı kontrol edin.")
        return
    
    # === PERSONEL LİSTESİ HAZIRLIĞI ===
    saha_listesi = set()
    today = datetime.now().date()
    
    if not df_personel.empty and 'Ad_Soyad' in df_personel.columns:
        saha_filt = df_personel['Departman'].str.strip().str.upper() == 'SAHA'
        if 'Isten_Cikis' in df_personel.columns:
             query_date = pd.Timestamp(today)
             active_filt = (df_personel['Isten_Cikis'].isnull()) | (df_personel['Isten_Cikis'] >= query_date)
             saha_filt = saha_filt & active_filt
        saha_listesi = set(df_personel[saha_filt]['Ad_Soyad'].str.upper().tolist())
    
    if not saha_listesi:
        saha_listesi = set([t.upper() for t in FIELD_TECHNICIANS])

    # === STYLE INJECTION ===
    st.markdown("""
        <style>
        [data-testid="stDataFrame"] table tr th, [data-testid="stDataFrame"] table tr td {
            padding-top: 0.8rem;
            padding-bottom: 0.8rem;
        }
        
        /* TAB STYLING */
        div[data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
            padding: 10px 0;
            border-bottom: none;
        }

        button[data-baseweb="tab"] {
            background-color: var(--bg-secondary, #F3F4F6) !important;
            border: 1px solid var(--border-color, #E5E7EB) !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            color: var(--text-secondary, #6B7280) !important;
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out !important;
            flex: 1; /* Tabs expand to fill width */
        }

        /* Hover Effect */
        button[data-baseweb="tab"]:hover {
            background-color: var(--card-bg, #FFFFFF) !important;
            border-color: #C4121F !important;
            color: #C4121F !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }

        /* Active Tab */
        button[data-baseweb="tab"][aria-selected="true"] {
            background-color: #C4121F !important; /* DHE Red */
            color: white !important;
            border-color: #C4121F !important;
            box-shadow: 0 4px 6px -1px rgba(196, 18, 31, 0.3);
        }
        
        /* Remove default top line */
        div[data-baseweb="tab-highlight"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # === TAB YAPISI ===
    tab_gunluk, tab_performans = st.tabs([f"GÜNLÜK TAKİP ({today.strftime('%d.%m.%Y')})", "TEKNİSYEN PERFORMANSI"])

    # === TAB 1: GÜNLÜK TAKİP ===
    with tab_gunluk:
        spacer(15)
        render_daily_tracking(df_raw, df_personel, all_technicians=saha_listesi)

    # === TAB 2: TEKNİSYEN PERFORMANSI ===
    with tab_performans:
        spacer(15)
        
        # === FİLTRELER (3 Yan Yana) ===
        col_y, col_ay, col_tek = st.columns(3, gap="medium")
        
        with col_y:
            yillar = sorted(df_raw['Yil'].dropna().unique().tolist(), reverse=True) if 'Yil' in df_raw.columns else [2026, 2025]
            yillar = [int(y) for y in yillar if pd.notna(y) and int(y) != 2024] # 2024'ü hariç tut
            current_year = datetime.now().year
            default_yil_idx = yillar.index(current_year) if current_year in yillar else 0
            secili_yil = st.selectbox("YIL", yillar, index=default_yil_idx, key="saha_yil")
        
        with col_ay:
            aylar_tum = list(AY_MAP.items())
            ay_listesi = ["Tümü"] + [ay[1] for ay in aylar_tum]
            current_month = datetime.now().month
            current_ay_adi = AY_MAP.get(current_month, "Ocak")
            default_ay_idx = ay_listesi.index(current_ay_adi) if current_ay_adi in ay_listesi else 0
            secili_ay = st.selectbox("AY", ay_listesi, index=default_ay_idx, key="saha_ay")
            secili_ay_no = [k for k, v in AY_MAP.items() if v == secili_ay][0] if secili_ay != "Tümü" else None
        
        with col_tek:
            raw_teknisyenler = sorted(df_raw['Teknisyen 1'].dropna().unique().tolist())
            raw_teknisyenler = [t for t in raw_teknisyenler if t.strip() != '']
            
            analiz_saha_listesi = set()
            if not df_personel.empty and 'Ad_Soyad' in df_personel.columns:
                if secili_ay_no:
                    last_day = calendar.monthrange(secili_yil, secili_ay_no)[1]
                    p_end = date(secili_yil, secili_ay_no, last_day)
                else:
                    p_end = date(secili_yil, 12, 31)
                
                p_end_ts = pd.Timestamp(p_end)
                mask_dept = df_personel['Departman'].str.strip().str.upper() == 'SAHA'
                
                mask_date = pd.Series([False] * len(df_personel), index=df_personel.index)
                if 'Ise_Giris' in df_personel.columns:
                    ise_giris_valid = pd.to_datetime(df_personel['Ise_Giris'], errors='coerce')
                    mask_entry = ise_giris_valid.notna() & (ise_giris_valid <= p_end_ts)
                    mask_date = mask_entry # Çıkış kontrolü eklenebilir
                
                analiz_saha_listesi = set(df_personel[mask_dept & mask_date]['Ad_Soyad'].str.upper().tolist())
                
            if not analiz_saha_listesi:
                 teknisyenler_dropdown = sorted(list(saha_listesi)) if not df_personel.empty else raw_teknisyenler
            else:
                 teknisyenler_dropdown = sorted(list(analiz_saha_listesi))
                 
            teknisyen_listesi = ["Tümü"] + teknisyenler_dropdown
            secili_teknisyen = st.selectbox("TEKNİSYEN", teknisyen_listesi, key="saha_teknisyen")
        
    
        
        # === VERİ FİLTRELEME ===
        df = df_raw.copy()
        if 'Yil' in df.columns: df = df[df['Yil'] == secili_yil]
        if secili_ay_no and 'Ay' in df.columns: df = df[df['Ay'] == secili_ay_no]
        
        # İstatistikler için filtrelenmiş DF (Teknisyen seçimi etkili)
        df_stats = df.copy()
        if secili_teknisyen != "Tümü":
            mask = (df_stats['Teknisyen 1'] == secili_teknisyen)
            if 'Teknisyen 2' in df_stats.columns: mask = mask | (df_stats['Teknisyen 2'] == secili_teknisyen)
            df_stats = df_stats[mask]
        
    
        
        spacer(20)
        
        # === ÖZET HESAPLAMALAR ===
        if secili_ay_no:
            is_gunleri = get_weekday_count(secili_yil, secili_ay_no, holidays=holidays)
        else:
            is_gunleri = get_weekday_count(secili_yil, holidays=holidays)
        
        # İstatistikler (Tümü veya Tek Kişi)
        sahada_gun = 0; izin_gun = 0; atolye_gun = 0
        
        # İstatistik Hesaplama (df_stats üzerinden)
        if secili_teknisyen != "Tümü":
            # Tek Kişi Hesabı
            if 'Tarih' in df_stats.columns:
                 sahada_gun = df_stats[df_stats['Durum'] == 'AKTİF']['Tarih'].dt.date.nunique()
                 
                 mask_aktif = df_stats['Durum'] == 'AKTİF'
                 mask_haftaici = df_stats['Tarih'].dt.dayofweek < 5
                 
                 dates_saha = df_stats[mask_aktif & mask_haftaici]['Tarih'].dt.date
                 if holidays: dates_saha = dates_saha[~dates_saha.isin(holidays)]
                 sahada_hi = dates_saha.nunique()
                 
                 izin_gun = df_stats[df_stats['Durum'] == 'İZİNLİ']['Tarih'].dt.date.nunique()
                 
                 mask_izinli = df_stats['Durum'] == 'İZİNLİ'
                 dates_izin = df_stats[mask_izinli & mask_haftaici]['Tarih'].dt.date
                 if holidays: dates_izin = dates_izin[~dates_izin.isin(holidays)]
                 izin_hi = dates_izin.nunique()
                 
                 atolye_gun = max(0, is_gunleri - sahada_hi - izin_hi)
            else:
                 sahada_gun = len(df_stats[df_stats['Durum'] == 'AKTİF'])
                 izin_gun = len(df_stats[df_stats['Durum'] == 'İZİNLİ'])
        else:
            # Toplu Hesap (df_stats = tüm ekip)
            for tek in saha_listesi:
                mask = (df_stats['Teknisyen 1'] == tek)
                if 'Teknisyen 2' in df_stats.columns: mask = mask | (df_stats['Teknisyen 2'] == tek)
                tek_df = df_stats[mask]
                
                # Efektif Gün
                tech_is_gunleri = is_gunleri
                if not df_personel.empty and 'Ad_Soyad' in df_personel.columns:
                     p_row = df_personel[df_personel['Ad_Soyad'].str.upper() == tek]
                     if not p_row.empty and 'Ise_Giris' in p_row.columns:
                         start_date = p_row.iloc[0]['Ise_Giris']
                         end_date = p_row.iloc[0]['Isten_Cikis'] if 'Isten_Cikis' in p_row.columns else None
                         tech_is_gunleri = calculate_effective_workdays(secili_yil, secili_ay_no, start_date, end_date=end_date, holidays=holidays)
                         
                         if not tek_df.empty and 'Tarih' in tek_df.columns:
                             if pd.notna(start_date): tek_df = tek_df[tek_df['Tarih'] >= pd.to_datetime(start_date)]
                             if pd.notna(end_date): tek_df = tek_df[tek_df['Tarih'] <= pd.to_datetime(end_date)]
    
                if not tek_df.empty and 'Tarih' in tek_df.columns:
                    t_sahada = tek_df[tek_df['Durum'] == 'AKTİF']['Tarih'].dt.date.nunique()
                    t_izin = tek_df[tek_df['Durum'] == 'İZİNLİ']['Tarih'].dt.date.nunique()
                    
                    mask_aktif = tek_df['Durum'] == 'AKTİF'
                    mask_haftaici = tek_df['Tarih'].dt.dayofweek < 5
                    
                    df_a_filtered = tek_df[mask_aktif & mask_haftaici]
                    dates_s = df_a_filtered['Tarih'].dt.date
                    if holidays: dates_s = dates_s[~dates_s.isin(holidays)]
                    t_sahada_hi = dates_s.nunique()
                    
                    mask_izinli = tek_df['Durum'] == 'İZİNLİ'
                    df_i_filtered = tek_df[mask_izinli & mask_haftaici]
                    dates_i = df_i_filtered['Tarih'].dt.date
                    if holidays: dates_i = dates_i[~dates_i.isin(holidays)]
                    t_izin_hi = dates_i.nunique()
                else:
                    t_sahada = len(tek_df[tek_df['Durum'] == 'AKTİF'])
                    t_izin = len(tek_df[tek_df['Durum'] == 'İZİNLİ'])
                    t_sahada_hi = t_sahada; t_izin_hi = t_izin
                
                t_atolye = max(0, tech_is_gunleri - t_sahada_hi - t_izin_hi)
                
                sahada_gun += t_sahada
                izin_gun += t_izin
                atolye_gun += t_atolye
    
        donem_text = f"{secili_ay} {secili_yil}" if secili_ay != "Tümü" else f"{secili_yil} Yılı"
        
        # Kapasite ve Verimlilik KPI'ları
        toplam_kapasite = 0
        
        # Kapasite Hesaplama Loop'u (KPI Kartları İçin)
        teks_to_calc = [secili_teknisyen] if secili_teknisyen != "Tümü" else list(saha_listesi)
        
        for tek in teks_to_calc:
             # Efektif Gün
            tech_is_gunleri = is_gunleri
            if not df_personel.empty and 'Ad_Soyad' in df_personel.columns:
                    p_row = df_personel[df_personel['Ad_Soyad'].str.upper() == tek]
                    if not p_row.empty and 'Ise_Giris' in p_row.columns:
                        start_date = p_row.iloc[0]['Ise_Giris']
                        end_date = p_row.iloc[0]['Isten_Cikis'] if 'Isten_Cikis' in p_row.columns else None
                        tech_is_gunleri = calculate_effective_workdays(secili_yil, secili_ay_no, start_date, end_date=end_date, holidays=holidays)
            
            toplam_kapasite += tech_is_gunleri

        # Yıllık İzin İndirimi Logic (Sadece Yıl = Tümü veya Yıl bazlı bakılıyorsa mantıklı)
        # Kullanıcı "kişi başı 14 gün düşelim" dedi. Bu aylık bakışta çok agresif olur.
        # Sadece yıllık bakışta (Ay = Tümü) 14, aksi takdirde 0 düşelim.
        # Veya orantısal: 14/12 * ay sayısı gibi de olabilir ama basitlik adına Yıllık -> 14.
        
        deduction_per_person = 14 if secili_ay == "Tümü" else 0
        total_deduction = len(teks_to_calc) * deduction_per_person
        
        net_kapasite = max(0, toplam_kapasite - total_deduction)
        
        # Verimlilik artık Net Kapasite'ye göre
        verimlilik_orani = (sahada_gun / net_kapasite * 100) if net_kapasite > 0 else 0
        
        # 4. Metrik: Net - Sahada
        kalan_kapasite = net_kapasite - sahada_gun
        
        # Ekstra KPI Kartları (Mevcutların Altına/Yanına)
        # Önce mevcutları göster
        render_period_stats(sahada_gun, atolye_gun, izin_gun, donem_text)
        
        spacer(40)
        # Yeni Kapasite ve Verimlilik Kartları (4'lü Yapı)
        kc1, kc2, kc3, kc4 = st.columns(4, gap="medium")
        from components.cards import render_kpi_card # Ensure import
        
        with kc1:
             st.markdown(render_kpi_card("İŞ GÜNÜ GÜCÜ", f"{toplam_kapasite:,}", "Brüt İş Günü Gücü", "calendar", "#6B7280"), unsafe_allow_html=True)
        with kc2:
             sub_text = f"-{total_deduction} Gün Yıllık İzin" if total_deduction > 0 else "İzin Dahil"
             st.markdown(render_kpi_card("NET İŞ GÜNÜ GÜCÜ", f"{net_kapasite:,}", sub_text, "briefcase", "#3B82F6"), unsafe_allow_html=True)
        with kc3:
             st.markdown(render_kpi_card("VERİMLİLİK", f"%{verimlilik_orani:.1f}", "Net İş Günü Gücüne Oran", "activity", "#8B5CF6"), unsafe_allow_html=True)
        with kc4:
             st.markdown(render_kpi_card("KALAN GÜN", f"{kalan_kapasite:,}", "Net - Sahada", "zap", "#F59E0B"), unsafe_allow_html=True)
        
        spacer(30)
        
        
        # === TABLO GÖSTERİMİ ===
        if secili_teknisyen == "Tümü":
            # --- ANA PERFORMANS TABLOLARI (Sadece 'Tümü' seçiliyken) ---
            
            ana_ekip = sorted(list(analiz_saha_listesi)) if 'analiz_saha_listesi' in locals() and analiz_saha_listesi else sorted(list(saha_listesi))
            
            render_technician_performance_table(df, ana_ekip, df_personel, secili_yil, secili_ay_no, is_gunleri, holidays)
            
            # Diğer Çalışanlar
            if 'raw_teknisyenler' not in locals(): raw_teknisyenler = []
            tum_personel_isimleri = set()
            if not df_personel.empty and 'Ad_Soyad' in df_personel.columns:
                tum_personel_isimleri = set(df_personel['Ad_Soyad'].str.upper().tolist())
            diger_calisanlar = sorted([t for t in raw_teknisyenler if t.upper() not in tum_personel_isimleri])
            
            if diger_calisanlar:
                spacer(30)
                render_other_workers_table(df, diger_calisanlar)
                
        else:
            # --- DETAY TABLOSU (Tek Kişi Seçiliyken) ---
            section_title(f"{secili_teknisyen} - SERVİS DETAYLARI", margin_top="0.5rem")
            df_detay = df_stats[df_stats['Durum'] == 'AKTİF'].copy()
            
            if df_detay.empty:
                st.info("Bu dönemde aktif servis kaydı bulunmuyor.")
            else:
                gosterilecek_kolonlar = ['Tarih', 'Müşteri', 'Servis Ürünü', 'İşlem', 'Şehir', 'Sorumlu']
                if 'Teknisyen 2' in df_detay.columns: gosterilecek_kolonlar.append('Teknisyen 2')
                
                mevcut_kolonlar = [k for k in gosterilecek_kolonlar if k in df_detay.columns]
                df_goster = df_detay[mevcut_kolonlar].copy()
                
                if 'Tarih' in df_goster.columns:
                    df_goster['Tarih'] = pd.to_datetime(df_goster['Tarih']).dt.strftime('%d.%m.%Y')
                
                st.dataframe(df_goster, width=1000, hide_index=True)
    
        # === GRAFİKLER (EN ALTTA - Her zaman görünür) ===
        spacer(30)
        
        # "Saha Ekibi" olarak tanımladığımız listeyi al (Tablodaki kişiler)
        active_tech_list = sorted(list(analiz_saha_listesi)) if 'analiz_saha_listesi' in locals() and analiz_saha_listesi else sorted(list(saha_listesi))
        
        # 1. Aylık Grafik İçin Veri Hazırlığı (Sadece Yıl ve Teknisyen filtresi)
        # df_raw: Ham veri
        df_monthly_chart = df_raw[df_raw['Yil'] == secili_yil].copy()
        
        # Sadece aktif saha ekibi filtresi (Her durumda uygula)
        mask_tech1 = df_monthly_chart['Teknisyen 1'].isin(active_tech_list)
        mask_tech2 = pd.Series(False, index=df_monthly_chart.index)
        if 'Teknisyen 2' in df_monthly_chart.columns:
            mask_tech2 = df_monthly_chart['Teknisyen 2'].isin(active_tech_list)
        df_monthly_chart = df_monthly_chart[mask_tech1 | mask_tech2]
        
        # Teknisyen Filtresi (Kullanıcı seçimi)
        if secili_teknisyen != "Tümü":
            mask = (df_monthly_chart['Teknisyen 1'] == secili_teknisyen)
            if 'Teknisyen 2' in df_monthly_chart.columns: mask = mask | (df_monthly_chart['Teknisyen 2'] == secili_teknisyen)
            df_monthly_chart = df_monthly_chart[mask]
            
        # Kompresör Filtresi
    
            
        # 2. Şehir Grafiği İçin Veri Hazırlığı (Yıl, Ay ve Teknisyen filtresi)
        # df_stats zaten filtrelerden geçmiş durumda, ancak "Diğer Çalışanlar"ı da içeriyor olabilir.
        # Bu yüzden df_stats üzerinde de saha ekibi filtresi uygulayalım.
        # 2. Şehir Grafiği İçin Veri Hazırlığı
        # Eğer "Tümü" seçiliyse: Her teknisyenin gittiği yer ayrı sayılmalı (Adam-Şehir)
        # Eğer Tek Kişi seçiliyse: O kişinin gittiği yerler (Zaten df_stats o kişiye göre filtreli)
        
        if secili_teknisyen == "Tümü":
            # Sadece AKTİF kayıtları baz al
            df_aktif_cities = df_stats[df_stats['Durum'] == 'AKTİF'].copy()
            
            # T1 için şehirler (T1 doluysa ve AKTİF personel ise)
            mask_t1 = df_aktif_cities['Teknisyen 1'].isin(active_tech_list)
            cities_t1 = df_aktif_cities[mask_t1][['Şehir']]
            
            cities_t2 = pd.DataFrame()
            if 'Teknisyen 2' in df_aktif_cities.columns:
                # T2 için şehirler (T2 doluysa ve AKTİF personel ise)
                mask_t2 = df_aktif_cities['Teknisyen 2'].isin(active_tech_list)
                cities_t2 = df_aktif_cities[mask_t2][['Şehir']]
                
            df_cities_chart = pd.concat([cities_t1, cities_t2], ignore_index=True)
            
        else:
            # Tek kişi seçiliyse
            # Sadece AKTİF olduğu işlerin şehirlerini say
            # Zaten df_stats seçili kişiye göre filtreli
            df_cities_chart = df_stats[df_stats['Durum'] == 'AKTİF'].copy()
            
        render_field_charts(df_monthly_chart, df_cities_chart, secili_yil, selected_person=secili_teknisyen, allowed_personnel=active_tech_list)




