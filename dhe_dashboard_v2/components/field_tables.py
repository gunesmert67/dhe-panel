
import streamlit as st
import pandas as pd
from core.date_utils import calculate_effective_workdays
from components.layout import section_title

def render_technician_performance_table(df, ana_ekip, df_personel, secili_yil, secili_ay_no, is_gunleri, holidays):
    """Teknisyen performans tablosunu render eder."""
    
    section_title("TEKNİSYEN PERFORMANSI", margin_top="2rem", show_border=False)
    
    perf_data = []
    for tek in ana_ekip:
        tek_df = df.copy()
        
        mask = (tek_df['Teknisyen 1'] == tek)
        if 'Teknisyen 2' in tek_df.columns:
            mask = mask | (tek_df['Teknisyen 2'] == tek)
        tek_df = tek_df[mask]
        
        # İşe giriş tarihine göre efektif iş günü
        tech_is_gunleri = is_gunleri
        if not df_personel.empty and 'Ad_Soyad' in df_personel.columns:
                p_row = df_personel[df_personel['Ad_Soyad'].str.upper() == tek]
                if not p_row.empty and 'Ise_Giris' in p_row.columns:
                    start_date = p_row.iloc[0]['Ise_Giris']
                    end_date = p_row.iloc[0]['Isten_Cikis'] if 'Isten_Cikis' in p_row.columns else None
                    tech_is_gunleri = calculate_effective_workdays(secili_yil, secili_ay_no, start_date, end_date=end_date, holidays=holidays)
                    
                    if not tek_df.empty and 'Tarih' in tek_df.columns:
                        if pd.notna(start_date):
                            start_ts = pd.to_datetime(start_date)
                            tek_df = tek_df[tek_df['Tarih'] >= start_ts]
                        if pd.notna(end_date):
                            end_ts = pd.to_datetime(end_date)
                            tek_df = tek_df[tek_df['Tarih'] <= end_ts]

        if len(tek_df) == 0:
            aktif = 0
            izin = 0
            atolye = max(0, tech_is_gunleri)
        else:
            if 'Tarih' in tek_df.columns:
                aktif = tek_df[tek_df['Durum'] == 'AKTİF']['Tarih'].dt.date.nunique()
                izin = tek_df[tek_df['Durum'] == 'İZİNLİ']['Tarih'].dt.date.nunique()
                
                df_aktif_tek = tek_df[tek_df['Durum'] == 'AKTİF']
                dates_saha = df_aktif_tek[df_aktif_tek['Tarih'].dt.dayofweek < 5]['Tarih'].dt.date
                if holidays: dates_saha = dates_saha[~dates_saha.isin(holidays)]
                aktif_hafta_ici = dates_saha.nunique()
                
                df_izin_tek = tek_df[tek_df['Durum'] == 'İZİNLİ']
                dates_izin = df_izin_tek[df_izin_tek['Tarih'].dt.dayofweek < 5]['Tarih'].dt.date
                if holidays: dates_izin = dates_izin[~dates_izin.isin(holidays)]
                izin_hafta_ici = dates_izin.nunique()
            else:
                aktif = len(tek_df[tek_df['Durum'] == 'AKTİF'])
                izin = len(tek_df[tek_df['Durum'] == 'İZİNLİ'])
                aktif_hafta_ici = aktif
                izin_hafta_ici = izin
                        
            atolye = max(0, tech_is_gunleri - aktif_hafta_ici - izin_hafta_ici)
        
        row_data = {
            "Teknisyen": tek,
            "Toplam İş Günü": aktif,
            "Kapasite": tech_is_gunleri
        }
        
        # İşlem türleri
        bakim = 0; ariza = 0; devreye_alma = 0; diger = 0
        
        if 'İşlem' in tek_df.columns:
            tek_df_aktif = tek_df[tek_df['Durum'] == 'AKTİF']
            islemler = tek_df_aktif['İşlem'].astype(str).str.strip().str.upper()
            
            bakim = (islemler == "BAKIM").sum()
            ariza = (islemler.isin(["ARIZA", "ARIZA+BAKIM"])).sum()
            devreye_alma = (islemler == "DEVREYE ALMA").sum()
            
            toplam_islem = len(tek_df_aktif)
            diger = max(0, toplam_islem - (bakim + ariza + devreye_alma))
        
        row_data["Bakım"] = bakim
        row_data["Arıza"] = ariza
        row_data["Devreye Alma"] = devreye_alma
        row_data["Diğer"] = diger
        
        row_data["Atölye"] = atolye
        row_data["İzin"] = izin
        
        perf_data.append(row_data)
    
    df_perf = pd.DataFrame(perf_data)
    if not df_perf.empty:
        # Kapasite (İş Günü Gücü) Sütunu
        df_perf['İş Günü Gücü'] = df_perf['Teknisyen'].map({d['Teknisyen']: d.get('Kapasite', 0) for d in perf_data})
        
        # Verimlilik %
        df_perf['Verimlilik %'] = df_perf.apply(lambda x: round((x['Toplam İş Günü'] / x['İş Günü Gücü'] * 100), 1) if x['İş Günü Gücü'] > 0 else 0, axis=1)

        target_cols = ["Teknisyen", "İş Günü Gücü", "Toplam İş Günü", "Verimlilik %", "Bakım", "Arıza", "Devreye Alma", "Diğer", "Atölye", "İzin"]
        for col in target_cols:
            if col not in df_perf.columns: df_perf[col] = 0
        
        # Sütun tiplerini ayarla (Verimlilik float kalmalı)
        int_cols = [c for c in target_cols if c not in ["Teknisyen", "Verimlilik %"]]
        df_perf[int_cols] = df_perf[int_cols].fillna(0).astype(int)
        
        df_perf = df_perf[target_cols].sort_values("Toplam İş Günü", ascending=False)
        
        # Formatlama: Verimlilik sütununu yüzdelik gösterim için string'e çevir
        df_perf['Verimlilik %'] = df_perf['Verimlilik %'].apply(lambda x: f"%{x}")
        
        height = (len(df_perf) + 1) * 35 + 3
        st.dataframe(df_perf, width=1000, hide_index=True, height=int(height))


