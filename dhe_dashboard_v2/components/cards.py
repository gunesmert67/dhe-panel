import streamlit as st
from typing import Union, Optional

# --- SVG ICONS REPOSITORY ---
# Centralized icon definitions to be used across the app
SVG_ICONS = {
    "chart": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='12' y1='20' x2='12' y2='10'%3E%3C/line%3E%3Cline x1='18' y1='20' x2='18' y2='4'%3E%3C/line%3E%3Cline x1='6' y1='20' x2='6' y2='16'%3E%3C/line%3E%3C/svg%3E",
    "trending-up": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='23 6 13.5 15.5 8.5 10.5 1 18'%3E%3C/polyline%3E%3Cpolyline points='17 6 23 6 23 12'%3E%3C/polyline%3E%3C/svg%3E",
    "check-circle": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M22 11.08V12a10 10 0 1 1-5.93-9.14'%3E%3C/path%3E%3Cpolyline points='22 4 12 14.01 9 11.01'%3E%3C/polyline%3E%3C/svg%3E",
    "clipboard": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2'%3E%3C/path%3E%3Crect x='8' y='2' width='8' height='4' rx='1' ry='1'%3E%3C/rect%3E%3C/svg%3E",
    "users": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'%3E%3C/path%3E%3Ccircle cx='9' cy='7' r='4'%3E%3C/circle%3E%3Cpath d='M23 21v-2a4 4 0 0 0-3-3.87'%3E%3C/path%3E%3Cpath d='M16 3.13a4 4 0 0 1 0 7.75'%3E%3C/path%3E%3C/svg%3E",
    "user-check": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'%3E%3C/path%3E%3Ccircle cx='8.5' cy='7' r='4'%3E%3C/circle%3E%3Cpolyline points='17 11 19 13 23 9'%3E%3C/polyline%3E%3C/svg%3E",
    "user-x": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'%3E%3C/path%3E%3Ccircle cx='8.5' cy='7' r='4'%3E%3C/circle%3E%3Cline x1='18' y1='8' x2='23' y2='13'%3E%3C/line%3E%3Cline x1='23' y1='8' x2='18' y2='13'%3E%3C/line%3E%3C/svg%3E",
    "wrench": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z'%3E%3C/path%3E%3C/svg%3E",
    "alert-triangle": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'%3E%3C/path%3E%3Cline x1='12' y1='9' x2='12' y2='13'%3E%3C/line%3E%3Cline x1='12' y1='17' x2='12.01' y2='17'%3E%3C/line%3E%3C/svg%3E",
    "trophy": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9H4.5a2.5 2.5 0 0 1 0-5H6'%3E%3C/path%3E%3Cpath d='M18 9h1.5a2.5 2.5 0 0 0 0-5H18'%3E%3C/path%3E%3Cpath d='M4 22h16'%3E%3C/path%3E%3Cpath d='M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22'%3E%3C/path%3E%3Cpath d='M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22'%3E%3C/path%3E%3Cpath d='M18 2H6v7a6 6 0 0 0 12 0V2Z'%3E%3C/path%3E%3C/svg%3E",
    "medal": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='8' r='7'%3E%3C/circle%3E%3Cpolyline points='8.21 13.89 7 23 12 20 17 23 15.79 13.88'%3E%3C/polyline%3E%3C/svg%3E",
    "clock": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'%3E%3C/circle%3E%3Cpolyline points='12 6 12 12 16 14'%3E%3C/polyline%3E%3C/svg%3E",
    "tool": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z'%3E%3C/path%3E%3C/svg%3E",
    "alert": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z'%3E%3C/path%3E%3Cline x1='12' y1='9' x2='12' y2='13'%3E%3C/line%3E%3Cline x1='12' y1='17' x2='12.01' y2='17'%3E%3C/line%3E%3C/svg%3E",
    "settings": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='3'%3E%3C/circle%3E%3Cpath d='M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z'%3E%3C/path%3E%3C/svg%3E",
    "zap": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolygon points='13 2 3 14 12 14 11 22 21 10 12 10 13 2'%3E%3C/polygon%3E%3C/svg%3E",
    "search": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'%3E%3C/circle%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'%3E%3C/line%3E%3C/svg%3E",
    "briefcase": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='2' y='7' width='20' height='14' rx='2' ry='2'%3E%3C/rect%3E%3Cpath d='M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16'%3E%3C/path%3E%3C/svg%3E",
    "truck": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='1' y='3' width='15' height='13'%3E%3C/rect%3E%3Cpolygon points='16 8 20 8 23 11 23 16 16 16 16 8'%3E%3C/polygon%3E%3Ccircle cx='5.5' cy='18.5' r='2.5'%3E%3C/circle%3E%3Ccircle cx='18.5' cy='18.5' r='2.5'%3E%3C/circle%3E%3C/svg%3E",
    "home": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'%3E%3C/path%3E%3Cpolyline points='9 22 9 12 15 12 15 22'%3E%3C/polyline%3E%3C/svg%3E",
    "coffee": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M18 8h1a4 4 0 0 1 0 8h-1'%3E%3C/path%3E%3Cpath d='M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z'%3E%3C/path%3E%3Cline x1='6' y1='1' x2='6' y2='4'%3E%3C/line%3E%3Cline x1='10' y1='1' x2='10' y2='4'%3E%3C/line%3E%3Cline x1='14' y1='1' x2='14' y2='4'%3E%3C/line%3E%3C/svg%3E",
    "calendar": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='18' rx='2' ry='2'%3E%3C/rect%3E%3Cline x1='16' y1='2' x2='16' y2='6'%3E%3C/line%3E%3Cline x1='8' y1='2' x2='8' y2='6'%3E%3C/line%3E%3Cline x1='3' y1='10' x2='21' y2='10'%3E%3C/line%3E%3C/svg%3E",
    "activity": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='22 12 18 12 15 21 9 3 6 12 2 12'%3E%3C/polyline%3E%3C/svg%3E"
}


