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
from core.data_loader import load_holidays
from core.date_utils import get_weekday_count, calculate_effective_workdays
from core.utils import tr_upper
from components.field_stats import render_daily_tracking, render_period_stats
from components.field_tables import render_technician_performance_table, render_other_workers_table
from components.field_charts import render_field_charts

def render_saha(holidays=None, data_packet=None):
    # DHE Saha Operasyonları Görünümü
    # Verileri Al (data_packet'tan veya boş)
    if data_packet is None:
        data_packet = {}
    
    df_raw = data_packet.get("saha", pd.DataFrame())
    df_personel = data_packet.get("saha_personel", pd.DataFrame())
    
    if holidays is None:
        holidays = data_packet.get("holidays", set())
        if not holidays:
            holidays = load_holidays()
        
    if df_raw.empty:
        st.error("❌ Google Sheets'ten veri çekilemedi. Lütfen bağlantıyı kontrol edin.")
        return
    
    # === PERSONEL LİSTESİ HAZIRLIĞI ===
    saha_listesi = set()
    today = datetime.now().date()
    
    if not df_personel.empty and 'Ad_Soyad' in df_personel.columns:
        saha_filt = df_personel['Departman'].astype(str).str.strip().apply(tr_upper) == 'SAHA'
        if 'Isten_Cikis' in df_personel.columns:
             query_date = pd.Timestamp(today)
             active_filt = (df_personel['Isten_Cikis'].isnull()) | (df_personel['Isten_Cikis'] >= query_date)
             saha_filt = saha_filt & active_filt
        saha_listesi = set(df_personel[saha_filt]['Ad_Soyad'].apply(tr_upper).tolist())
    
    if not saha_listesi:
        saha_listesi = set([t.upper() for t in FIELD_TECHNICIANS])

    # === STYLE INJECTION ===
    # === STYLE INJECTION REMOVED (Handled Globally) ===

    # === TAB YAPISI ===
    tab_gunluk, tab_performans = st.tabs([f"GÜNLÜK TAKİP ({today.strftime('%d.%m.%Y')})", "TEKNİSYEN PERFORMANSI"])

    # === TAB 1: GÜNLÜK TAKİP ===
    with tab_gunluk:
        spacer(16)
        render_daily_tracking(df_raw, df_personel, all_technicians=saha_listesi)

    # === TAB 2: TEKNİSYEN PERFORMANSI ===
    with tab_performans:
        spacer(16)
        
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
                mask_dept = df_personel['Departman'].astype(str).str.strip().apply(tr_upper) == 'SAHA'
                
                mask_date = pd.Series([False] * len(df_personel), index=df_personel.index)
                if 'Ise_Giris' in df_personel.columns:
                    ise_giris_valid = pd.to_datetime(df_personel['Ise_Giris'], errors='coerce')
                    mask_entry = (ise_giris_valid.isna()) | (ise_giris_valid <= p_end_ts)
                    mask_date = mask_entry # Çıkış kontrolü eklenebilir
                
                analiz_saha_listesi = set(df_personel[mask_dept & mask_date]['Ad_Soyad'].apply(tr_upper).tolist())
                
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
        
    
        
        spacer(24)
        
        # === ÖZET HESAPLAMALAR ===
        # 1. ADIM: DÖNEMİN TÜM İŞ GÜNLERİNİ TEK SEFERDE HESAPLA (Global Maske)
        # -------------------------------------------------------------------
        try:
            # Dönem sınırlarını belirle
            if secili_ay_no:
                p_start = date(secili_yil, secili_ay_no, 1)
                last_day = calendar.monthrange(secili_yil, secili_ay_no)[1]
                p_end = date(secili_yil, secili_ay_no, last_day)
            else:
                p_start = date(secili_yil, 1, 1)
                p_end = date(secili_yil, 12, 31)
            
            # Bugünü geçmemeli (Kapasite de bugüne kadar hesaplanmalı mı? Genelde evet)
            p_end = min(p_end, date.today())
            
            # Pandas Date Range (Tüm Günler)
            # Not: Eğer p_start > p_end ise (Gelecek ay) boş range döner
            full_date_range = pd.date_range(start=p_start, end=p_end)
            
            # Sadece Hafta İçi (Pzt=0...Cum=4)
            workday_mask = full_date_range.dayofweek < 5
            valid_dates = full_date_range[workday_mask]
            
            # Tatilleri Çıkar (Vektörize)
            if holidays:
                # Tatilleri normalize et ve timestamp'e çevir
                # holidays seti genelde date objesi veya string içeriyor, pd.Timestamp ile uyumlu hale getirelim
                holiday_timestamps = pd.to_datetime(list(holidays), errors="coerce")
                valid_dates = valid_dates[~valid_dates.isin(holiday_timestamps)]
                
            # Artık elimizde "valid_dates" var: Bu dönemdeki "Resmi Çalışma Günleri" listesi.
            # Her teknisyen için sadece giriş/çıkış tarihine göre bunu filtreleyeceğiz.
            # len(valid_dates) -> Bu dönemin max iş günü sayısı
            global_max_workdays = len(valid_dates)
            
        except Exception as e:
            # Fallback
            st.error(f"Tarih hesaplama hatası: {e}")
            global_max_workdays = 0
            valid_dates = pd.DatetimeIndex([])

        
        # İstatistikler (Tümü veya Tek Kişi)
        sahada_gun = 0; izin_gun = 0; atolye_gun = 0
        
        # İstatistik Hesaplama (df_stats üzerinden) - MEVCUT MANTIK KORUNDU
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
                 
                 # Tek kişi için base gün sayısı:
                 # valid_dates içinden kişinin çalışma aralığına uyanları say
                 tech_workdays = global_max_workdays
                 if not df_personel.empty and 'Ad_Soyad' in df_personel.columns:
                     p_row = df_personel[df_personel['Ad_Soyad'].apply(tr_upper) == secili_teknisyen]
                     if not p_row.empty and 'Ise_Giris' in p_row.columns:
                         start_dt = pd.to_datetime(p_row.iloc[0]['Ise_Giris'])
                         end_dt = pd.to_datetime(p_row.iloc[0]['Isten_Cikis']) if 'Isten_Cikis' in p_row.columns else pd.NaT
                         
                         # Vectorized filter on valid_dates Index
                         dates_final = valid_dates
                         if pd.notna(start_dt): dates_final = dates_final[dates_final >= start_dt]
                         if pd.notna(end_dt): dates_final = dates_final[dates_final <= end_dt]
                         tech_workdays = len(dates_final)

                 atolye_gun = max(0, tech_workdays - sahada_hi - izin_hi)
            else:
                 sahada_gun = len(df_stats[df_stats['Durum'] == 'AKTİF'])
                 izin_gun = len(df_stats[df_stats['Durum'] == 'İZİNLİ'])
        else:
            # Toplu Hesap
            # Buradaki döngü sadece istatistik toplamak için, kapasite hesabını aşağıda optimize ettik.
            # Ancak atolye_gun için yine de kişi bazlı hesap lazım.
            # Neyse ki valid_dates hazır olduğu için çok hızlı olacak.
            
            for tek in saha_listesi:
                mask = (df_stats['Teknisyen 1'] == tek)
                if 'Teknisyen 2' in df_stats.columns: mask = mask | (df_stats['Teknisyen 2'] == tek)
                tek_df = df_stats[mask]
                
                # HIZLI PERSONEL MASKESİ
                tech_workdays = global_max_workdays
                if not df_personel.empty and 'Ad_Soyad' in df_personel.columns:
                     # Bunu map dışına alabiliriz ama df_personel küçük, sorun değil.
                     p_row = df_personel[df_personel['Ad_Soyad'].str.upper() == tek]
                     if not p_row.empty:
                         start_dt = pd.to_datetime(p_row.iloc[0]['Ise_Giris'], dayfirst=True, errors='coerce')
                         end_dt = pd.to_datetime(p_row.iloc[0]['Isten_Cikis'], dayfirst=True, errors='coerce') if 'Isten_Cikis' in p_row.columns else pd.NaT
                         
                         dates_final = valid_dates
                         if pd.notna(start_dt): dates_final = dates_final[dates_final >= start_dt]
                         if pd.notna(end_dt): dates_final = dates_final[dates_final <= end_dt]
                         tech_workdays = len(dates_final)
                
                if not tek_df.empty and 'Tarih' in tek_df.columns:
                    t_sahada = tek_df[tek_df['Durum'] == 'AKTİF']['Tarih'].dt.date.nunique()
                    t_izin = tek_df[tek_df['Durum'] == 'İZİNLİ']['Tarih'].dt.date.nunique()
                    
                    mask_aktif = tek_df['Durum'] == 'AKTİF'
                    mask_haftaici = tek_df['Tarih'].dt.dayofweek < 5
                    
                    df_a = tek_df[mask_aktif & mask_haftaici]
                    dates_s = df_a['Tarih'].dt.date
                    if holidays: dates_s = dates_s[~dates_s.isin(holidays)]
                    t_sahada_hi = dates_s.nunique()
                    
                    mask_izinli = tek_df['Durum'] == 'İZİNLİ'
                    df_i = tek_df[mask_izinli & mask_haftaici]
                    dates_i = df_i['Tarih'].dt.date
                    if holidays: dates_i = dates_i[~dates_i.isin(holidays)]
                    t_izin_hi = dates_i.nunique()
                else:
                    t_sahada = len(tek_df[tek_df['Durum'] == 'AKTİF'])
                    t_izin = len(tek_df[tek_df['Durum'] == 'İZİNLİ'])
                    t_sahada_hi = t_sahada; t_izin_hi = t_izin
                
                t_atolye = max(0, tech_workdays - t_sahada_hi - t_izin_hi)
                
                sahada_gun += t_sahada
                izin_gun += t_izin
                atolye_gun += t_atolye
    
        donem_text = f"{secili_ay} {secili_yil}" if secili_ay != "Tümü" else f"{secili_yil} Yılı"
        
        # 2. ADIM: KAPASİTE HESAPLAMA (OPTİMİZE EDİLMİŞ)
        # ----------------------------------------------
        toplam_kapasite = 0
        teks_to_calc = [secili_teknisyen] if secili_teknisyen != "Tümü" else list(saha_listesi)
        
        # Personel tarihlerini map haline getirip hızlı erişim sağlayalım
        tech_dates_map = {}
        if not df_personel.empty and 'Ad_Soyad' in df_personel.columns:
             for idx, row in df_personel.iterrows():
                 name = str(row['Ad_Soyad']).upper()
                 s = pd.to_datetime(row['Ise_Giris'], dayfirst=True, errors='coerce')
                 e = pd.to_datetime(row['Isten_Cikis'], dayfirst=True, errors='coerce') if 'Isten_Cikis' in row and pd.notna(row['Isten_Cikis']) else pd.NaT
                 tech_dates_map[name] = (s, e)
        
        for tek in teks_to_calc:
             # Default: Global maske (Giriş çıkış yoksa full kapasite varsayıyoruz veya 0 mı? Data mantığına göre değişir)
             # Burada full varsayıyoruz (Eski kod öyleydi)
             tech_capacity = global_max_workdays
             
             if tek in tech_dates_map:
                 start_dt, end_dt = tech_dates_map[tek]
                 
                 # Vektörize Filtreleme (Çok Hızlı)
                 dates_final = valid_dates
                 if pd.notna(start_dt): dates_final = dates_final[dates_final >= start_dt]
                 if pd.notna(end_dt): dates_final = dates_final[dates_final <= end_dt]
                 tech_capacity = len(dates_final)
             
             toplam_kapasite += tech_capacity

        # Yıllık İzin (Deduction)
        deduction_per_person = 14 if secili_ay == "Tümü" else 0
        total_deduction = len(teks_to_calc) * deduction_per_person
        
        net_kapasite = max(0, toplam_kapasite - total_deduction)
        
        # Verimlilik KPI
        verimlilik_orani = (sahada_gun / net_kapasite * 100) if net_kapasite > 0 else 0
        kalan_kapasite = net_kapasite - sahada_gun
        
        # Ekstra KPI Kartları (Mevcutların Altına/Yanına)
        # Önce mevcutları göster
        render_period_stats(sahada_gun, atolye_gun, izin_gun, donem_text)
        
        spacer(40)
        # Yeni Kapasite ve Verimlilik Kartları (4'lü Yapı)
        kc1, kc2, kc3, kc4 = st.columns(4)
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
        
        spacer(32)
        
        # is_gunleri tanımla (global_max_workdays'den)
        is_gunleri = global_max_workdays
        
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
                spacer(32)
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
        spacer(32)
        
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




