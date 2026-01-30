"""
CRM Page - Müşteri Takip
=========================
Tab yapısı ile dönem bazlı müşteri analizi.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from components.cards import render_kpi_card
from components.layout import spacer, section_title
from config.constants import COLORS

def render_crm_page(df_crm: pd.DataFrame, df_teklif: pd.DataFrame, df_siparis: pd.DataFrame):
    """Müşteri Takip - Tab yapısı ile dönem bazlı görünüm."""
    
    # HEADER
    section_title("MÜŞTERİ TAKİP", margin_top="0rem", show_border=False, margin_bottom="0.5rem")
    
    if df_crm.empty:
        st.warning("Müşteri verileri yüklenemedi.")
        return

    # =========================================================================
    # VERİ HESAPLAMALARI
    # =========================================================================
    
    # Segment güncelleme - emoji yerine temiz metin
    def clean_segment(seg):
        if pd.isna(seg):
            return "Diğer"
        seg = str(seg)
        if "VIP" in seg:
            return "Öncelikli"
        elif "Gold" in seg:
            return "Düzenli"
        elif "Standart" in seg:
            return "Ara Sıra"
        elif "Potansiyel" in seg:
            return "Potansiyel"
        elif "Pasif" in seg:
            return "Uyuyan"
        return "Diğer"
    
    df_crm = df_crm.copy()
    df_crm["Segment_Clean"] = df_crm["Segment"].apply(clean_segment)
    
    # Müşterileri 4 gruba ayır - SADECE AY BAZLI
    # Kritik: 24+ ay (730+ gün)
    # Pasife Dönük: 12-24 ay (365-730 gün)
    # İzlemede: 6-12 ay (180-365 gün)
    # Aktif: 0-6 ay (0-180 gün)

    # 1. Kritik (24+ Ay)
    df_kritik = df_crm[
        (df_crm["Recency_Days"] >= 730) & 
        (df_crm["Total_Teklif_EUR"] > 0)
    ].copy()
    
    # 2. Pasife Dönük (12-24 Ay)
    df_pasif = df_crm[
        (df_crm["Recency_Days"] >= 365) & 
        (df_crm["Recency_Days"] < 730) &
        (df_crm["Total_Teklif_EUR"] > 0)
    ].copy()
    
    # 3. İzlemede (6-12 Ay)
    df_izleme = df_crm[
        (df_crm["Recency_Days"] >= 180) & 
        (df_crm["Recency_Days"] < 365) &
        (df_crm["Total_Teklif_EUR"] > 0)
    ].copy()
    
    # 4. Aktif (0-6 Ay)
    df_aktif = df_crm[
        (df_crm["Recency_Days"] < 180) &
        (df_crm["Total_Teklif_EUR"] > 0)
    ].copy()
    
    # Sıralama
    df_kritik = df_kritik.sort_values("Total_Teklif_EUR", ascending=False)
    df_pasif = df_pasif.sort_values("Total_Teklif_EUR", ascending=False)
    df_izleme = df_izleme.sort_values("Total_Teklif_EUR", ascending=False)
    df_aktif = df_aktif.sort_values("Total_Teklif_EUR", ascending=False)
    
    # KPI Kartları
    toplam_musteri = len(df_crm[df_crm["Total_Teklif_EUR"] > 0])
    # Aktif müşteri: Son 1 yıl (0-6 + 6-12 ay)
    aktif_musteri_sayisi = len(df_aktif) + len(df_izleme)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(render_kpi_card(
            "AKTİF MÜŞTERİ", 
            f"{aktif_musteri_sayisi}", 
            f"Son 1 yılda işlem", 
            "users", 
            COLORS["SUCCESS"]
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(render_kpi_card(
            "TEKLİF PORTFÖYÜ", 
            f"{toplam_musteri}", 
            "Teklif verilen firma", 
            "briefcase", 
            COLORS["INFO"]
        ), unsafe_allow_html=True)
    
    spacer(24)
    
    # =========================================================================
    # TAB YAPISI
    # =========================================================================
    tab_aktif, tab_izleme, tab_pasif, tab_kritik = st.tabs([
        "0-6 AY", 
        "6-12 AY", 
        "12-24 AY",
        "24+ AY"
    ])
    
    # Tab CSS
    # Tab CSS Injection
    # === TAB CSS REMOVED (Handled Globally) ===
    
    # =========================================================================
    # YARDIMCI FONKSİYON
    # =========================================================================
    def render_customer_table(df, color, period_label):
        """Tek bir müşteri grubu için tablo render et."""
        
        # Filtre Alanı (Arama + Personel)
        c_search, c_personel = st.columns([3, 1], gap="medium")
        
        with c_search:
            search_term = st.text_input(
                "Müşteri Ara", 
                placeholder="Ara...", 
                label_visibility="collapsed",
                key=f"crm_search_{period_label}"
            )
            
        with c_personel:
            # Sadece bu dönemde mevcut olan personeller
            available_personnel = []
            if "Sorumlu_Clean" in df.columns:
                 available_personnel = sorted(df["Sorumlu_Clean"].dropna().unique().astype(str).tolist())
            
            selected_personnel = st.selectbox(
                "Personel",
                ["Tümü"] + available_personnel,
                label_visibility="collapsed",
                key=f"crm_personel_{period_label}"
            )
        
        spacer(16)
        
        if df.empty:
            st.info("Bu dönemde müşteri bulunamadı.")
            return
            
        # Arama filtresi
        df_filtered = df.copy()
        
        if search_term:
            df_filtered = df_filtered[df_filtered["Musteri"].str.contains(search_term, case=False, na=False)]
            
        # Personel Filtresi
        if selected_personnel != "Tümü" and "Sorumlu_Clean" in df_filtered.columns:
            df_filtered = df_filtered[df_filtered["Sorumlu_Clean"] == selected_personnel]
            
        if df_filtered.empty:
            st.info("Arama kriterlerine uygun müşteri bulunamadı.")
            return
        
        count = len(df_filtered)
        
        # Başlık
        st.markdown(f'<div style="font-size:1rem; font-weight:600; margin-bottom:12px; color:{color};">{count} Müşteri Listeleniyor</div>', unsafe_allow_html=True)
        
        # Tablo formatında göster
        df_display = df_filtered.copy()
        
        df_display["Son_Islem"] = df_display["Son_Teklif_Tarihi"].dt.strftime("%d.%m.%Y")
        
        # Son Teklif Detayları (NaN kontrolü)
        if "Son_Teklif_No" not in df_display.columns:
            df_display["Son_Teklif_No"] = "-"
            df_display["Son_Teklif_Tutar"] = 0
            
        df_display["Teklif_Fmt"] = df_display["Total_Teklif_EUR"]
        
        if "Sorumlu_Clean" in df_display.columns:
            df_display["Sorumlu_Display"] = df_display["Sorumlu_Clean"]
        else:
            df_display["Sorumlu_Display"] = "-"
            
        st.dataframe(
            df_display[["Musteri", "Sorumlu_Display", "Son_Teklif_No", "Son_Teklif_Tutar", "Son_Islem"]],
            column_config={
                "Musteri": st.column_config.TextColumn("Firma Ünvanı", width="large"),
                "Sorumlu_Display": st.column_config.TextColumn("Sorumlu", width="small"),
                "Son_Teklif_No": st.column_config.TextColumn("Son Teklif No", width="small"),
                "Son_Teklif_Tutar": st.column_config.NumberColumn("Son Tutar", format="€%.0f", width="small"),
                "Son_Islem": st.column_config.TextColumn("Son Tarih", width="small"),
            },
            hide_index=True,
            height=350,
            width="stretch"
        )
    
    # =========================================================================
    # TAB İÇERİKLERİ
    # =========================================================================
    
    with tab_aktif:
        spacer(16)
        render_customer_table(df_aktif, COLORS["SUCCESS"], "aktif")
    
    with tab_izleme:
        spacer(16)
        render_customer_table(df_izleme, COLORS["WARNING"], "izleme")
    
    with tab_pasif:
        spacer(16)
        render_customer_table(df_pasif, "#F97316", "pasif") # Orange not in main constants yet, keep hardcoded or add
    
    with tab_kritik:
        spacer(16)
        render_customer_table(df_kritik, COLORS["DANGER"], "kritik")