def render_kpi_card(title: str, value: Union[str, int, float], sub: str, icon_key: str, color: str, delta: float = None) -> str:
    """
    Premium KPI Card - Steve Jobs Edition
    Clean, minimal, functional.
    """
    icon_url = SVG_ICONS.get(icon_key, "")
    
    # Delta Badge
    delta_html = ""
    if delta is not None:
        is_positive = delta >= 0
        d_color = "var(--success)" if is_positive else "var(--error)"
        d_bg = "rgba(16, 185, 129, 0.1)" if is_positive else "rgba(239, 68, 68, 0.1)"
        d_arrow = "↑" if is_positive else "↓"
        delta_html = f'''<span style="
            color: {d_color}; 
            font-weight: 600; 
            background: {d_bg}; 
            padding: 4px 8px; 
            border-radius: 6px; 
            font-size: 0.75rem; 
            margin-right: 8px;
            font-feature-settings: 'tnum' 1;
        ">{d_arrow} {abs(delta):.1f}%</span>'''
    
    # Icon
    if icon_url:
        icon_html = f'''<div style="
            width: 40px; 
            height: 40px; 
            background: {color}12; 
            border-radius: 10px; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            flex-shrink: 0;
        "><div style="
            background-color: {color}; 
            width: 20px; 
            height: 20px; 
            -webkit-mask-image: url('{icon_url}'); 
            -webkit-mask-size: contain; 
            -webkit-mask-repeat: no-repeat; 
            -webkit-mask-position: center;
        "></div></div>'''
    else:
        # Icon bulunamadıysa renkli kare göster
        icon_html = f'''<div style="
            width: 40px; 
            height: 40px; 
            background: {color}; 
            border-radius: 10px; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            flex-shrink: 0;
        "></div>'''

    html = f'''<div style="
        background: var(--card-bg); 
        border-radius: 12px; 
        padding: 24px; 
        border: 1px solid var(--border-color); 
        border-left: 4px solid {color}; 
        box-shadow: var(--shadow-sm); 
        height: 100%; 
        display: flex; 
        flex-direction: column; 
        gap: 16px;
        transition: all 200ms ease;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="
                font-size: 0.8rem; 
                font-weight: 600; 
                color: var(--text-secondary); 
                letter-spacing: 0.04em; 
                text-transform: uppercase;
            ">{title}</div>
            {icon_html}
        </div>
        <div>
            <div style="
                font-size: 2.25rem; 
                font-weight: 800; 
                color: var(--text-primary); 
                line-height: 1.1;
                font-feature-settings: 'tnum' 1;
                letter-spacing: -0.02em;
            ">{value}</div>
            <div style="
                font-size: 0.85rem; 
                color: var(--text-muted); 
                margin-top: 8px;
                display: flex; 
                align-items: center; 
                flex-wrap: wrap;
            ">{delta_html}<span>{sub}</span></div>
        </div>
    </div>'''
    return html.replace('\n', '').strip()


