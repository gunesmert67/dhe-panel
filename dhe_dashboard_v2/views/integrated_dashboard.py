
import streamlit as st
import pandas as pd
from datetime import datetime
from config.constants import AY_MAP, PERSONEL_MAP
from core.utils import get_exchange_rate
from components.layout import spacer
from components.dashboard_financials import render_financial_summary_tab, render_conversion_analysis_tab
from components.dashboard_charts import render_yearly_performance_chart

def render_integrated_dashboard(df_teklif: pd.DataFrame, df_siparis: pd.DataFrame):
    """
    Birleştirilmiş Teknik Ofis Performansı ve Detaylı Analiz Sayfası.
    Tab yapısı ile Özet ve Detay görünümlerini ayırır.
    """
    
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
    
    c_yil, c_donem, c_pb = st.columns([1.5, 1, 1], gap="large")
    
    with c_yil:
        selected_year_val = st.selectbox("YIL", available_years, index=0, key="int_dash_yil_single")
        selected_years = [selected_year_val] # List format for compatibility
    
    with c_donem:
        selected_period = st.selectbox("DÖNEM", donem_opsiyonlari, index=default_donem_index, key="int_dash_donem")
        
    with c_pb:
        target_currency = st.radio("PARA BİRİMİ", ["EUR", "USD", "TL"], index=0, horizontal=True, key="int_dash_pb")
    
    # Veri Hazırlığı
    df_sip_years = df_siparis[df_siparis["Yil"].isin(selected_years)].copy()
    df_tek_years = df_teklif[df_teklif["Yil"].isin(selected_years)].copy()
    
    if selected_period != "Tüm Yıl":
        months = [[k for k, v in AY_MAP.items() if v == selected_period][0]]
        df_sip_filtered = df_sip_years[df_sip_years["Ay"].isin(months)].copy()
        df_tek_filtered = df_tek_years[df_tek_years["Ay"].isin(months)].copy()
        filter_label = f"{selected_period} ({', '.join(map(str, sorted(selected_years)))})"
    else:
        df_sip_filtered = df_sip_years.copy()
        df_tek_filtered = df_tek_years.copy()
        filter_label = f"Tüm Dönem ({', '.join(map(str, sorted(selected_years)))})"

    # Kur Dönüşümü
    max_selected_year = max(selected_years) if selected_years else 2025
    rate = get_exchange_rate(target_currency, max_selected_year)
    if rate == 0: rate = 1.0
    conversion_factor = 1.0 / rate
    symbol_map = {"EUR": "€", "USD": "$", "TL": "₺"}
    sym = symbol_map.get(target_currency, "€")

    # CSS
    st.markdown("""
    <style>
        div.row-widget.stRadio > div[role="radiogroup"] {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 4px;
            display: inline-flex;
            gap: 4px;
            width: 100%;
        }
        div.row-widget.stRadio > div[role="radiogroup"] label {
            background-color: transparent !important;
            border: none;
            flex: 1;
            text-align: center;
            border-radius: 6px;
            padding: 4px 12px;
            color: var(--text-secondary) !important;
        }
        div.row-widget.stRadio > div[role="radiogroup"] label[data-checked="true"] {
            background-color: var(--card-bg) !important;
            color: var(--text-primary) !important;
            font-weight: 600;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
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

    # --- TAB YAPISI ---
    tab_finansal, tab_teklif_siparis, tab_detay = st.tabs(["FİNANSAL", "TEKLİF / SİPARİŞ", "DETAYLI İŞLEM KAYITLARI"])
    
    # Geçmiş Veri (Delta Hesaplaması)
    previous_values = None
    if len(selected_years) == 1:
        current_sel_year = selected_years[0]
        prev_year = current_sel_year - 1
        
        # Sadece bir önceki yılın verisini al
        df_sip_prev = df_siparis[df_siparis["Yil"] == prev_year].copy()
        df_tek_prev = df_teklif[df_teklif["Yil"] == prev_year].copy()
        
        # Eğer spesifik bir ay seçiliyse, o ayın önceki yılına bak
        if selected_period != "Tüm Yıl":
             months = [[k for k, v in AY_MAP.items() if v == selected_period][0]]
             df_sip_prev = df_sip_prev[df_sip_prev["Ay"].isin(months)]
             df_tek_prev = df_tek_prev[df_tek_prev["Ay"].isin(months)]
        
        previous_values = {
            "total_ciro": df_sip_prev["Tutar_EUR"].sum(),
            "total_kar": df_sip_prev["Kar_EUR"].sum(),
            "total_siparis": len(df_sip_prev),
            "total_teklif": len(df_tek_prev)
        }

    with tab_finansal:
        render_financial_summary_tab(df_sip_filtered, df_tek_filtered, selected_years, selected_period, sym, conversion_factor, previous_values)
        
        # Grafikler (Tüm yıllar)
        all_available_years = sorted(df_siparis["Yil"].dropna().unique().astype(int).tolist(), reverse=True)
        all_available_years = [y for y in all_available_years if 2017 <= y <= 2030]
        render_yearly_performance_chart(df_siparis, all_available_years, conversion_factor, sym)

    with tab_teklif_siparis:
        render_conversion_analysis_tab(df_sip_filtered, df_tek_filtered, filter_label)

    with tab_detay:
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        
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
