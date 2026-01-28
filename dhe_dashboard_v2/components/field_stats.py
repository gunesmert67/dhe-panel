
import streamlit as st
import pandas as pd
from datetime import datetime, date
from components.cards import render_kpi_card
from components.layout import spacer, section_title
from config.constants import FIELD_TECHNICIANS

def render_daily_tracking(df_raw, df_personel, all_technicians):
    """Günlük takip bölümünü (KPI Kartları + 3'lü Tablo) render eder."""
    
    today = datetime.now().date()
    
    if 'Tarih' in df_raw.columns:
        df_bugun = df_raw[df_raw['Tarih'].dt.date == today].copy()
    else:
        df_bugun = pd.DataFrame()
    

    
    if df_bugun.empty:
        # Bugün için veri yoksa, herkes atölyede varsayımı (veya veri girilmemiş)
        # Ancak burada mantık biraz karışık, orijinal koddaki mantığı koruyalım:
        bugun_sahada = 0
        bugun_atolye = len(all_technicians)
        bugun_izinli = 0
        sahada_toplam = set()
        izinli_set = set()
        atolye_set = all_technicians.copy()
    else:
        # Sahada: Aktif olan satırlardaki Teknisyen 1 + Teknisyen 2
        df_aktif_bugun = df_bugun[df_bugun['Durum'] == 'AKTİF'].copy()
        sahada_tek1 = set(df_aktif_bugun['Teknisyen 1'].dropna().str.strip().str.upper().unique()) if 'Teknisyen 1' in df_aktif_bugun.columns else set()
        sahada_tek2 = set(df_aktif_bugun['Teknisyen 2'].dropna().str.strip().str.upper().unique()) if 'Teknisyen 2' in df_aktif_bugun.columns else set()
        sahada_tek2 = {t for t in sahada_tek2 if t != ''}
        sahada_toplam = sahada_tek1.union(sahada_tek2)
        
        # İzinli
        df_izinli_bugun = df_bugun[df_bugun['Durum'] == 'İZİNLİ'].copy()
        izinli_tek1 = set(df_izinli_bugun['Teknisyen 1'].dropna().str.strip().str.upper().unique()) if 'Teknisyen 1' in df_izinli_bugun.columns else set()
        izinli_set = izinli_tek1
        
        # Hesaplanan Atölye
        excelde_gorulenler = sahada_toplam.union(izinli_set)
        atolye_set = all_technicians - excelde_gorulenler
        
        # Manuel Atölye
        df_atolye_bugun = df_bugun[df_bugun['Durum'] == 'ATÖLYE'].copy()
        atolye_excel = set(df_atolye_bugun['Teknisyen 1'].dropna().str.strip().str.upper().unique()) if 'Teknisyen 1' in df_atolye_bugun.columns else set()
        atolye_set = atolye_set.union(atolye_excel)
        
        bugun_sahada = len(sahada_toplam)
        bugun_izinli = len(izinli_set)
        bugun_atolye = len(atolye_set)
    
    # === KPI KARTLARI ===
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(render_kpi_card("SAHADA", f"{bugun_sahada}", "Bugün Aktif", "truck", "#10B981"), unsafe_allow_html=True)
    with g2:
        st.markdown(render_kpi_card("ATÖLYE", f"{bugun_atolye}", "Ofiste", "home", "#6B7280"), unsafe_allow_html=True)
    with g3:
        st.markdown(render_kpi_card("İZİNLİ", f"{bugun_izinli}", "Bugün", "coffee", "#F59E0B"), unsafe_allow_html=True)
    
    spacer(25)
    
    # === YAN YANA TABLOLAR ===
    # Teknik Ofis Tespiti
    teknik_ofis_set = set()
    if not df_bugun.empty:
        df_aktif_bugun_temp = df_bugun[df_bugun['Durum'] == 'AKTİF'].copy()
        for _, row in df_aktif_bugun_temp.iterrows():
            tek1 = str(row.get('Teknisyen 1', '')).strip().upper()
            tek2 = str(row.get('Teknisyen 2', '')).strip().upper()
            if tek1 and tek1 not in all_technicians:
                teknik_ofis_set.add(tek1)
            if tek2 and tek2 not in all_technicians:
                teknik_ofis_set.add(tek2)
    
    col_sahada, col_atolye, col_ofis = st.columns(3, gap="medium")
    
    with col_sahada:
        section_title("SAHADA", margin_top="1.5rem", show_border=False)
        if df_bugun.empty or sahada_toplam == set():
            st.info("Bugün sahada kimse yok.")
        else:
            df_aktif_bugun = df_bugun[df_bugun['Durum'] == 'AKTİF'].copy()
            sahada_list = []
            for _, row in df_aktif_bugun.iterrows():
                tek1 = str(row.get('Teknisyen 1', '')).strip()
                tek1_upper = tek1.upper()
                musteri = row.get('Müşteri', '-')
                if tek1 and tek1_upper in all_technicians:
                    sahada_list.append({"Teknisyen": tek1, "Firma": musteri})
                tek2 = str(row.get('Teknisyen 2', '')).strip()
                tek2_upper = tek2.upper()
                if tek2 and tek2_upper in all_technicians:
                    sahada_list.append({"Teknisyen": tek2, "Firma": musteri})
            
            if sahada_list:
                df_sahada = pd.DataFrame(sahada_list).drop_duplicates()
                st.dataframe(df_sahada, width=500, hide_index=True, height=(len(df_sahada) + 1) * 35 + 3)
            else:
                st.info("Bugün sahada teknisyen yok.")
    
    with col_atolye:
        section_title("ATÖLYE / İZİNLİ", margin_top="1.5rem", show_border=False)
        atolye_izin_list = []
        
        # Atölyedekiler
        for tek in sorted(atolye_set):
            # Orijinal case'i bulmaya çalış (güzellik için)
            original_name = next((t for t in FIELD_TECHNICIANS if t.upper() == tek), tek)
            atolye_izin_list.append({"Teknisyen": original_name, "Durum": "ATÖLYE"})
        
        # İzinliler
        for tek in sorted(izinli_set):
            original_name = next((t for t in FIELD_TECHNICIANS if t.upper() == tek), tek)
            atolye_izin_list.append({"Teknisyen": original_name, "Durum": "İZİNLİ"})
        
        if atolye_izin_list:
            df_atolye_goster = pd.DataFrame(atolye_izin_list)
            st.dataframe(df_atolye_goster, width=500, hide_index=True, height=(len(df_atolye_goster) + 1) * 35 + 3)
        else:
            st.info("Herkes sahada!")
    
    with col_ofis:
        section_title("TEKNİK OFİS", margin_top="1.5rem", show_border=False)
        if teknik_ofis_set:
            ofis_list = []
            df_aktif_bugun = df_bugun[df_bugun['Durum'] == 'AKTİF'].copy()
            for _, row in df_aktif_bugun.iterrows():
                tek1 = str(row.get('Teknisyen 1', '')).strip()
                tek2 = str(row.get('Teknisyen 2', '')).strip()
                musteri = row.get('Müşteri', '-')
                
                if tek1.upper() in teknik_ofis_set:
                    ofis_list.append({"Kişi": tek1, "Firma": musteri})
                if tek2.upper() in teknik_ofis_set:
                    ofis_list.append({"Kişi": tek2, "Firma": musteri})
            
            df_ofis = pd.DataFrame(ofis_list).drop_duplicates()
            st.dataframe(df_ofis, width=500, hide_index=True, height=(len(df_ofis) + 1) * 35 + 3)
        else:
            st.info("Bugün teknik ofisten sahaya çıkan yok.")

def render_period_stats(sahada_gun, atolye_gun, izin_gun, donem_text):
    """Dönemsel özet kartlarını render eder."""
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(render_kpi_card("SAHADA", f"{sahada_gun:,}", donem_text, "truck", "#10B981"), unsafe_allow_html=True)
    with k2:
        st.markdown(render_kpi_card("ATÖLYE", f"{atolye_gun:,}", donem_text, "home", "#6B7280"), unsafe_allow_html=True)
    with k3:
        st.markdown(render_kpi_card("İZİN", f"{izin_gun:,}", donem_text, "coffee", "#F59E0B"), unsafe_allow_html=True)
