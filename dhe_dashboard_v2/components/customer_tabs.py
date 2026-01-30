
import streamlit as st
import pandas as pd
from components.cards import premium_card, render_kpi_card
from components.charts import render_chartjs
from components.layout import spacer, section_title

def render_summary_tab(df_musteri, theme="light"):
    """Müşteri Portföy Özeti Tab'ı"""
    spacer(16)
    
    # Ortak hesaplamalar
    toplam_musteri = len(df_musteri)
    bos_musteriler = df_musteri[df_musteri["Sorumlu_Clean"] == "BOŞ / SAHİPSİZ"]
    bos_sayisi = len(bos_musteriler)
    sahipli_sayisi = toplam_musteri - bos_sayisi
    
    # Tema renkleri
    if theme == "dark":
        text_color = "#9CA3AF"
        grid_color = "rgba(255, 255, 255, 0.05)"
        bar_bg = "rgba(59, 130, 246, 0.2)"
        bar_border = "#60A5FA"
    else:
        text_color = "#6B7280"
        grid_color = "#E5E7EB"
        bar_bg = "rgba(59, 130, 246, 0.7)"
        bar_border = "#3B82F6"

    # KPI Kartları
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(render_kpi_card("TOPLAM MÜŞTERİ", f"{toplam_musteri:,}".replace(",", "."), "Kayıtlı Firma Sayısı", "users", "#3B82F6"), unsafe_allow_html=True)
    with k2:
        st.markdown(render_kpi_card("SAHİPLİ MÜŞTERİ", f"{sahipli_sayisi:,}".replace(",", "."), "Aktif Temsilcisi Olan", "user-check", "#10B981"), unsafe_allow_html=True)
    with k3:
        st.markdown(render_kpi_card("SAHİPSİZ MÜŞTERİ", f"{bos_sayisi}", "Atama Bekleyen", "user-x", "#EF4444"), unsafe_allow_html=True)
    
    # Personel Müşteri Dağılımı Grafiği
    section_title("PERSONEL MÜŞTERİ DAĞILIMI", margin_top="2rem")
    
    df_chart = df_musteri[df_musteri["Sorumlu_Clean"] != "BOŞ / SAHİPSİZ"].copy()
    
    pers_dist = df_chart.groupby("Sorumlu_Clean")["Kisa_Ad"].count().reset_index()
    pers_dist.columns = ["Sorumlu", "Musteri_Sayisi"]
    pers_dist = pers_dist.sort_values("Musteri_Sayisi", ascending=True)
    
    labels = pers_dist["Sorumlu"].tolist()
    data_values = pers_dist["Musteri_Sayisi"].tolist()
    
    bar_data = {
        "labels": labels,
        "datasets": [{
            "label": "Müşteri Sayısı",
            "data": data_values,
            "backgroundColor": bar_bg, 
            "borderColor": bar_border,
            "borderWidth": 1,
            "borderRadius": 4,
            "barPercentage": 0.6
        }]
    }
    
    bar_options = {
        "indexAxis": 'y',
        "maintainAspectRatio": False,
        "plugins": {
            "legend": {"display": False},
            "datalabels": {
                "display": True,
                "anchor": "end",
                "align": "end",
                "color": text_color,
                "font": {"weight": "bold", "family": "Inter"},
                "formatter": "__value_only__" # Special handler not needed, default is ok but alignment is key
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
                "beginAtZero": True, 
                "grid": {"color": grid_color},
                "ticks": {"color": text_color, "font": {"family": "'Inter', 'Roboto', sans-serif"}}
            },
            "y": {
                "grid": {"display": False},
                "ticks": {"color": text_color, "font": {"family": "'Inter', 'Roboto', sans-serif"}}
            }
        }
    }
    render_chartjs("bar", bar_data, bar_options, height=400)