def render_perf_card(name: str, tutar_fmt: str, kar_fmt: str, progress_pct: float) -> str:
    """
    Premium Personnel Performance Card
    Clean avatar, progress bar, key metrics.
    """
    # Güvenli initials hesaplama
    name_parts = name.split()[:2] if name else []
    initials = "".join([n[0] for n in name_parts if n]).upper() or "?"
    
    # Varsayılan renk (Mavi)
    avatar_bg = "#3B82F6"
    
    html = f'''<div style="
        background: var(--card-bg); 
        border: 1px solid var(--border-color); 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 16px;
        display: flex; 
        flex-direction: column; 
        gap: 16px; 
        height: calc(100% - 16px); 
        box-shadow: var(--shadow-sm);
        transition: all 200ms ease;
    ">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="
                width: 44px; 
                height: 44px; 
                border-radius: 12px; 
                background: linear-gradient(135deg, {avatar_bg}, {avatar_bg}dd); 
                color: white; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-weight: 700; 
                font-size: 0.9rem;
                flex-shrink: 0;
            ">{initials}</div>
            <div style="flex: 1; min-width: 0;">
                <div style="
                    font-weight: 700; 
                    color: var(--text-primary); 
                    font-size: 0.95rem; 
                    white-space: nowrap; 
                    overflow: hidden; 
                    text-overflow: ellipsis;
                ">{name}</div>
                <div style="
                    font-size: 0.75rem; 
                    color: var(--text-muted);
                ">Teknik Servis</div>
            </div>
        </div>
        <div>
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                <div style="
                    font-size: 1.25rem; 
                    font-weight: 800; 
                    color: var(--text-primary);
                    font-feature-settings: 'tnum' 1;
                ">{tutar_fmt}</div>
                <div style="
                    font-size: 1.25rem; 
                    font-weight: 800; 
                    color: var(--success);
                    background: rgba(16, 185, 129, 0.1);
                    padding: 2px 8px;
                    border-radius: 4px;
                ">{kar_fmt}</div>
            </div>
            <div style="
                width: 100%; 
                height: 6px; 
                background: var(--bg-secondary); 
                border-radius: 3px; 
                overflow: hidden;
            ">
                <div style="
                    width: {min(progress_pct, 100)}%; 
                    height: 100%; 
                    background: linear-gradient(90deg, {avatar_bg} 0%, {avatar_bg}cc 100%); 
                    border-radius: 3px;
                    transition: width 500ms ease;
                "></div>
            </div>
        </div>
    </div>'''
    return html.replace('\n', '').strip()


def card(title: str, value: Union[str, int, float], sub: Optional[str] = None, delta: float = None) -> str:
    """Legacy wrapper for simple cards."""
    return render_kpi_card(title, value, sub if sub else "", "chart", "#3B82F6", delta)


