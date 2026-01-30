"""
DHE Dashboard - Bellis Sayfası
==============================
Bellis makine veritabanı görselleştirmesi.
Türkiye haritası, KPI kartları ve detay tablosu.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict

from core.bellis_loader import load_bellis_data, load_sehirler_data, prepare_bellis_summary
from config.city_coordinates import SERVICE_PROVIDER_COLORS, TURKEY_REGIONS
from components.cards import render_kpi_card


def render_bellis_page(df_sehirler: pd.DataFrame = None):
    """Ana Bellis sayfası render fonksiyonu."""
    
    # Veri Yükleme
    df_bellis = load_bellis_data()
    
    if df_sehirler is None or df_sehirler.empty:
        df_sehirler = load_sehirler_data()
    
    if df_bellis.empty:
        st.error("Bellis verileri yüklenemedi. Lütfen data/Bellis.xlsx dosyasını kontrol edin.")
        return
    
    # Veri Zenginleştirme
    df_enriched, kpis = prepare_bellis_summary(df_bellis, df_sehirler)
    
    # === TAB STYLE INJECTION ===
    # === TAB STYLE INJECTION REMOVED (Handled Globally) ===
    
    # === TAB YAPISI ===
    tab_veriler, tab_liste = st.tabs(["BELLIS MAKINE VERILERI", "DETAYLI MAKINE LISTESI"])
    
    # === TAB 1: VERİ GÖRSELLEŞTİRME ===
    with tab_veriler:
        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
        
        # =========================================================================
        # KPI KARTLARI
        # =========================================================================
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(render_kpi_card(
                title="Toplam Makine",
                value=f"{kpis.get('total', 0):,}",
                sub="Bellis veritabanı",
                icon_key="settings",
                color="#1E293B"
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(render_kpi_card(
                title="DHE Servisinde",
                value=f"{kpis.get('dhe', 0):,}",
                sub="Bizim müşterilerimiz",
                icon_key="wrench",
                color="#C4121F"
            ), unsafe_allow_html=True)
        
        with col3:
            market_share = kpis.get('market_share', 0)
            st.markdown(render_kpi_card(
                title="Pazar Payımız",
                value=f"%{market_share}",
                sub="DHE / Toplam",
                icon_key="chart",
                color="#10B981"
            ), unsafe_allow_html=True)
        
        with col4:
            # Sadece TR içi (İller listesinde olanlar)
            turkiye_count = kpis.get('is_turkey', 0)
            st.markdown(render_kpi_card(
                title="Türkiye'de",
                value=f"{turkiye_count:,}",
                sub="Yurt İçi Makineler",
                icon_key="truck",
                color="#3B82F6"
            ), unsafe_allow_html=True)
        
        st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
        
        # =========================================================================
        # TÜRKİYE HARİTASI (Tam Genişlik)
        # =========================================================================
        st.markdown("""
        <div class="section-title">
            TÜRKİYE HARİTASI
        </div>
        """, unsafe_allow_html=True)
        
        render_turkey_map(kpis.get("city_summary", pd.DataFrame()))
        
        st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
        
        # =========================================================================
        # BÖLGE DAĞILIMI VE SERVİS DAĞILIMI (Yan Yana)
        # =========================================================================
        col_region, col_service = st.columns(2)
        
        with col_region:
            st.markdown("""
            <div class="section-title">
                BÖLGE DAĞILIMI
            </div>
            """, unsafe_allow_html=True)
            
            render_region_chart(df_enriched)
        
        with col_service:
            st.markdown("""
            <div class="section-title">
                SERVİS DAĞILIMI
            </div>
            """, unsafe_allow_html=True)
            
            render_service_pie_chart(kpis.get("service_distribution", {}))
    
    # === TAB 2: DETAY TABLOSU ===
    with tab_liste:
        st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)
        render_detail_table(df_enriched)


def render_turkey_map(city_summary: pd.DataFrame):
    """Türkiye haritası üzerinde şehir bazlı scatter map."""
    
    if city_summary.empty:
        st.info("Harita için veri bulunamadı.")
        return
    
    # Plotly Scatter Mapbox
    # Plotly Scatter Mapbox
    fig = px.scatter_mapbox(
        city_summary,
        lat="Enlem",
        lon="Boylam",
        # size="Toplam" kaldırıldı (Eşit büyüklük istendi)
        color="DHE_Oran",
        hover_name="Sehir",
        hover_data={
            "Toplam": True,
            "DHE": True,
            "DHE_Oran": ":.1f",
            "Enlem": False,
            "Boylam": False
        },
        color_continuous_scale=[
            [0, "#FCD34D"],      # Sarı (0% DHE)
            [0.5, "#F97316"],    # Turuncu
            [1, "#C4121F"]       # Kırmızı (100% DHE)
        ],
        zoom=5,
        center={"lat": 39.0, "lon": 35.0},
    )
    
    # Custom Hover Template (HTML) - Minified for safety
    # Custom Hover Template (HTML) - Simplified for robustness
    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "<span style='color: #cbd5e1;'>──────────</span><br>"
            "<span style='color: #64748b;'>Toplam:</span> <b>%{customdata[0]}</b><br>"
            "<span style='color: #64748b;'>DHE:</span> <b style='color: #C4121F;'>%{customdata[1]}</b><br>"
            "<span style='color: #64748b;'>Pazar Payı:</span> <b style='color: #10B981;'>%{customdata[2]:.1f}%</b>"
            "<extra></extra>"
        )
    )
    
    # Marker size sabit olsun
    fig.update_traces(marker=dict(size=12))
    
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=450,
        coloraxis_colorbar=dict(
            title="DHE %",
            ticksuffix="%"
        ),
        # Tooltip Genel Stili
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Inter, system-ui, sans-serif",
            bordercolor="#e2e8f0",
            align="left"
        )
    )
    
    st.plotly_chart(fig, width='stretch')


def render_service_pie_chart(service_dist: Dict):
    """Servis sağlayıcı dağılımı pasta grafik."""
    
    if not service_dist:
        st.info("Servis dağılımı verisi bulunamadı.")
        return
    
    # Veriyi DataFrame'e çevir
    df_pie = pd.DataFrame([
        {"Servisci": k, "Adet": v} 
        for k, v in service_dist.items()
    ])
    
    # Renkleri eşleştir
    colors = [SERVICE_PROVIDER_COLORS.get(s, "#9CA3B8") for s in df_pie["Servisci"]]
    
    fig = go.Figure(data=[go.Pie(
        labels=df_pie["Servisci"],
        values=df_pie["Adet"],
        hole=0.4,
        marker_colors=colors,
        textposition='outside',
        textinfo='label+percent',
        hovertemplate=(
            "<b>%{label}</b><br>"
            "<span style='color: #cbd5e1;'>──────────</span><br>"
            "<span style='color: #64748b;'>Makine:</span> <b>%{value}</b><br>"
            "<span style='color: #64748b;'>Oran:</span> <b>%{percent}</b>"
            "<extra></extra>"
        )
    )])
    
    fig.update_layout(
        showlegend=False,
        margin={"r": 20, "t": 20, "l": 20, "b": 20},
        height=350,
        annotations=[dict(
            text=f"<b>{sum(service_dist.values())}</b><br>Makine",
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False
        )],
        # Premium Tooltip Style
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Inter, system-ui, sans-serif",
            bordercolor="#e2e8f0",
            align="left"
        )
    )
    
    st.plotly_chart(fig, width='stretch')


def render_region_chart(df: pd.DataFrame):
    """Bölge bazlı yatay bar chart."""
    
    if df.empty or "Bolge_Ad" not in df.columns:
        st.info("Bölge verisi bulunamadı.")
        return
    
    # Bölge özeti
    region_summary = df.groupby("Bolge_Ad").agg(
        Toplam=("Musteri", "count"),
        DHE=("Servisci", lambda x: (x == "DHE").sum())
    ).reset_index()
    
    region_summary["Diger"] = region_summary["Toplam"] - region_summary["DHE"]
    region_summary = region_summary.sort_values("Toplam", ascending=True)
    
    # Stacked horizontal bar
    fig = go.Figure()
    
    # Common hover template for bars
    def get_template(label_tr):
        return (
            "<b>%{y}</b><br>"
            "<span style='color: #cbd5e1;'>──────────</span><br>"
            f"<span style='color: #64748b;'>{label_tr}:</span> <b>%{{x}}</b>"
            "<extra></extra>"
        )
    
    # DHE ilk sırada (sol tarafta)
    fig.add_trace(go.Bar(
        y=region_summary["Bolge_Ad"],
        x=region_summary["DHE"],
        name="DHE",
        orientation='h',
        marker_color="#C4121F",
        text=region_summary["DHE"],
        textposition='inside',
        textfont=dict(color='white'),
        hovertemplate=get_template("DHE Makineleri")
    ))
    
    # Diğer (sağ tarafta, sarı renk)
    fig.add_trace(go.Bar(
        y=region_summary["Bolge_Ad"],
        x=region_summary["Diger"],
        name="Diğer",
        orientation='h',
        marker_color="#F59E0B",  # Sarı/turuncu
        text=region_summary["Diger"],
        textposition='inside',
        textfont=dict(color='white'),
        hovertemplate=get_template("Diğer Makineler")
    ))
    
    fig.update_layout(
        barmode='stack',
        height=350,
        margin={"r": 20, "t": 30, "l": 20, "b": 20},
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            traceorder="normal"
        ),
        xaxis=dict(
            title="Makine Sayısı",
            showgrid=True,
            gridcolor="#f1f5f9"
        ),
        yaxis=dict(
            title="",
            showgrid=False
        ),
        plot_bgcolor="white",
        # Premium Tooltip Style
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Inter, system-ui, sans-serif",
            bordercolor="#e2e8f0",
            align="left"
        )
    )
    
    st.plotly_chart(fig, width='stretch')


def render_detail_table(df: pd.DataFrame):
    """Filtrelenebilir detay tablosu."""
    
    if df.empty:
        st.info("Tablo için veri bulunamadı.")
        return
    
    # Filtreler
    col1, col2, col3 = st.columns(3)
    
    with col1:
        servisci_options = ["Tümü"] + sorted(df["Servisci"].unique().tolist())
        selected_servisci = st.selectbox("Servisci", servisci_options, key="bellis_servisci")
    
    with col2:
        bolge_options = ["Tümü"] + sorted(df["Bolge_Ad"].unique().tolist())
        selected_bolge = st.selectbox("Bölge", bolge_options, key="bellis_bolge")
    
    with col3:
        search_term = st.text_input("Müşteri Ara", key="bellis_search")
    
    # Filtreleme
    df_filtered = df.copy()
    
    if selected_servisci != "Tümü":
        df_filtered = df_filtered[df_filtered["Servisci"] == selected_servisci]
    
    if selected_bolge != "Tümü":
        df_filtered = df_filtered[df_filtered["Bolge_Ad"] == selected_bolge]
    
    if search_term:
        df_filtered = df_filtered[
            df_filtered["Musteri"].str.contains(search_term, case=False, na=False)
        ]
    
    # Görüntülenecek kolonlar
    display_cols = ["Musteri", "Sehir", "Bolge_Ad", "Servisci", "Makine_Modeli", "Seri_No"]
    display_cols = [c for c in display_cols if c in df_filtered.columns]
    
    # Kolon isimleri
    column_config = {
        "Musteri": st.column_config.TextColumn("Müşteri", width="large"),
        "Sehir": st.column_config.TextColumn("Şehir", width="medium"),
        "Bolge_Ad": st.column_config.TextColumn("Bölge", width="medium"),
        "Servisci": st.column_config.TextColumn("Servisci", width="medium"),
        "Makine_Modeli": st.column_config.TextColumn("Model", width="medium"),
        "Seri_No": st.column_config.TextColumn("Seri No", width="medium"),
    }
    
    st.dataframe(
        df_filtered[display_cols],
        width='stretch',
        height=400,
        column_config=column_config,
        hide_index=True
    )
    
    # Özet satırı
    st.caption(f"Toplam {len(df_filtered)} kayıt gösteriliyor (filtrelenmiş)")
