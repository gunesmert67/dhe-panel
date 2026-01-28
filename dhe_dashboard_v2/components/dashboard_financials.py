
import streamlit as st
import pandas as pd
from components.layout import spacer, section_title
from components.cards import render_kpi_card, render_perf_card, render_conversion_card
from config.constants import PERSONEL_MAP
from core.utils import calculate_delta

def render_financial_summary_tab(df_sip_filtered, df_tek_filtered, selected_years, selected_period, sym, conversion_factor, previous_values=None, df_all_filtered=None):
    """Finansal Özet Tab'ını render eder."""
    
    spacer(10)
    
    # 1. KPI KARTLARI
    total_ciro = df_sip_filtered["Tutar_EUR"].sum()
    total_kar = df_sip_filtered["Kar_EUR"].sum()
    total_siparis = len(df_sip_filtered)
    
    # Use all quotes (open + ordered) if available, otherwise fallback to open quotes
    if df_all_filtered is not None:
        total_teklif = len(df_all_filtered)
    else:
        total_teklif = len(df_tek_filtered)
    
    def format_curr(val):
        converted = val * conversion_factor
        return f"{sym}{converted:,.0f}".replace(",", ".")

    # Delta Hesapla
    delta_ciro = None; delta_kar = None; delta_margin = None; delta_conv = None
    sub_text = "Seçili Dönem Toplamı"
    
    # Mevcut Dönem Metrikleri
    margin_pct = (total_kar / total_ciro * 100) if total_ciro > 0 else 0
    conversion_rate = (total_siparis / total_teklif * 100) if total_teklif > 0 else 0
    
    if previous_values:
        sub_text = "Önceki Döneme Göre"
        
        # Ciro Delta
        prev_ciro = previous_values.get("total_ciro", 0)
        delta_ciro = calculate_delta(total_ciro, prev_ciro)
        
        # Kar Delta
        prev_kar = previous_values.get("total_kar", 0)
        delta_kar = calculate_delta(total_kar, prev_kar)
        
        # Kar Marjı Delta (Puan farkı olarak değil, değişim yüzdesi olarak)
        # Veya puan farkı daha anlamlı olabilir: %10 -> %12 (+2 puan)
        # Ancak calculate_delta fonksiyonumuz % değişim hesaplıyor. Tutarlılık için onu kullanalım.
        prev_margin = (prev_kar / prev_ciro * 100) if prev_ciro > 0 else 0
        delta_margin = calculate_delta(margin_pct, prev_margin)
        
        # Dönüşüm Oranı Delta (Sipariş/Teklif değişimi)
        prev_siparis = previous_values.get("total_siparis", 0)
        prev_teklif = previous_values.get("total_teklif", 0)
        prev_conv = (prev_siparis / prev_teklif * 100) if prev_teklif > 0 else 0
        delta_conv = calculate_delta(conversion_rate, prev_conv)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1: 
        st.markdown(render_kpi_card(f"TOPLAM CİRO ({sym})", format_curr(total_ciro), sub_text, "chart", "#3B82F6", delta=delta_ciro), unsafe_allow_html=True)
    with k2: 
        st.markdown(render_kpi_card(f"TOPLAM KAR ({sym})", format_curr(total_kar), sub_text, "trending-up", "#10B981", delta=delta_kar), unsafe_allow_html=True)
    with k3: 
        # Kar Marjı Kartı
        st.markdown(render_kpi_card("KAR MARJI %", f"%{margin_pct:.1f}", sub_text, "pie-chart", "#8B5CF6", delta=delta_margin), unsafe_allow_html=True)
    with k4: 
        # Sipariş / Teklif Kartı
        val_str = f"{total_siparis} / {total_teklif}"
        st.markdown(render_kpi_card("SİPARİŞ / TEKLİF", val_str, sub_text, "layers", "#F59E0B", delta=delta_conv), unsafe_allow_html=True)

    # 2. PERSONEL PERFORMANSI (AVATAR & PROGRESS)
    section_title("PERSONEL PERFORMANSI", margin_top="2.5rem", show_border=False)
    
    perf = df_sip_filtered.groupby("Personel_Adi")[["Tutar_EUR", "Kar_EUR"]].sum()
    perf = perf.sort_values("Tutar_EUR", ascending=False).reset_index()
    aktif_personel_isimleri = list(set(PERSONEL_MAP.values()))
    perf = perf[perf["Personel_Adi"].isin(aktif_personel_isimleri)] 
    
    if not perf.empty:
        max_val = perf["Tutar_EUR"].max()
        if max_val == 0: max_val = 1
        
        cols = st.columns(4)
        for i in range(len(perf)):
            col_idx = i % 4
            if i > 0 and col_idx == 0:
                 spacer(16)
                 cols = st.columns(4)
            with cols[col_idx]:
                p = perf.iloc[i]
                progress_pct = (p['Tutar_EUR'] / max_val) * 100
                st.markdown(render_perf_card(
                    p['Personel_Adi'], 
                    format_curr(p['Tutar_EUR']), 
                    format_curr(p['Kar_EUR']),
                    progress_pct
                ), unsafe_allow_html=True)
    else:
        st.info("Bu kriterlere uygun personel performansı bulunamadı.")
 
    # --- ESKİ ÇALIŞANLAR BÖLÜMÜ ---
    # Not: Eski çalışanlar için tüm dataya ihtiyaç var mı? Hayır, filtrelenmiş data yeterli.
    # Ancak filtrelenmiş data içinde 'eski çalışan' varsa gösterir.
    
    all_personel_perf = df_sip_filtered.groupby("Personel_Adi")[["Tutar_EUR", "Kar_EUR"]].sum()
    all_personel_perf = all_personel_perf.sort_values("Tutar_EUR", ascending=False).reset_index()
    
    eski_calisanlar = all_personel_perf[~all_personel_perf["Personel_Adi"].isin(aktif_personel_isimleri)].copy()
    
    eski_calisanlar = eski_calisanlar[
        (eski_calisanlar["Tutar_EUR"] > 0) & 
        (eski_calisanlar["Personel_Adi"].notna()) & 
        (eski_calisanlar["Personel_Adi"] != "") &
        (eski_calisanlar["Personel_Adi"] != "nan")
    ]
    
    if not eski_calisanlar.empty:
        spacer(40)
        with st.expander("Eski Çalışanlar", expanded=False):
            st.caption("Veri görüntülenen dönemde satışı olan eski çalışanlar.")
            rows = len(eski_calisanlar)
            cols_per_row = 4
            max_val_eski = all_personel_perf["Tutar_EUR"].max() if not all_personel_perf.empty else 1
            
            for i in range(0, rows, cols_per_row):
                 if i > 0: spacer(16)
                 batch = eski_calisanlar.iloc[i:i+cols_per_row]
                 cols = st.columns(4)
                 for j, row in enumerate(batch.itertuples()):
                     with cols[j]:
                         progress_pct = (row.Tutar_EUR / max_val_eski) * 100
                         st.markdown(render_perf_card(
                             row.Personel_Adi, 
                             format_curr(row.Tutar_EUR), 
                             format_curr(row.Kar_EUR),
                             progress_pct
                         ), unsafe_allow_html=True)