def render_other_workers_table(df, diger_calisanlar):
    """Diğer çalışanlar (Eski Çalışanlar) tablosunu render eder."""
    # Başlık güncellemesi
    section_title("ESKİ ÇALIŞANLAR", margin_top="1rem", show_border=False)

    if not diger_calisanlar:
        st.info("Seçilen dönemde eski teknisyen yok.")
        return
    
    diger_data = []
    for tek in diger_calisanlar:
        tek_df = df.copy()
        mask = (tek_df['Teknisyen 1'] == tek)
        if 'Teknisyen 2' in tek_df.columns:
            mask = mask | (tek_df['Teknisyen 2'] == tek)
        tek_df = tek_df[mask]
        
        if len(tek_df) == 0: continue
        
        if 'Tarih' in tek_df.columns:
            aktif = tek_df[tek_df['Durum'] == 'AKTİF']['Tarih'].dt.date.nunique()
        else:
            aktif = len(tek_df[tek_df['Durum'] == 'AKTİF'])
        
        row_data = {"Teknisyen": tek, "Toplam İş Günü": aktif}
        
        bakim = 0; ariza = 0; devreye_alma = 0; diger = 0
        if 'İşlem' in tek_df.columns:
            tek_df_aktif = tek_df[tek_df['Durum'] == 'AKTİF']
            islemler = tek_df_aktif['İşlem'].astype(str).str.strip().str.upper()
            bakim = (islemler == "BAKIM").sum()
            ariza = (islemler.isin(["ARIZA", "ARIZA+BAKIM"])).sum()
            devreye_alma = (islemler == "DEVREYE ALMA").sum()
            diger = max(0, len(tek_df_aktif) - (bakim + ariza + devreye_alma))
        
        row_data["Bakım"] = bakim
        row_data["Arıza"] = ariza
        row_data["Devreye Alma"] = devreye_alma
        row_data["Diğer"] = diger
        # Atölye ve İzin kaldırıldı

        if aktif > 0:
            diger_data.append(row_data)
    
    df_diger = pd.DataFrame(diger_data)
    if not df_diger.empty:
        # Atölye ve İzin hedef sütunlardan çıkarıldı
        target_cols = ["Teknisyen", "Toplam İş Günü", "Bakım", "Arıza", "Devreye Alma", "Diğer"]
        for col in target_cols:
             if col not in df_diger.columns: df_diger[col] = 0
        
        df_diger = df_diger[target_cols].fillna(0).astype({col: int for col in target_cols if col != "Teknisyen"})
        df_diger = df_diger.sort_values("Toplam İş Günü", ascending=False)
        
        height = (len(df_diger) + 1) * 35 + 3
        st.dataframe(df_diger, width=1000, hide_index=True, height=int(height))
    else:
        st.info("Seçilen dönemde eski teknisyen yok.")
