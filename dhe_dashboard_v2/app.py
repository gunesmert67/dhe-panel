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

# =============================================================================
# STREAMLIT CLOUD CREDENTIAL YÖNETİMİ
# =============================================================================
# Bu kod hem local hem cloud ortamında çalışır:
# - Local: Mevcut data/credentials.json kullanılır
# - Cloud: st.secrets'tan okunup dosya oluşturulur

def _setup_cloud_credentials():
    """Streamlit Cloud için credential dosyasını oluşturur."""
    # Data klasörünü oluştur
    os.makedirs("data", exist_ok=True)
    
    # Eğer secrets'ta credential varsa dosyaya yaz
    if "dosyalar" in st.secrets and "gcp_json" in st.secrets["dosyalar"]:
        json_content = st.secrets["dosyalar"]["gcp_json"]
        
        credential_path = "data/credentials.json"
        # Dosya yoksa veya boşsa oluştur
        if not os.path.exists(credential_path) or os.path.getsize(credential_path) == 0:
            with open(credential_path, "w", encoding="utf-8") as f:
                f.write(json_content)

# Credential setup (Cloud ortamında çalışır, local'de atlanır)
try:
    _setup_cloud_credentials()
except Exception:
    pass  # Local ortamda secrets olmayabilir, sorun değil

# Core Imports
from core.data_loader import load_data, prepare_crm_data, load_holidays
from core.bellis_loader import load_bellis_data, load_sehirler_data

# View Imports
from views import (
    landing_page, 
    crm, 
    customers, 
    field_ops,
    integrated_dashboard,
    islem_ozeti,
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

# LOGIN AYARI
LOGIN_ENABLED = True

def _render_login_screen():
    """Basit giriş ekranı."""
    # === STYLE INJECTION REMOVED (Handled Globally) ===
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 10px;">
                <img src="https://dhe.com.tr/wp-content/uploads/2023/08/logo_dhe.png" width="150">
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; margin-bottom: 20px; font-size: 24px; font-weight: bold;'>Teknik Servis Yönetim Paneli Giriş</div>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Kullanıcı Adı", placeholder="servis")
            password = st.text_input("Şifre", type="password", placeholder="******")
            submit = st.form_submit_button("Giriş Yap", type="primary", use_container_width=True)
            
            if submit:
                if username.strip() == "servis" and password.strip() == "dhe2026":
                    st.session_state["authenticated"] = True
                    st.session_state["login_user"] = "Servis Yöneticisi"
                    st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                    st.rerun()
                else:
                    st.error("Hatalı kullanıcı adı veya şifre!")
    
    st.stop()


def main():
    styles.inject_css()
    
    # Session State Başlatma
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        
    # GLOBAL LOGIN CHECK
    if LOGIN_ENABLED and not st.session_state["authenticated"]:
        _render_login_screen()
        return

    if not LOGIN_ENABLED:
        st.session_state["authenticated"] = True
        
    if "page" not in st.session_state:
        st.session_state.page = "ANA SAYFA"

    # Veri Yükleme
    # Not: Progress callback kullanmıyoruz - Streamlit rerun'da closure sorunu yaratıyordu
    with st.spinner("Veriler yükleniyor..."):
        try:
            data_packet = load_data(_progress_callback=None)
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
        menu_item("İşlem Özeti", "ISLEM_OZETI", "")
        menu_item("Bellis", "BELLIS", "")
        

        
        # Spacer (Footer'ı Alta İtmek İçin)
        st.markdown("<div style='flex-grow: 1; height: 50px;'></div>", unsafe_allow_html=True)
        
        # Footer
        layout.render_sidebar_footer(df_teklif, df_siparis)
        
        # Logout Butonu
        if st.session_state.get("authenticated", False):
            st.markdown("---")
            if st.button("🔒 Çıkış Yap", key="logout_btn", type="secondary", width="stretch"):
                st.session_state["authenticated"] = False
                st.rerun()
        
    layout.render_header()
    
    # İçerik Render
    page = st.session_state.page
    
    try:
        if page == "ANA SAYFA":
            landing_page.render_landing_page(df_teklif, df_siparis, df_musteri, df_all_quotes, data_packet=data_packet)
            
        elif page == "SERVİS PERFORMANSI":
            integrated_dashboard.render_integrated_dashboard(df_teklif, df_siparis, df_all_quotes)
            
        elif page == "MÜŞTERİ YÖNETİMİ":
            df_urun = data_packet.get("urun", pd.DataFrame())
            customers.render_musteri(df_musteri, df_all_quotes, df_urun)
            
        elif page == "CRM ANALİZİ":
            df_crm = data_packet.get("crm", pd.DataFrame())
            if df_crm.empty and not df_siparis.empty:
                df_crm = prepare_crm_data(df_teklif, df_siparis, df_musteri)
            crm.render_crm_page(df_crm, df_teklif, df_siparis)
            
        elif page == "SAHA EKİBİ":
            field_ops.render_saha(holidays=data_packet.get("holidays"), data_packet=data_packet)
            

            
        elif page == "ISLEM_OZETI":
            islem_ozeti.render_islem_ozeti_page(data_packet=data_packet)
            
        elif page == "BELLIS":
            bellis.render_bellis_page()
            
    except Exception as e:
        logger.exception(f"Sayfa render hatası: {page}")
        st.error(f"Sayfa yüklenirken bir hata oluştu: {e}")
        st.info("Lütfen sayfayı yenileyin veya başka bir menü seçin.")


if __name__ == "__main__":
    main()
