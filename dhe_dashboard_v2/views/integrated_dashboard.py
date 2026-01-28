
import streamlit as st
import pandas as pd
from datetime import datetime
from config.constants import AY_MAP, PERSONEL_MAP
from core.utils import get_exchange_rate
from core.transforms import filter_latest_revisions
from components.layout import spacer
from components.dashboard_financials import render_financial_summary_tab, render_conversion_analysis_tab
from components.dashboard_charts import render_yearly_performance_chart

def render_integrated_dashboard(df_teklif: pd.DataFrame, df_siparis: pd.DataFrame, df_all_quotes: pd.DataFrame = None):
    """
    Birleştirilmiş Teknik Ofis Performansı ve Detaylı Analiz Sayfası.
    Tab yapısı ile Özet ve Detay görünümlerini ayırır.
    """
    if df_all_quotes is None:
        df_all_quotes = df_teklif.copy() # Fallback

    # --- ORTAK FİLTRE VE AYARLAR ---
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    available_years = sorted(df_siparis["Yil"].dropna().unique().astype(int).tolist(), reverse=True)
    if not available_years: available_years = [current_year]
    available_years = [y for y in available_years if 2017 <= y <= 2030]
    if not available_years: available_years = [current_year]
    
    default_years = [current_year] if current_year in available_years else [available_years[0]]
    current_month_name = AY_MAP.get(current_month, "Ocak")
    donem_opsiyonlari = ["Tüm Yıl"] + list(AY_MAP.values())
    default_donem_index = donem_opsiyonlari.index(current_month_name) if current_month_name in donem_opsiyonlari else 0
    
    # Layout: Yıl | Dönem | Para Birimi | Görünüm Modu
    c_yil, c_donem, c_pb, c_view = st.columns([1.5, 1, 1, 1], gap="medium")
    
    with c_yil:
        selected_year_val = st.selectbox("YIL", available_years, index=0, key="int_dash_yil_single")
        selected_years = [selected_year_val] # List format for compatibility
    
    with c_donem:
        selected_period = st.selectbox("DÖNEM", donem_opsiyonlari, index=default_donem_index, key="int_dash_donem")
        
    with c_pb:
        target_currency = st.radio("PARA BİRİMİ", ["EUR", "GBP", "TL"], index=0, horizontal=True, key="int_dash_pb")

    with c_view:
        # view_mode = st.radio("VERİ DURUMU", ["Net", "Tümü"], index=0, horizontal=True, key="int_dash_view_mode", help="Net: Sadece en güncel revizyonları gösterir.\nTümü: Tüm revizyonları dahil eder.")
        # ARTIK DEFAULT OLARAK HER ZAMAN NET (REVİZYONSUZ/GÜNCEL) GÖSTERİYORUZ
        st.markdown("<div style='padding-top: 10px; font-size: 0.8rem; color: gray;'>*Sadece en güncel revizyonlar gösterilmektedir.</div>", unsafe_allow_html=True)
        view_mode = "Net" # Sabitliyoruz

    # --- FİLTRELEME MANTIĞI (GLOBA REVİZYON - İPTAL) ---
    # Eski mantık: Tüm datada en son revizyonu alıyordu. Bu da Ocak ayındaki teklifin Şubat revizyonu varsa Ocak'ta görünmemesine yol açıyordu.
    # Yeni mantık: Revizyon filtresini dönem bazlı uygulayacağız.
    # if view_mode == "Net":
    #     df_siparis = filter_latest_revisions(df_siparis, "Siparis_No")
    #     df_teklif = filter_latest_revisions(df_teklif, "Teklif_No")
    #     df_all_quotes = filter_latest_revisions(df_all_quotes, "Teklif_No")
    
    # Chart İçin Global Net Data (Grafiklerde "şu anki durum" mantığı devam edebilir veya değişebilir)
    # Şimdilik grafik için ayrı bir set tutalım:
    df_siparis_chart = df_siparis.copy()
    if view_mode == "Net":
        df_siparis_chart = filter_latest_revisions(df_siparis_chart, "Siparis_No")

    # Veri Hazırlığı
    df_sip_years = df_siparis[df_siparis["Yil"].isin(selected_years)].copy()
    df_tek_years = df_teklif[df_teklif["Yil"].isin(selected_years)].copy()
    df_all_years = df_all_quotes[df_all_quotes["Yil"].isin(selected_years)].copy()
    
    if selected_period != "Tüm Yıl":
        months = [[k for k, v in AY_MAP.items() if v == selected_period][0]]
        df_sip_filtered = df_sip_years[df_sip_years["Ay"].isin(months)].copy()
        df_tek_filtered = df_tek_years[df_tek_years["Ay"].isin(months)].copy()
        df_all_filtered = df_all_years[df_all_years["Ay"].isin(months)].copy()
        filter_label = f"{selected_period} ({', '.join(map(str, sorted(selected_years)))})"
    else:
        df_sip_filtered = df_sip_years.copy()
        df_tek_filtered = df_tek_years.copy()
        df_all_filtered = df_all_years.copy()
        filter_label = f"Tüm Dönem ({', '.join(map(str, sorted(selected_years)))})"

    # --- REVİZYON FİLTRESİ (LOCAL - SEÇİLİ DÖNEM İÇİN) ---
    # "Net" modunda, SADECE o dönem içinde tekrarlayan revizyonları temizle.
    # Böylece Ocak ayında Teklif A varsa ve Şubat'ta A-R1 varsa:
    # Ocak seçildiğinde: A görünür (Çünkü o dönemde tek).
    # Bu mantık "O tarihteki görüntü"yü verir.
    if view_mode == "Net":
        df_sip_filtered = filter_latest_revisions(df_sip_filtered, "Siparis_No")
        df_tek_filtered = filter_latest_revisions(df_tek_filtered, "Teklif_No")
        df_all_filtered = filter_latest_revisions(df_all_filtered, "Teklif_No")

    # Kur Dönüşümü
    max_selected_year = max(selected_years) if selected_years else 2025
    rate = get_exchange_rate(target_currency, max_selected_year)
    if rate == 0: rate = 1.0
    conversion_factor = 1.0 / rate
    symbol_map = {"EUR": "€", "GBP": "£", "TL": "₺"}
    sym = symbol_map.get(target_currency, "€")

    # CSS
    # === STYLE INJECTION REMOVED (Handled Globally) ===

    # --- TAB YAPISI ---
    tab_finansal, tab_teklif_siparis, tab_detay = st.tabs(["FİNANSAL", "SİPARİŞ / TEKLİF", "DETAYLI İŞLEM KAYITLARI"])
    
    # Geçmiş Veri (Delta Hesaplaması)
    previous_values = None
    if len(selected_years) == 1:
        current_sel_year = selected_years[0]
        prev_year = current_sel_year - 1
        
        # Sadece bir önceki yılın verisini al
        df_sip_prev = df_siparis[df_siparis["Yil"] == prev_year].copy()
        # df_tek_prev = df_teklif[df_teklif["Yil"] == prev_year].copy() # Old: Open quotes
        df_all_prev = df_all_quotes[df_all_quotes["Yil"] == prev_year].copy() # New: All quotes
        
        # Eğer spesifik bir ay seçiliyse, o ayın önceki yılına bak
        if selected_period != "Tüm Yıl":
             months = [[k for k, v in AY_MAP.items() if v == selected_period][0]]
             df_sip_prev = df_sip_prev[df_sip_prev["Ay"].isin(months)]
             # df_tek_prev = df_tek_prev[df_tek_prev["Ay"].isin(months)]
             df_all_prev = df_all_prev[df_all_prev["Ay"].isin(months)]
        
        # Delta için de filtre (Mevcut dönem "Net" ise geçmiş dönem de "Net" olmalı ki elma-elma kıyaslansın)
        if view_mode == "Net":
            df_sip_prev = filter_latest_revisions(df_sip_prev, "Siparis_No")
            df_all_prev = filter_latest_revisions(df_all_prev, "Teklif_No")

        previous_values = {
            "total_ciro": df_sip_prev["Tutar_EUR"].sum(),
            "total_kar": df_sip_prev["Kar_EUR"].sum(),
            "total_siparis": len(df_sip_prev),
            "total_teklif": len(df_all_prev) # Using total quotes for comparison
        }

    with tab_finansal:
        render_financial_summary_tab(df_sip_filtered, df_tek_filtered, selected_years, selected_period, sym, conversion_factor, previous_values, df_all_filtered=df_all_filtered)
        
        # Grafikler (Tüm yıllar)
        all_available_years = sorted(df_siparis["Yil"].dropna().unique().astype(int).tolist(), reverse=True)
        all_available_years = [y for y in all_available_years if 2017 <= y <= 2030]
        render_yearly_performance_chart(df_siparis_chart, all_available_years, conversion_factor, sym)

    with tab_teklif_siparis:
        render_conversion_analysis_tab(df_sip_filtered, df_tek_filtered, filter_label, df_all_filtered=df_all_filtered)

    with tab_detay:
        spacer(16)
        
        c_durum, c_pers, c_arama = st.columns([1.5, 2, 3], gap="medium")
        
        with c_durum:
            durum_secimi = st.radio("Kayıt Türü", ["Sipariş", "Teklif"], horizontal=True, label_visibility="collapsed", key="detay_durum_sec")
        
        with c_pers:
            aktif_personel_isimleri = list(set(PERSONEL_MAP.values()))
            secilen_personel = st.selectbox("Personel", ["Tümü"] + sorted(aktif_personel_isimleri), label_visibility="collapsed", key="detay_pers_sec")
             
        with c_arama:
             arama_metni = st.text_input("Müşteri Firma Ara", placeholder="Firma adı yazın...", label_visibility="collapsed", key="detay_arama")
        
        spacer(10)
        
        df_table = df_sip_filtered.copy() if durum_secimi == "Sipariş" else df_tek_filtered.copy()
        
        if secilen_personel != "Tümü":
            df_table = df_table[df_table["Personel_Adi"] == secilen_personel]
            
        if arama_metni:
            df_table = df_table[df_table["Musteri"].str.lower().str.contains(arama_metni.lower(), na=False)]
            
        if not df_table.empty:
            df_table = df_table.sort_values("Tarih", ascending=False)
            df_table["Tarih_Str"] = df_table["Tarih"].dt.strftime("%d.%m.%Y")
            df_table["Gosterim_Tutar"] = df_table["Tutar_EUR"] * conversion_factor
            df_table["Gosterim_Maliyet"] = df_table["Maliyet_EUR"] * conversion_factor
            
            st.dataframe(
                df_table[["Tarih_Str", "Teklif_No", "Musteri", "Personel_Adi", "Gosterim_Tutar", "Gosterim_Maliyet"]],
                column_config={
                    "Tarih_Str": "Tarih",
                    "Teklif_No": "Belge No",
                    "Musteri": st.column_config.TextColumn("Müşteri Firma", width="large"),
                    "Personel_Adi": "Temsilci",
                    "Gosterim_Tutar": st.column_config.NumberColumn(f"Tutar ({sym})", format=f"{sym}%.0f"),
                    "Gosterim_Maliyet": st.column_config.NumberColumn(f"Maliyet ({sym})", format=f"{sym}%.0f"),
                },
                height=350, width="stretch", hide_index=True
            )
            st.markdown(f"*Toplam {len(df_table)} kayıt listeleniyor.*")
        else:
            st.warning("Kriterlere uygun kayıt bulunamadı.")