def render_conversion_analysis_tab(df_sip_filtered, df_tek_filtered, filter_label, df_all_filtered=None):
    """Teklif/Sipariş Analizi Tab'ını render eder."""
    
    spacer(10)
    
    # Özet KPI Satırı
    # section_title("GENEL BAKIŞ", margin_top="0.5rem") - REMOVED per request
    
    teklif_donem = len(df_tek_filtered)
    siparis_donem = len(df_sip_filtered)
    
    if df_all_filtered is not None:
        toplam_teklif = len(df_all_filtered)
    else:
        toplam_teklif = teklif_donem + siparis_donem
    
    musteri_siparis = df_sip_filtered["Musteri"].nunique() if not df_sip_filtered.empty else 0
    overall_conversion = (siparis_donem / toplam_teklif * 100) if toplam_teklif > 0 else 0
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(render_kpi_card("SİPARİŞ SAYISI", f"{siparis_donem}", filter_label, "check-circle", "#10B981"), unsafe_allow_html=True)
    with k2:
        st.markdown(render_kpi_card("TEKLİF SAYISI", f"{toplam_teklif}", filter_label, "clipboard", "#F59E0B"), unsafe_allow_html=True)
    with k3:
        st.markdown(render_kpi_card("AKTİF MÜŞTERİ", f"{musteri_siparis}", "Sipariş veren firma", "users", "#6366F1"), unsafe_allow_html=True)
    with k4:
        st.markdown(render_kpi_card("DÖNÜŞÜM ORANI", f"%{overall_conversion:.1f}", "Sipariş / Teklif", "trending-up", "#8B5CF6"), unsafe_allow_html=True)
    
    # Personel Bazlı
    section_title("PERSONEL PERFORMANSI", margin_top="3rem", show_border=False)
    
    # 1. Toplam Teklif Sayısı (Tüm Teklifler üzerinden)
    if df_all_filtered is not None and not df_all_filtered.empty:
        teklif_per_personel = df_all_filtered.groupby("Personel_Adi").agg(
            Teklif_Sayisi=("Teklif_No", "count"), 
            Teklif_Musteri=("Musteri", "nunique")
        ).reset_index()

    else:
        # Fallback: df_all_filtered yoksa boş dön, RISKLI TOPLAMA MANTIGINI KALDIRIYORUZ
        teklif_per_personel = pd.DataFrame(columns=["Personel_Adi", "Teklif_Sayisi", "Teklif_Musteri"])
    
    # 2. Sipariş Sayısı
    if not df_sip_filtered.empty:
        siparis_per_personel = df_sip_filtered.groupby("Personel_Adi").agg(
            Siparis_Sayisi=("Siparis_No", "count"), 
            Siparis_Musteri=("Musteri", "nunique")
        ).reset_index()
    else:
        siparis_per_personel = pd.DataFrame(columns=["Personel_Adi", "Siparis_Sayisi", "Siparis_Musteri"])
    
    # 3. Birleştirme
    perf_df = pd.merge(teklif_per_personel, siparis_per_personel, on="Personel_Adi", how="outer").fillna(0)
    
    # Eski yöntemden gelen (Acik_Teklif_Sayisi) logic kaldırıldı.
    # if "Acik_Teklif_Sayisi" in perf_df.columns:
    #     perf_df["Teklif_Sayisi"] = perf_df["Acik_Teklif_Sayisi"] + perf_df["Siparis_Sayisi"]
    
    perf_df["Donusum_Orani"] = perf_df.apply(lambda r: (r["Siparis_Sayisi"] / r["Teklif_Sayisi"] * 100) if r["Teklif_Sayisi"] > 0 else 0, axis=1)
    perf_df["Musteri_Sayisi"] = perf_df[["Teklif_Musteri", "Siparis_Musteri"]].max(axis=1)
    
    # Aktif Personel Filtresi
    aktif_personel_isimleri = list(set(PERSONEL_MAP.values()))
    perf_df_aktif = perf_df[perf_df["Personel_Adi"].isin(aktif_personel_isimleri)].copy()
    perf_df_aktif = perf_df_aktif[perf_df_aktif["Teklif_Sayisi"] > 0].sort_values("Donusum_Orani", ascending=False).reset_index(drop=True)
    
    if not perf_df_aktif.empty:
        cols = st.columns(4)
        for i, row in perf_df_aktif.iterrows():
            col_idx = i % 4
            if i > 0 and col_idx == 0:
                spacer(8)
                cols = st.columns(4)
            with cols[col_idx]:
                st.markdown(render_conversion_card(
                    name=row["Personel_Adi"],
                    teklif_count=int(row["Teklif_Sayisi"]),
                    siparis_count=int(row["Siparis_Sayisi"]),
                    musteri_count=int(row["Musteri_Sayisi"]),
                    conversion_rate=row["Donusum_Orani"]
                ), unsafe_allow_html=True)
    else:
        st.info("Bu kriterlere uygun personel verisi bulunamadı.")

    # --- ESKİ ÇALIŞANLAR BÖLÜMÜ ---
    perf_df_eski = perf_df[~perf_df["Personel_Adi"].isin(aktif_personel_isimleri)].copy()
    
    # Filtreleme: Teklifi olan ve ismi geçerli olanlar
    perf_df_eski = perf_df_eski[
        (perf_df_eski["Teklif_Sayisi"] > 0) & 
        (perf_df_eski["Personel_Adi"].notna()) & 
        (perf_df_eski["Personel_Adi"] != "") &
        (perf_df_eski["Personel_Adi"] != "nan")
    ].sort_values("Donusum_Orani", ascending=False).reset_index(drop=True)

    if not perf_df_eski.empty:
        spacer(40)
        with st.expander("Eski Çalışanlar", expanded=False):
            st.caption("Veri görüntülenen dönemde işlem yapmış eski çalışanlar.")
            
            rows = len(perf_df_eski)
            cols_per_row = 4
            
            for i in range(0, rows, cols_per_row):
                 if i > 0: spacer(16)
                 batch = perf_df_eski.iloc[i:i+cols_per_row]
                 cols = st.columns(4)
                 for j, row in enumerate(batch.itertuples()):
                     with cols[j]:
                         st.markdown(render_conversion_card(
                             name=row.Personel_Adi,
                             teklif_count=int(row.Teklif_Sayisi),
                             siparis_count=int(row.Siparis_Sayisi),
                             musteri_count=int(row.Musteri_Sayisi),
                             conversion_rate=row.Donusum_Orani
                         ), unsafe_allow_html=True)