def render_details_tab(df_musteri, theme="light"):
    """Detay Görüntüleme Tab'ı"""
    spacer(16)
    
    if theme == "dark":
        badge_bg = "rgba(255, 255, 255, 0.05)"
        badge_border = "rgba(255, 255, 255, 0.1)"
        badge_text = "#F3F4F6"
    else:
        badge_bg = "white"
        badge_border = "#E5E7EB"
        badge_text = "#374151"

    personel_listesi = df_musteri["Sorumlu_Clean"].unique().tolist()
    personel_listesi = sorted([p for p in personel_listesi if p != "BOŞ / SAHİPSİZ"])
    secenekler = ["TÜMÜ", "BOŞ / SAHİPSİZ"] + personel_listesi
    
    # Kompakt düzen - Personel Seçimi
    c_label, c_select, c_badge, c_space = st.columns([1.2, 3, 2, 4], gap="small")

    with c_label:
        st.markdown("""
        <div style='padding-top: 8px; font-size:0.9rem; color:var(--text-secondary); font-weight:700; text-align: right; white-space: nowrap;'>
            PERSONEL SEÇİMİ:
        </div>
        """, unsafe_allow_html=True)
    
    with c_select:
        secilen_personel = st.selectbox(
            "Personel",
            options=secenekler,
            index=0,
            label_visibility="collapsed",
            key="portfoy_personel_sec"
        )
    
    # Seçime göre filtreleme
    if secilen_personel == "TÜMÜ":
        df_filtered = df_musteri.copy()
    elif secilen_personel == "BOŞ / SAHİPSİZ":
        df_filtered = df_musteri[df_musteri["Sorumlu_Clean"] == "BOŞ / SAHİPSİZ"].copy()
    else:
        df_filtered = df_musteri[df_musteri["Sorumlu_Clean"] == secilen_personel].copy()
    
    # Arama kutuları
    spacer(16)
    c_kisa_label, c_kisa_input, c_uzun_label, c_uzun_input = st.columns([1.2, 3, 1.2, 4.8], gap="small")
    
    with c_kisa_label:
        st.markdown("""
        <div style='padding-top: 8px; font-size:0.85rem; color:var(--text-secondary); font-weight:600; text-align: right; white-space: nowrap;'>
            KISA AD:
        </div>
        """, unsafe_allow_html=True)
    
    with c_kisa_input:
        kisa_ad_arama = st.text_input("Kısa Ad Ara", placeholder="Ara...", label_visibility="collapsed", key="kisa_ad_arama")
    
    with c_uzun_label:
        st.markdown("""
        <div style='padding-top: 8px; font-size:0.85rem; color:var(--text-secondary); font-weight:600; text-align: right; white-space: nowrap;'>
            FİRMA ÜNVANI:
        </div>
        """, unsafe_allow_html=True)
    
    with c_uzun_input:
        uzun_ad_arama = st.text_input("Firma Ünvanı Ara", placeholder="Ara...", label_visibility="collapsed", key="uzun_ad_arama")
    
    # Arama filtreleri
    from core.utils import tr_upper
    
    if kisa_ad_arama:
        # Vektörize değil apply kullanıyoruz çünkü tr_upper özel map gerektirir
        # Ancak performans için str.upper() çok daha hızlıdır.
        # Yine de doğruluk için apply(tr_upper) şart.
        # Büyük veri setlerinde performans düşebilir ama müşteri sayısı sınırlı.
        
        # Arama terimini çevir
        term = tr_upper(kisa_ad_arama)
        
        # Kolon üzerinde arama
        # Not: Kaynak veri mixed case ise önce çevirmeliyiz
        mask = df_filtered["Kisa_Ad"].astype(str).apply(tr_upper).str.contains(term, na=False)
        df_filtered = df_filtered[mask]
    
    if uzun_ad_arama:
        term_uzun = tr_upper(uzun_ad_arama)
        mask_uzun = df_filtered["Uzun_Ad"].astype(str).apply(tr_upper).str.contains(term_uzun, na=False)
        df_filtered = df_filtered[mask_uzun]
    
    kayit_sayisi = len(df_filtered)
    
    with c_badge:
        st.markdown(f"""
        <div style="margin-top: 2px; margin-left:10px; background: {badge_bg}; padding: 0.4rem 1rem; border-radius: 6px; display: inline-flex; align-items: center; gap: 8px; border: 1px solid {badge_border}; white-space: nowrap; height: 38px;">
            <span style="font-size: 1rem; font-weight: 700; color: {badge_text}; line-height: 1;">{kayit_sayisi:,}</span>
            <span style="font-size: 0.7rem; color: {badge_text}; opacity: 0.8; text-transform: uppercase; font-weight: 600;">KAYIT</span>
        </div>
        """.replace(",", "."), unsafe_allow_html=True)
    
    spacer(24)
    
    if kayit_sayisi > 0:
        if secilen_personel == "TÜMÜ":
            df_display = df_filtered[["Kisa_Ad", "Uzun_Ad", "Sorumlu_Clean"]].copy()
            st.dataframe(
                df_display,
                column_config={
                    "Kisa_Ad": st.column_config.TextColumn("KISA AD", width="medium"), 
                    "Uzun_Ad": st.column_config.TextColumn("FİRMA ÜNVANI", width="large"),
                    "Sorumlu_Clean": st.column_config.TextColumn("SORUMLU", width="medium")
                },
                height=500, width="stretch", hide_index=True
            )
        else:
            df_display = df_filtered[["Kisa_Ad", "Uzun_Ad"]].copy()
            st.dataframe(
                df_display,
                column_config={
                    "Kisa_Ad": st.column_config.TextColumn("KISA AD", width="medium"),
                    "Uzun_Ad": st.column_config.TextColumn("FİRMA ÜNVANI", width="large")
                },
                height=500, width="stretch", hide_index=True
            )
    else:
        st.info("Bu kriterlere uygun müşteri bulunamadı.")


