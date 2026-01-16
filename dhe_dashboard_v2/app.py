"""
DHE Endüstriyel Dashboard - Ana Uygulama
=========================================
Streamlit tabanlı iş zekası ve yönetim portalı.

Klasör Yapısı:
- config/     : Sabitler ve konfigürasyon
- core/       : Veri yükleme ve yardımcı fonksiyonlar
- services/   : BackupManager, SystemMonitor
- components/ : UI bileşenleri (cards, charts, layout)
- views/      : Sayfa görünümleri
- data/       : Veri dosyaları
"""
import streamlit as st
import pandas as pd
import logging
import os

# Core Imports
from core.data_loader import load_data, prepare_crm_data, load_saha_data, load_holidays
from core.bellis_loader import load_bellis_data, load_sehirler_data

# View Imports
from views import (
    landing_page, 
    crm, 
    customers, 
    field_ops,
    integrated_dashboard,
    yuksel_ops,
    bellis
)
# Component Imports
from components import layout, styles, placeholders


# =============================================================================
# LOGGING YAPILANDIRMASI
# =============================================================================
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/dashboard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# SAYFA KONFİGÜRASYONU
# =============================================================================
st.set_page_config(
    page_title="DHE Endüstriyel | Yönetim Portalı",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    styles.inject_css()
    
    # Session State Başlatma
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        

        
    if "page" not in st.session_state:
        st.session_state.page = "ANA SAYFA"

    # Veri Yükleme
    # Not: Progress callback kullanmıyoruz - Streamlit rerun'da closure sorunu yaratıyordu
    with st.spinner("Veriler yükleniyor..."):
        try:
            data_packet = load_data(_progress_callback=None)
            # Saha verilerini de ön yükle (Cache Warming)
            load_saha_data()
            # Bellis verilerini de ön yükle
            load_bellis_data()
            load_sehirler_data()
        except Exception as e:
            logger.exception(f"Kritik yükleme hatası: {e}")
            st.error(f"Kritik yükleme hatası: {e}")
            data_packet = {}
        
    df_teklif = data_packet.get("teklif", pd.DataFrame())
    df_siparis = data_packet.get("siparis", pd.DataFrame())
    df_musteri = data_packet.get("musteri", pd.DataFrame())
    df_all_quotes = data_packet.get("all_quotes", pd.DataFrame())
    
    # Veri Kontrolü: Kritik tablolar boşsa devam etme
    if df_teklif.empty or df_siparis.empty:
        st.error("Veri yüklenemedi veya eksik. Lütfen günlükleri kontrol edin.")
        if st.button("Tekrar Dene"):
            st.rerun()
        return

    # SIDEBAR NAVİGASYON
    with st.sidebar:
        layout.render_sidebar_header()
        
        # --- DYNAMIC THEME CSS ---
        styles.inject_sidebar_style()


        
        # --- LOGO ALANI (ÖZEL MARKDOWN) ---
        st.sidebar.markdown("""
        <div class="sidebar-logo-container">
            <img src="https://dhe.com.tr/wp-content/uploads/2023/08/logo_dhe.png" width="140" style="opacity: 0.9;">
        </div>
        """, unsafe_allow_html=True)

        # --- MENÜ FONKSİYONU ---
        def menu_item(label, page_name, icon):
            is_active = st.session_state.page == page_name
            btn_type = "primary" if is_active else "secondary"
            
            # Label ve İkon Birleşimi
            display_label = f"{icon}  {label}"
            
            if st.button(display_label, key=f"nav_{page_name}", type=btn_type, width="stretch"):
                st.session_state.page = page_name
                st.rerun()

        # --- MENÜ YAPISI ---
        
        # Ana Sayfa (Grup Başlığı Yok)
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        menu_item("Ana Sayfa", "ANA SAYFA", "")
        
        # Teknik Ofis
        st.markdown('<div class="sidebar-group-title">TEKNİK OFİS</div>', unsafe_allow_html=True)
        menu_item("Müşteri Yönetimi", "MÜŞTERİ YÖNETİMİ", "")
        menu_item("CRM Analizi", "CRM ANALİZİ", "")
        menu_item("Servis Performansı", "SERVİS PERFORMANSI", "")
        
        # Atölye
        st.markdown('<div class="sidebar-group-title">ATÖLYE</div>', unsafe_allow_html=True)
        menu_item("Teknisyen", "SAHA EKİBİ", "")
        menu_item("İşlem Özeti", "YUKSEL_OZEL", "")
        menu_item("Bellis", "BELLIS", "")
        

        
        # Spacer (Footer'ı Alta İtmek İçin)
        st.markdown("<div style='flex-grow: 1; height: 50px;'></div>", unsafe_allow_html=True)
        
        # Footer
        layout.render_sidebar_footer(df_teklif, df_siparis)
        
    layout.render_header()
    
    # İçerik Render
    page = st.session_state.page
    
    try:
        if page == "ANA SAYFA":
            landing_page.render_landing_page(df_teklif, df_siparis, df_musteri, df_all_quotes)
            
        elif page == "SERVİS PERFORMANSI":
            integrated_dashboard.render_integrated_dashboard(df_teklif, df_siparis)
            
        elif page == "MÜŞTERİ YÖNETİMİ":
            df_urun = data_packet.get("urun", pd.DataFrame())
            customers.render_musteri(df_musteri, df_all_quotes, df_urun)
            
        elif page == "CRM ANALİZİ":
            df_crm = data_packet.get("crm", pd.DataFrame())
            if df_crm.empty and not df_siparis.empty:
                df_crm = prepare_crm_data(df_teklif, df_siparis, df_musteri)
            crm.render_crm_page(df_crm, df_teklif, df_siparis)
            
        elif page == "SAHA EKİBİ":
            field_ops.render_saha(holidays=data_packet.get("holidays"))
            

            
        elif page == "YUKSEL_OZEL":
            yuksel_ops.render_yuksel_page()
            
        elif page == "BELLIS":
            bellis.render_bellis_page()
            
    except Exception as e:
        logger.exception(f"Sayfa render hatası: {page}")
        st.error(f"Sayfa yüklenirken bir hata oluştu: {e}")
        st.info("Lütfen sayfayı yenileyin veya başka bir menü seçin.")


if __name__ == "__main__":
    main()
