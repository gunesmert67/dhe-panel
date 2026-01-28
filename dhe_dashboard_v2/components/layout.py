import streamlit as st
from datetime import datetime
import os
import pandas as pd

def render_header():
    tarih = datetime.now().strftime("%d.%m.%Y")
    st.markdown(f"""<div class="main-header">
        <div class="header-title">DHE ENDÜSTRİYEL <span style="color:var(--accent-neon)">///</span> YÖNETİM PORTALI</div>
        <div class="header-date">{tarih}</div>
    </div>""", unsafe_allow_html=True)

def render_sidebar_header():
    # Artık app.py içinde custom markdown ile yönetiliyor
    pass

import textwrap

def render_sidebar_footer(df_teklif: pd.DataFrame, df_siparis: pd.DataFrame):
    """
    Renders the sidebar footer with developer options.
    """
    st.sidebar.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
    
    # Sabit tema renkleri (her zaman light mode)
    title_color = "#374151"
    text_color = "#111827"
    muted_color = "#6B7280"
    card_bg = "rgba(0,0,0,0.04)"
    border_color = "rgba(0,0,0,0.08)"

    with st.sidebar.expander("Sistem Bilgisi", expanded=False):
        # Veri Kaynakları - Sadece İsimler
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <div style="font-size: 0.72rem; color: {title_color}; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 0.6rem;">
                Veri Kaynakları
            </div>
            <div style="background: {card_bg}; border-radius: 6px; padding: 0.5rem 0.75rem; margin-bottom: 0.4rem;">
                <div style="font-size: 0.8rem; font-weight: 600; color: {text_color};">DHE_Data</div>
            </div>
            <div style="background: {card_bg}; border-radius: 6px; padding: 0.5rem 0.75rem;">
                <div style="font-size: 0.8rem; font-weight: 600; color: {text_color};">2025 SERVİS PROGRAMI</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Yenile Butonu
        if st.button("Verileri Yenile", key="refresh_data_btn_inner", type="primary", width="stretch", help="Google Sheets'ten verileri tekrar çeker"):
            st.cache_data.clear()
            st.rerun()
            
        st.markdown(f"""
        <div style="font-size: 0.68rem; color: {muted_color}; text-align: center; margin-top: 0.4rem;">
            Manuel Kontrol (Oto-Yenileme Kapalı)
        </div>
        """, unsafe_allow_html=True)
            

            
    # Footer Metni (Sadece Copyright)
    footer_color = "#9CA3AF"
    label_color_global = "#6B7280"
    
    st.sidebar.markdown(f"""
        <div style="text-align: center; margin-top: 20px; font-size: 0.68rem; color: {footer_color};">
            DHE Endüstriyel © 2026<br>
            <span style="color: {label_color_global};">Designed by Mert</span>
        </div>
    """, unsafe_allow_html=True)


# =============================================================================
# UI HELPER FONKSİYONLARI
# =============================================================================

def spacer(height: int = 20):
    """
    Dikey boşluk ekler.
    
    Args:
        height: Piksel cinsinden yükseklik (varsayılan: 20)
    """
    st.markdown(f"<div style='height: {height}px; clear: both;'></div>", unsafe_allow_html=True)


def section_title(title: str, margin_top: str = "2rem", margin_bottom: str = "1rem", show_border: bool = True):
    """
    Bölüm başlığı render eder.
    
    Args:
        title: Başlık metni
        margin_top: Üst boşluk (CSS değeri)
        margin_bottom: Alt boşluk (CSS değeri)
        show_border: Altındaki çizginin gösterilip gösterilmeyeceği
    """
    border_style = "" if show_border else "border-bottom: none !important;"
    st.markdown(f'<div class="section-title" style="margin-top:{margin_top};margin-bottom:{margin_bottom};{border_style}">{title}</div>', unsafe_allow_html=True)


def render_badge(value: int, label: str = "KAYIT"):
    """
    Sayı badge'i render eder.
    
    Args:
        value: Gösterilecek sayı
        label: Badge etiketi
    
    Returns:
        str: HTML string
    """
    from core.utils import get_theme_colors
    colors = get_theme_colors()
    
    return f"""
    <div style="margin-top: 2px; background: {colors['badge_bg']}; padding: 0.4rem 1rem; border-radius: 6px; display: inline-flex; align-items: center; gap: 8px; border: 1px solid {colors['badge_border']}; white-space: nowrap; height: 38px;">
        <span style="font-size: 1rem; font-weight: 700; color: {colors['badge_text']}; line-height: 1;">{value:,}</span>
        <span style="font-size: 0.7rem; color: {colors['badge_text']}; opacity: 0.8; text-transform: uppercase; font-weight: 600;">{label}</span>
    </div>
    """.replace(",", ".")
