
import streamlit as st
import pandas as pd
from components.customer_tabs import render_summary_tab, render_details_tab, render_orphaned_analysis_tab, render_products_tab

def render_musteri(df_musteri: pd.DataFrame, df_all_quotes: pd.DataFrame = None, df_urun: pd.DataFrame = None):
    """Müşteri Portföyü - Tab yapısı ile Özet, Detay, Sahipsiz Analiz ve Servis Ürünleri."""
    
    if df_musteri.empty:
        st.warning("Müşteri master listesi yüklenemedi.")
        return
    
    # Tema Kontrolü
    theme = st.session_state.get("theme", "light")
    
    # Table CSS Injection
    # Table & Tab CSS Injection
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