def render_conversion_card(name: str, teklif_count: int, siparis_count: int, musteri_count: int, conversion_rate: float) -> str:
    """
    Premium Conversion Performance Card - Steve Jobs Edition
    Shows quote/order counts, customer count, and conversion rate with circular progress.
    """
    # Güvenli initials hesaplama
    name_parts = name.split()[:2] if name else []
    initials = "".join([n[0] for n in name_parts if n]).upper() or "?"
    
    # Varsayılan renkler
    avatar_bg = "#3B82F6"  # Mavi (Blue-500)
    ring_color = "#3B82F6"
    
    # Dönüşüm oranı için renk
    if conversion_rate >= 50:
        rate_color = "#10B981"  # Yeşil
    elif conversion_rate >= 25:
        rate_color = "#F59E0B"  # Turuncu
    else:
        rate_color = "#EF4444"  # Kırmızı
    
    # Circular progress için SVG parametreleri
    radius = 32
    circumference = 2 * 3.14159 * radius
    progress_offset = circumference - (conversion_rate / 100 * circumference)
    
    html = f'''<div style="
        background: var(--card-bg); 
        border: 1px solid var(--border-color); 
        border-radius: 16px; 
        padding: 24px; 
        margin-bottom: 16px;
        display: flex; 
        flex-direction: column; 
        gap: 20px; 
        height: calc(100% - 16px); 
        box-shadow: var(--shadow-sm);
        transition: all 200ms ease;
        position: relative;
        overflow: hidden;
    ">
        <!-- Subtle gradient overlay -->
        <div style="
            position: absolute;
            top: 0;
            right: 0;
            width: 120px;
            height: 120px;
            background: radial-gradient(circle at top right, {avatar_bg}08, transparent 70%);
            pointer-events: none;
        "></div>
        
        <!-- Header: Avatar + Name + Circular Progress -->
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="
                    width: 48px; 
                    height: 48px; 
                    border-radius: 14px; 
                    background: linear-gradient(135deg, {avatar_bg}, {avatar_bg}cc); 
                    color: white; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    font-weight: 700; 
                    font-size: 1rem;
                    flex-shrink: 0;
                    box-shadow: 0 4px 12px {avatar_bg}40;
                ">{initials}</div>
                <div>
                    <div style="
                        font-weight: 700; 
                        color: var(--text-primary); 
                        font-size: 1rem; 
                        line-height: 1.3;
                    ">{name}</div>
                    <div style="
                        font-size: 0.72rem; 
                        color: var(--text-muted);
                        font-weight: 500;
                    ">Teknik Servis</div>
                </div>
            </div>
            
            <!-- Circular Progress for Conversion Rate -->
            <div style="position: relative; width: 72px; height: 72px;">
                <svg width="72" height="72" viewBox="0 0 72 72" style="transform: rotate(-90deg);">
                    <circle cx="36" cy="36" r="{radius}" fill="none" stroke="var(--bg-secondary)" stroke-width="5"/>
                    <circle cx="36" cy="36" r="{radius}" fill="none" stroke="{rate_color}" stroke-width="5" 
                        stroke-dasharray="{circumference}" stroke-dashoffset="{progress_offset}" 
                        stroke-linecap="round" style="transition: stroke-dashoffset 0.5s ease;"/>
                </svg>
                <div style="
                    position: absolute; 
                    top: 50%; 
                    left: 50%; 
                    transform: translate(-50%, -50%);
                    text-align: center;
                ">
                    <div style="font-size: 0.95rem; font-weight: 800; color: {rate_color}; line-height: 1;">{conversion_rate:.0f}%</div>
                    <div style="font-size: 0.55rem; color: var(--text-muted); font-weight: 600; margin-top: 1px;">DÖNÜŞÜM</div>
                </div>
            </div>
        </div>
        
        <!-- Metrics Grid -->
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
            <!-- Teklif -->
            <div style="
                background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(245, 158, 11, 0.04));
                border-radius: 12px;
                padding: 14px 12px;
                text-align: center;
                border: 1px solid rgba(245, 158, 11, 0.15);
            ">
                <div style="font-size: 1.5rem; font-weight: 800; color: #F59E0B; line-height: 1;">{teklif_count}</div>
                <div style="font-size: 0.65rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; margin-top: 4px; letter-spacing: 0.5px;">Teklif</div>
            </div>
            
            <!-- Sipariş -->
            <div style="
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(16, 185, 129, 0.04));
                border-radius: 12px;
                padding: 14px 12px;
                text-align: center;
                border: 1px solid rgba(16, 185, 129, 0.15);
            ">
                <div style="font-size: 1.5rem; font-weight: 800; color: #10B981; line-height: 1;">{siparis_count}</div>
                <div style="font-size: 0.65rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; margin-top: 4px; letter-spacing: 0.5px;">Sipariş</div>
            </div>
            
            <!-- Müşteri -->
            <div style="
                background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(99, 102, 241, 0.04));
                border-radius: 12px;
                padding: 14px 12px;
                text-align: center;
                border: 1px solid rgba(99, 102, 241, 0.15);
            ">
                <div style="font-size: 1.5rem; font-weight: 800; color: #6366F1; line-height: 1;">{musteri_count}</div>
                <div style="font-size: 0.65rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; margin-top: 4px; letter-spacing: 0.5px;">Müşteri</div>
            </div>
        </div>
    </div>'''
    return html.replace('\n', '').strip()


# Compatibility aliases
premium_card = render_kpi_card
perf_card = render_perf_card
conversion_card = render_conversion_card
