import streamlit as st
from datetime import datetime
import pandas as pd
from core.utils import get_theme_colors
from components.layout import spacer, section_title

# ============================================================================
# LOGIN AYARI - True yaparak şifre ekranını aktif edebilirsiniz
# ============================================================================
LOGIN_ENABLED = False


def render_landing_page(df_teklif: pd.DataFrame, df_siparis: pd.DataFrame, df_musteri: pd.DataFrame, df_all_quotes: pd.DataFrame = None):
    """
    Renders the main landing page with company summary and login state.
    """
    # Login ekranı (şimdilik devre dışı - LOGIN_ENABLED = True ile aktif edin)
    if LOGIN_ENABLED and not st.session_state.get("authenticated", False):
        _render_login_screen()
        return
    
    # Login devre dışıysa otomatik olarak authenticated yap
    if not LOGIN_ENABLED:
        st.session_state["authenticated"] = True

    # --- AUTHENTICATED VIEW (COMMAND CENTER) ---
    
    # Tema ayarlarını Authenticated view için de hazırla
    current_theme = st.session_state.get("theme", "light")
    is_dark = current_theme == "dark"
    
    if is_dark:
        hero_bg = "linear-gradient(to right, #1E293B, #0F172A)"
        hero_border = "rgba(255,255,255,0.1)"
        text_white = "white"
        sub_text = "#94A3B8"
    else:
        hero_bg = "linear-gradient(to right, #FFFFFF, #F3F4F6)"
        hero_border = "#E5E7EB"
        text_white = "#111827"
        sub_text = "#4B5563"
    
    # 1. HERO SECTION
    simdi = datetime.now()
    tarih_str = simdi.strftime("%d.%m.%Y")
    user_name = st.session_state.get('login_user', 'Yönetici')
    
    # Hero HTML
    # Hero HTML (CSS Classes from styles.py)
    # .hero-container css class is defined in components/styles.py
    hero_html = f"""
    <div class="hero-container" style="background: {hero_bg}; border: 1px solid {hero_border}; color: {text_white};">
        <div>
            <div style="font-size: 0.8rem; letter-spacing: 1px; color: {sub_text}; text-transform: uppercase; font-weight:600;">YÖNETİM PANELİ</div>
            <div style="font-size: 2rem; font-weight: 800; letter-spacing: -1px;">Hoş geldin, <span style="color: #EF4444;">{user_name}</span></div>
            <div style="font-size: 0.95rem; color: {sub_text}; margin-top: 0.5rem;">İşlemlerinize komuta merkezinden devam edebilirsiniz.</div>
        </div>
        <div style="text-align: right;">
            <div style="font-weight: 700; font-size: 1.2rem;">{tarih_str}</div>
            <div style="color: #10B981; font-size: 0.8rem; font-weight:600;">● Sistem Online</div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)
    
    # 2. KEY PERFORMANCE INDICATORS (PREMIUM CARDS)
    section_title("ŞİRKET ÖZETİ")
    
    from components.cards import render_kpi_card
    from config.constants import AY_MAP

    def render_landing_card(title, value, delta_val, sub_text, icon_key, color, btn_key, target_page):
         """Adapter for landing page cards using shared component"""
         st.markdown(render_kpi_card(title, value, sub_text, icon_key, color, delta=delta_val), unsafe_allow_html=True)
         if st.button(f"İncele", key=btn_key, width="stretch"):
            st.session_state.page = target_page
            st.rerun()

    # Dinamik Ay/Yıl hesaplama
    current_year = simdi.year
    current_month = simdi.month
    prev_year = current_year - 1
    
    # Ay ismi
    ay_adi = AY_MAP.get(current_month, f"Ay {current_month}")
    
    # AYLIK Veriler (Orijinal Mantık)
    if df_all_quotes is not None and not df_all_quotes.empty:
        df_tek_current = df_all_quotes[(df_all_quotes["Yil"] == current_year) & (df_all_quotes["Ay"] == current_month)]
        df_tek_prev = df_all_quotes[(df_all_quotes["Yil"] == prev_year) & (df_all_quotes["Ay"] == current_month)]
    else:
        df_tek_current = df_teklif[(df_teklif["Yil"] == current_year) & (df_teklif["Ay"] == current_month)]
        df_tek_prev = df_teklif[(df_teklif["Yil"] == prev_year) & (df_teklif["Ay"] == current_month)]
    
    df_sip_current = df_siparis[(df_siparis["Yil"] == current_year) & (df_siparis["Ay"] == current_month)]
    df_sip_prev = df_siparis[(df_siparis["Yil"] == prev_year) & (df_siparis["Ay"] == current_month)]
    
    # Sayılar (AYLIK)
    teklif_current = len(df_tek_current)
    teklif_prev = len(df_tek_prev)
    
    siparis_current = len(df_sip_current)
    siparis_prev = len(df_sip_prev)
    
    # Delta Calculation Helper
    def calc_delta(curr, prev):
        if prev == 0: return None
        return ((curr - prev) / prev) * 100
        
    delta_teklif = calc_delta(teklif_current, teklif_prev)
    delta_siparis = calc_delta(siparis_current, siparis_prev)
    
    # Müşteri Sayısı
    musteri_sayisi = len(df_musteri)
    
    # Saha Ekibi - Bugün sahada olanları hesapla (FIELD_TECHNICIANS listesinden)
    try:
        from core.data_loader import load_saha_data
        from config.constants import FIELD_TECHNICIANS
        
        # Tuple Unpack (df_saha, df_personel)
        saha_data = load_saha_data()
        if isinstance(saha_data, tuple):
            df_saha, df_personel = saha_data
        else:
            df_saha = saha_data
            df_personel = pd.DataFrame()
            
        if not df_saha.empty:
            # Bugünün tarihi ile karşılaştır
            today = simdi.date()
            df_saha_today = df_saha[
                (df_saha["Tarih"].dt.date == today) & 
                (df_saha["Durum"] == "AKTİF")
            ]
            
            # Takip edilecek teknisyen listesi (Personel sayfasından veya Fallback)
            sahada_izlenecek = set()
            if not df_personel.empty and 'Ad_Soyad' in df_personel.columns and 'Departman' in df_personel.columns:
                 # Sadece 'SAHA' departmanındakileri say
                 saha_filt = df_personel['Departman'].str.strip().str.upper() == 'SAHA'
                 sahada_izlenecek = set(df_personel[saha_filt]['Ad_Soyad'].str.upper().tolist())
            
            if not sahada_izlenecek:
                 # Fallback: Sabit liste
                 sahada_izlenecek = set([t.upper() for t in FIELD_TECHNICIANS])
            
            sahada_set = set()
            for _, row in df_saha_today.iterrows():
                tek1 = str(row.get('Teknisyen 1', '')).strip().upper()
                if tek1 and tek1 in sahada_izlenecek:
                    sahada_set.add(tek1)
                tek2 = str(row.get('Teknisyen 2', '')).strip().upper()
                if tek2 and tek2 in sahada_izlenecek:
                    sahada_set.add(tek2)
            
            sahada_sayisi = len(sahada_set)
        else:
            sahada_sayisi = 0
    except:
        sahada_sayisi = 0
    
    # Grid
    c1, c2, c3, c4 = st.columns(4, gap="large")
    
    with c1:
        render_landing_card(
            f"{ay_adi.upper()} TEKLİF", 
            f"{teklif_current}", 
            delta_teklif, 
            f"{prev_year} aynı aya göre" if delta_teklif else "Karşılaştırma yok", 
            "clipboard", 
            "#F59E0B", 
            "lnd_btn_1", 
            "SERVİS PERFORMANSI"
        )
        
    with c2:
        render_landing_card(
            f"{ay_adi.upper()} SİPARİŞ", 
            f"{siparis_current}", 
            delta_siparis, 
            f"{prev_year} aynı aya göre" if delta_siparis else "Karşılaştırma yok", 
            "check-circle", 
            "#10B981", 
            "lnd_btn_2", 
            "SERVİS PERFORMANSI"
        )
        
    with c3:
        render_landing_card(
            "SAHADA", 
            f"{sahada_sayisi}", 
            None, 
            "Bugün aktif teknisyen", 
            "wrench", 
            "#6366F1", 
            "lnd_btn_3", 
            "SAHA EKİBİ"
        )
        
    with c4:
        render_landing_card(
            "MÜŞTERİLER", 
            f"{musteri_sayisi}", 
            None, 
            "Toplam kayıtlı firma", 
            "users", 
            "#3B82F6", 
            "lnd_btn_4", 
            "MÜŞTERİ YÖNETİMİ"
        )
        
    # 4. FOOTER NOTE
    st.markdown(f"""
    <div style="margin-top: 3rem; text-align: center; color: #9CA3AF; font-size: 0.8rem; border-top: 1px solid #E5E7EB; padding-top: 1rem;">
        DHE Endüstriyel © {current_year}
    </div>
    """, unsafe_allow_html=True)