def render_orphaned_analysis_tab(df_musteri, df_all_quotes, bos_musteriler):
    """Sahipsiz Müşteri Analiz Tab'ı"""
    spacer(16)
    
    if df_all_quotes is not None and not df_all_quotes.empty:

        spacer(16)
        
        available_years = sorted(df_all_quotes["Yil"].dropna().unique().astype(int).tolist(), reverse=True)
        
        if not available_years:
            st.warning("Teklif verilerinde yıl bilgisi bulunamadı.")
        else:
            sahipsiz_musteriler = bos_musteriler["Kisa_Ad"].tolist()
            cards_container = st.container()
            
            spacer(16)
            spacer(16)
            # st.markdown("---") # Removed
            
            
            col_filter, col_table = st.columns([1, 3], gap="large")
            
            with col_filter:
                st.markdown('<div style="font-weight:700; font-size:1.1rem; margin-top:1.5rem; margin-bottom:10px;">Filtreler</div>', unsafe_allow_html=True)
                spacer(8)
                
                selected_years = st.multiselect(
                    "Yıl Seçimi",
                    options=available_years,
                    default=[available_years[0]] if available_years else [],
                    key="orphan_year_filter_v2"
                )
                
                spacer(12)
                
                if selected_years:
                    df_base = df_all_quotes[
                        (df_all_quotes["Yil"].isin(selected_years)) & 
                        (df_all_quotes["Musteri"].isin(sahipsiz_musteriler))
                    ].copy()
                    
                    if not df_base.empty:
                        mevcut_personeller = sorted(df_base["Personel_Adi"].dropna().unique().tolist())
                        options_pers = ["TÜMÜ"] + mevcut_personeller
                        
                        selected_personnel_val = st.selectbox(
                            "Personel Filtresi",
                            options=options_pers,
                            index=0,
                            key="orphan_pers_filter_v2"
                        )
                    else:
                        selected_personnel_val = "TÜMÜ"
                        st.info("Bu yıllarda kayıt yok.")
                else:
                    selected_personnel_val = "TÜMÜ"
                    st.info("Yıl seçiniz.")
            
            with col_table:
                if selected_years:
                    df_base = df_all_quotes[
                        (df_all_quotes["Yil"].isin(selected_years)) & 
                        (df_all_quotes["Musteri"].isin(sahipsiz_musteriler))
                    ].copy()
                    
                    if selected_personnel_val != "TÜMÜ":
                        df_orphan_quotes = df_base[df_base["Personel_Adi"] == selected_personnel_val].copy()
                    else:
                        df_orphan_quotes = df_base.copy()
                    
                    if not df_orphan_quotes.empty:
                        df_grouped = df_orphan_quotes.groupby("Musteri").agg(
                            Teklif_Adedi=("Teklif_No", "nunique"),
                            Son_Tarih=("Tarih", "max"),
                            Personeller=("Personel_Adi", lambda x: ", ".join(sorted(list(set(x.dropna())))))
                        ).reset_index().sort_values("Teklif_Adedi", ascending=False)
                        
                        musteri_names = df_musteri[["Kisa_Ad", "Uzun_Ad"]].drop_duplicates(subset=["Kisa_Ad"])
                        df_grouped = pd.merge(df_grouped, musteri_names, left_on="Musteri", right_on="Kisa_Ad", how="left")
                        df_grouped["Son_Tarih_Str"] = df_grouped["Son_Tarih"].dt.strftime("%d.%m.%Y")
                        
                        yil_str = ", ".join(map(str, sorted(selected_years)))
                        yil_str = ", ".join(map(str, sorted(selected_years)))
                        section_title(f"SAHİPSİZ MÜŞTERİ TEKLİFLERİ ({yil_str})", margin_top="1rem", show_border=False)
                        spacer(8)
                        
                        st.dataframe(
                            df_grouped[["Musteri", "Uzun_Ad", "Teklif_Adedi", "Son_Tarih_Str", "Personeller"]],
                            column_config={
                                "Musteri": st.column_config.TextColumn("KISA KOD", width="small"),
                                "Uzun_Ad": st.column_config.TextColumn("FİRMA ADI", width="medium"),
                                "Teklif_Adedi": st.column_config.NumberColumn("TEKLİF SAYISI", format="%d"),
                                "Son_Tarih_Str": st.column_config.TextColumn("SON TEKLİF", width="small"),
                                "Personeller": st.column_config.TextColumn("TEKLİF VEREN(LER)", width="large")
                            },
                            hide_index=True, height=300, width="stretch"
                        )
                        
                        with cards_container:
                            unique_orphan_count = df_orphan_quotes["Musteri"].nunique()
                            total_quote_count = len(df_orphan_quotes)
                            oc1, oc2 = st.columns(2)
                            with oc1: st.markdown(render_kpi_card("TEKLİF ALAN SAHİPSİZ MÜŞTERİ", f"{unique_orphan_count}", f"Seçilen kriterlerde ({yil_str})", "user-x", "#6366F1"), unsafe_allow_html=True)
                            with oc2: st.markdown(render_kpi_card("TOPLAM TEKLİF", f"{total_quote_count}", "Sorumlusu atanmamış müşterilere verilen teklifler", "clipboard", "#10B981"), unsafe_allow_html=True)

                    else:
                        st.success("✅ Seçilen kriterlerde sahipsiz müşterilere teklif kaydı bulunamadı!")
                        with cards_container:
                            oc1, oc2 = st.columns(2)
                            with oc1: st.markdown(render_kpi_card("TEKLİF ALAN SAHİPSİZ MÜŞTERİ", "0", "Kayıt bulunamadı", "user-x", "#6366F1"), unsafe_allow_html=True)
                            with oc2: st.markdown(render_kpi_card("TOPLAM TEKLİF", "0", "Kayıt bulunamadı", "clipboard", "#10B981"), unsafe_allow_html=True)

                else:
                    st.info("Lütfen soldan en az bir yıl seçiniz.")
                    with cards_container:
                         oc1, oc2 = st.columns(2)
                         with oc1: st.markdown(render_kpi_card("TEKLİF ALAN SAHİPSİZ MÜŞTERİ", "-", "Yıl seçimi bekleniyor", "user-x", "#6366F1"), unsafe_allow_html=True)
                         with oc2: st.markdown(render_kpi_card("TOPLAM TEKLİF", "-", "Yıl seçimi bekleniyor", "clipboard", "#10B981"), unsafe_allow_html=True)
    else:
        st.info("Teklif verileri yüklenmedi veya boş.")


