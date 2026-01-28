
import streamlit as st
import pandas as pd
from components.customer_tabs import render_summary_tab, render_details_tab, render_orphaned_analysis_tab, render_products_tab

def render_musteri(df_musteri: pd.DataFrame, df_all_quotes: pd.DataFrame = None, df_urun: pd.DataFrame = None):
    """Müşteri Portföyü - Tab yapısı ile Özet, Detay, Sahipsiz Analiz ve Servis Ürünleri."""
    
    if df_musteri.empty:
        st.warning("Müşteri master listesi yüklenemedi.")
        return

    # Veri Tutarlılığı: Sahipsiz müşteri analizinde de NET teklif sayısını baz alalım
    from core.transforms import filter_latest_revisions
    if df_all_quotes is not None and not df_all_quotes.empty:
         df_all_quotes = filter_latest_revisions(df_all_quotes, "Teklif_No")
    
    # Tema Kontrolü
    theme = st.session_state.get("theme", "light")
    
    # Table CSS Injection
    # Table & Tab CSS Injection
    # === TAB/TABLE CSS REMOVED (Handled Globally) ===

    # TAB YAPISI
    tab_ozet, tab_detay, tab_sahipsiz, tab_urun_tab = st.tabs([
        "PORTFÖY ÖZETİ", 
        "DETAY GÖRÜNTÜLEME", 
        "SAHİPSİZ MÜŞTERİ ANALİZİ",
        "SERVİS ÜRÜNLERİ"
    ])
    
    # TAB 1: PORTFÖY ÖZETİ
    with tab_ozet:
        render_summary_tab(df_musteri, theme)
    
    # TAB 2: DETAY GÖRÜNTÜLEME
    with tab_detay:
        render_details_tab(df_musteri, theme)

    # TAB 3: SAHİPSİZ MÜŞTERİ ANALİZİ
    with tab_sahipsiz:
        bos_musteriler = df_musteri[df_musteri["Sorumlu_Clean"] == "BOŞ / SAHİPSİZ"]
        render_orphaned_analysis_tab(df_musteri, df_all_quotes, bos_musteriler)
    
    # TAB 4: SERVİS ÜRÜNLERİ
    with tab_urun_tab:
        render_products_tab(df_urun)
