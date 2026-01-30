
import streamlit as st
import pandas as pd
from config.constants import AY_KISA
from components.layout import  section_title
from components.charts import render_chartjs

def render_yearly_performance_chart(df_siparis, all_available_years, conversion_factor=1.0, sym="€"):
    """Yıllık Satış Performansı Grafiğini Render Eder."""
    
    # Başlık
    section_title("YILLIK SATIŞ PERFORMANSI", margin_top="2rem", show_border=False)
    
    st.markdown('''
    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Yılları açmak/kapatmak için yılların üzerine tıklayın</div>
    ''', unsafe_allow_html=True)
    
    # Metrik seçici (sağ tarafa hizalı)
    _, col_spacer, col_metric = st.columns([4, 1, 1])
    with col_metric:
        selected_metric = st.radio("METRİK", ["Ciro", "Kar"], index=1, horizontal=True, key="chart_metric_selector", label_visibility="collapsed")
    
    # Seçilen metriğe göre veri sütunu
    data_column = "Tutar_EUR" if selected_metric == "Ciro" else "Kar_EUR"
    
    theme = st.session_state.get("theme", "light")
    tick_color = "#9CA3AF" if theme == "dark" else "#4B5563"
    grid_color = "rgba(255, 255, 255, 0.05)" if theme == "dark" else "rgba(0, 0, 0, 0.05)"

    year_colors = [
        {"border": "#3B82F6", "bg": "rgba(59, 130, 246, 0.15)"},   # Blue
        {"border": "#10B981", "bg": "rgba(16, 185, 129, 0.15)"},   # Green
        {"border": "#F59E0B", "bg": "rgba(245, 158, 11, 0.15)"},   # Amber
        {"border": "#8B5CF6", "bg": "rgba(139, 92, 246, 0.15)"},   # Purple
        {"border": "#EF4444", "bg": "rgba(239, 68, 68, 0.15)"},    # Red
        {"border": "#EC4899", "bg": "rgba(236, 72, 153, 0.15)"},   # Pink
    ]
    
    datasets = []
    all_months = list(range(1, 13))
    chart_labels = [AY_KISA.get(m, str(m)) for m in all_months]
    default_visible_years = [2024, 2025, 2026]
    
    for idx, year in enumerate(sorted(all_available_years)):
        color_set = year_colors[idx % len(year_colors)]
        
        df_year = df_siparis[df_siparis["Yil"] == year].copy()
        year_monthly = df_year.groupby("Ay")[data_column].sum()
        year_values = [(year_monthly.get(m, 0) * conversion_factor) for m in all_months]
        
        if sum(year_values) == 0:
            continue
        
        is_hidden = year not in default_visible_years
        
        datasets.append({
            "label": f"{year}",
            "data": year_values,
            "borderColor": color_set["border"],
            "backgroundColor": color_set["bg"],
            "fill": False,
            "tension": 0.4,
            "pointRadius": 3,
            "pointHoverRadius": 5,
            "borderWidth": 2,
            "hidden": is_hidden
        })
    
    if datasets:
        line_data = {"labels": chart_labels, "datasets": datasets}
        line_options = {
            "maintainAspectRatio": False,
            "plugins": {
                "legend": {
                    "display": True,
                    "position": "top",
                    "labels": {
                        "color": tick_color,
                        "usePointStyle": True,
                        "padding": 20,
                        "font": {"family": "'Inter', 'Roboto', sans-serif", "size": 12}
                    }
                },
                "tooltip": {
                    "backgroundColor": "#1F2937" if theme == "dark" else "#FFFFFF",
                    "titleColor": "#F9FAFB" if theme == "dark" else "#111827",
                    "bodyColor": "#F9FAFB" if theme == "dark" else "#6B7280",
                    "borderColor": "rgba(255,255,255,0.1)" if theme == "dark" else "#E5E7EB",
                    "borderWidth": 1,
                    "padding": 10
                }
            },
            "scales": {
                "x": {
                    "ticks": {"color": tick_color, "font": {"family": "'Inter', 'Roboto', sans-serif"}},
                    "grid": {"color": grid_color}
                },
                "y": {
                    "ticks": {"color": tick_color, "font": {"family": "'Inter', 'Roboto', sans-serif"}},
                    "grid": {"color": grid_color},
                    "beginAtZero": True
                }
            }
        }
        render_chartjs("line", line_data, line_options, height=350, currency_symbol=sym)
    else:
        st.info("Trend verisi yok.")