def render_products_tab(df_urun):
    """Servis Ürünleri Tab'ı"""
    spacer(16)
    
    if df_urun is not None and not df_urun.empty:
        toplam_cihaz = len(df_urun)
        benzersiz_musteri = df_urun["Musteri"].nunique()
        
        kp1, kp2 = st.columns(2)
        with kp1: st.markdown(render_kpi_card("TOPLAM ÜRÜN", f"{toplam_cihaz}", "Kayıtlı servis ürünü", "settings", "#6366F1"), unsafe_allow_html=True)
        with kp2: st.markdown(render_kpi_card("ÜRÜN SAHİBİ MÜŞTERİ", f"{benzersiz_musteri}", "Müşteri Sayısı", "users", "#10B981"), unsafe_allow_html=True)
        
        spacer(24)
        spacer(24)
        # st.markdown("---") # Removed
        
        df_musteri_cihaz = df_urun.groupby("Musteri").agg(
            Cihaz_Sayisi=("Seri_No", "count"),
            Ilk_Tarih=("Tarih", "min"),
            Son_Tarih=("Tarih", "max")
        ).reset_index().sort_values("Cihaz_Sayisi", ascending=False)
        
        col_sel, col_detay = st.columns([1, 2], gap="large")
        
        with col_sel:
            st.markdown('<div style="font-weight:700; font-size:1.2rem; margin-bottom:12px;">Firma Seçimi</div>', unsafe_allow_html=True)
            options = df_musteri_cihaz["Musteri"].tolist()
            counts = dict(zip(df_musteri_cihaz["Musteri"], df_musteri_cihaz["Cihaz_Sayisi"]))
            
            # Default "ACIBADEN" veya "ACIBADEM" bul
            default_idx = 0
            for i, opt in enumerate(options):
                opt_u = opt.upper()
                if "ACIBADEN" in opt_u or "ACIBADEM" in opt_u:
                    default_idx = i
                    break
            
            selected_firm = st.selectbox("Listeden firma seçin veya yazın:", options=options, index=default_idx, format_func=lambda x: f"{x} ({counts.get(x, 0)} cihaz)", key="srv_analysis_select")
            if selected_firm:
                firm_count = counts.get(selected_firm, 0)
                st.info(f"Seçili firma için **{firm_count}** adet cihaz kaydı bulundu.")
        
        with col_detay:
            if selected_firm:
                section_title(f"{selected_firm} — CİHAZ LİSTESİ", margin_top="0", show_border=False)
                df_cihazlar = df_urun[df_urun["Musteri"] == selected_firm].copy()
                if not df_cihazlar.empty:
                    # Tarih sütunu string gelebilir, datetime'a çevir
                    df_cihazlar["Tarih"] = pd.to_datetime(df_cihazlar["Tarih"], dayfirst=True, errors='coerce')
                    df_cihazlar["Tarih_Str"] = df_cihazlar["Tarih"].dt.strftime("%d.%m.%Y").fillna("-")
                    st.dataframe(
                        df_cihazlar[["Seri_No", "Cihaz_No", "Tarih_Str"]],
                        column_config={
                            "Seri_No": st.column_config.TextColumn("Seri No", width="medium"),
                            "Cihaz_No": st.column_config.TextColumn("Cihaz No", width="medium"),
                            "Tarih_Str": st.column_config.TextColumn("Devreye Alma", width="small"),
                        },
                        hide_index=True, width="stretch", height=300 
                    )
                else:
                    st.warning("Veri hatası: Cihaz listesi boş.")
            else:
                st.info("Lütfen soldan bir firma seçin.")
    else:
        st.info("Servis ürünleri verisi yüklenmedi veya boş.")
