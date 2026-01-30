
import streamlit as st
import pandas as pd
from core.utils import tr_upper
from components import styles
from components.layout import section_title
from components.charts import render_chartjs
from config.constants import AY_KISA, ISLEM_OZETI_PERSONEL

def clean_action_type(action):
    """İşlem tipini normalize eder ve kategorize eder."""
    if pd.isna(action):
        return "DİĞER"
    
    action = str(action).strip().upper()
    
    if "BAKIM" in action:
        return "BAKIM"
    elif "ARIZA" in action:
        return "ARIZA"
    elif "DEVREYE ALMA" in action or " DA " in f" {action} ": # DA kelime olarak geçiyorsa
        return "DEVREYE ALMA"
    elif "KONTROL" in action:
        return "KONTROL"
    else:
        return "DİĞER"


@st.cache_data(show_spinner="Veriler işleniyor...", ttl=3600)
def prepare_islem_ozeti_data(df_saha, personnel_name="YÜKSEL"):
    """
    Saha verilerini işleyip İşlem Özeti raporuna hazırlar.
    Bu işlem ağır olduğu için önbelleğe alınır.
    
    Args:
        df_saha: Ham saha verisi frame'i
        personnel_name: Filtrelenecek personel adı (örn: "YÜKSEL", "SAMET")
    """
    # 2. Global Filtreleme: Sadece Sorumlu = SEÇİLEN PERSONEL
    target_col = None
    possible_cols = ['Sorumlu', 'Sorumlu Personel', 'Personel']
    
    for col in df_saha.columns:
        if str(col).strip() in possible_cols:
            target_col = col
            break
            
    filtered_df = pd.DataFrame()
    if target_col:
        # tr_upper kullanarak Türkçe karakter uyumlu filtreleme
        search_term = tr_upper(personnel_name)
        
        # Lambda fonksiyonu ile her satırı kontrol et
        mask = df_saha[target_col].astype(str).apply(lambda x: search_term in tr_upper(x))
        filtered_df = df_saha[mask].copy()
    else:
        return pd.DataFrame() # Hata durumunda boş dön

    if filtered_df.empty:
        return pd.DataFrame()

    # 3. İşlem Tipi Temizliği
    process_col = None
    possible_process_cols = ['İşlem', 'Islem', 'Yapılan İşlem', 'Açıklama']
    for col in df_saha.columns:
        if str(col).strip() in possible_process_cols:
            process_col = col
            break
    
    if not process_col:
        return pd.DataFrame()

    filtered_df['Kategori'] = filtered_df[process_col].apply(clean_action_type)
    
    # Tarih formatlama
    if 'Tarih' in filtered_df.columns:
        filtered_df['Tarih'] = pd.to_datetime(filtered_df['Tarih'], dayfirst=True)
    
    # Yıl Kolonu (Yoksa oluştur)
    if 'Yil' not in filtered_df.columns:
        filtered_df['Yil'] = filtered_df['Tarih'].dt.year

    # 4. GRUPLAMA (TÜM VERİ İÇİN)
    grouped_rows = []
    
    # Sıralama: Müşteri, Kategori, Tarih
    filtered_df = filtered_df.sort_values(by=['Müşteri', 'Kategori', 'Tarih'])

    for (musteri, kategori), group in filtered_df.groupby(['Müşteri', 'Kategori']):
        group = group.sort_values('Tarih')
        
        group['prev_date'] = group['Tarih'].shift(1)
        group['date_diff'] = (group['Tarih'] - group['prev_date']).dt.days
        
        group['group_id'] = (group['date_diff'] > 1).cumsum()
        
        for _, sub_group in group.groupby('group_id'):
            first_row = sub_group.iloc[0].copy()
            start_date = sub_group['Tarih'].min()
            end_date = sub_group['Tarih'].max()
            
            # Süre (Gün)
            duration = (end_date - start_date).days + 1
            
            if start_date == end_date:
                date_str = start_date.strftime('%d.%m.%Y')
            else:
                date_str = f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"
            
            first_row['Tarih_Gosterim'] = date_str
            first_row['Tarih'] = start_date
            first_row['Bitis_Tarihi'] = end_date
            first_row['Sure'] = duration
            
            # Yıl: Başlangıç tarihinin yılı
            first_row['Yil'] = start_date.year
            
            grouped_rows.append(first_row)
            
    if grouped_rows:
        grouped_df = pd.DataFrame(grouped_rows)
    else:
        grouped_df = pd.DataFrame(columns=filtered_df.columns)
        
    return grouped_df

def render_islem_ozeti_page(data_packet=None):
    # === STYLE INJECTION REMOVED (Handled Globally) ===
    


    # 1. Veri Alma (data_packet'tan)
    if data_packet is None:
        data_packet = {}
    
    df_saha = data_packet.get("saha", pd.DataFrame())

    if df_saha.empty:
        st.warning("Görüntülenecek veri bulunamadı.")
        return

    # Personel Listesi
    PERSONEL_LISTESI = ISLEM_OZETI_PERSONEL
    
    col_filter, _ = st.columns([1, 3])
    with col_filter:
        selected_personnel = st.selectbox("Personel Seçimi:", PERSONEL_LISTESI, index=0)

    # Veriyi cache'li fonksiyon ile hazırla
    grouped_df = prepare_islem_ozeti_data(df_saha, selected_personnel)

    if grouped_df.empty:
        st.info(f"{selected_personnel} için kayıt bulunamadı veya işlenemedi.")
        return


    # ==========================
    # BÖLÜM 1: YILLIK ÖZET TABLO
    # ==========================
    
    years = [2024, 2025, 2026]
    categories = ["BAKIM", "ARIZA", "DEVREYE ALMA", "KONTROL", "DİĞER"]
    summary_data = []

    for y in years:
        year_data = grouped_df[grouped_df['Yil'] == y]
        
        total_ops = len(year_data)
        total_days = year_data['Sure'].sum() if not year_data.empty else 0
        
        row = {
            "YIL": str(y),
            "TOPLAM": f"{total_ops} İşlem / {int(total_days)} Gün"
        }
        
        # Kategori sayıları
        for cat in categories:
            cat_data = year_data[year_data['Kategori'] == cat]
            c_count = len(cat_data)
            c_days = cat_data['Sure'].sum() if not cat_data.empty else 0
            row[cat] = f"{c_count} İşlem / {int(c_days)} Gün"
            
        summary_data.append(row)
    
    section_title("YILLIK ÖZET TABLO (İşlem Adeti / Adam Gün)", margin_top="1rem", show_border=False)
    df_summary = pd.DataFrame(summary_data)
    
    # Sütun sırasını belirle
    cols_order = ["YIL", "TOPLAM"] + categories
    
    # Stil vererek göster
    st.dataframe(
        df_summary[cols_order],
        hide_index=True,
        width="stretch",
        column_config={
            "YIL": st.column_config.TextColumn("YIL"),
            "TOPLAM": st.column_config.TextColumn("TOPLAM"),
            "BAKIM": st.column_config.TextColumn("BAKIM"),
            "ARIZA": st.column_config.TextColumn("ARIZA"),
            "DEVREYE ALMA": st.column_config.TextColumn("DEVREYE ALMA"),
            "KONTROL": st.column_config.TextColumn("KONTROL"),
            "DİĞER": st.column_config.TextColumn("DİĞER"),
        }
    )
    

    
    # ==========================
    # BÖLÜM 2: AYLIK GRAFİKLER
    # ==========================
    

    
    # Veriyi hazırla: grouped_df -> Yıl, Ay, İşlem Sayısı (Adet)
    if not grouped_df.empty:
        grouped_df['Ay'] = grouped_df['Tarih'].dt.month
        
        # Grafik Ayarları
        theme = st.session_state.get("theme", "light")
        tick_color = "#9CA3AF" if theme == "dark" else "#4B5563"
        grid_color = "rgba(255, 255, 255, 0.05)" if theme == "dark" else "rgba(0, 0, 0, 0.05)"

        year_colors = [
            {"border": "#3B82F6", "bg": "rgba(59, 130, 246, 0.15)"},   # Blue
            {"border": "#10B981", "bg": "rgba(16, 185, 129, 0.15)"},   # Green
            {"border": "#F59E0B", "bg": "rgba(245, 158, 11, 0.15)"},   # Amber
        ]
        
        all_months = list(range(1, 13))
        chart_labels = [AY_KISA.get(m, str(m)) for m in all_months]
        target_years = [2024, 2025, 2026]
        


        # 2.B - AYLIK İŞ GÜNÜ SAYISI
        section_title("AYLIK İŞ GÜNÜ SAYISI", margin_top="1rem", show_border=False)
        st.markdown("<div style='font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 12px;'>Yıllara göre toplam adam gün</div>", unsafe_allow_html=True)

        datasets_days = []
        for idx, year in enumerate(sorted(target_years)):
            color_set = year_colors[idx % len(year_colors)]
            df_year = grouped_df[grouped_df["Yil"] == year].copy()
            
            if df_year.empty:
                year_values = [0] * 12
            else:
                # BU SEFER 'Sure' SÜTUNUNU TOPLUYORUZ
                year_monthly = df_year.groupby("Ay")["Sure"].sum()
                year_values = [int(year_monthly.get(m, 0)) for m in all_months]
            
            datasets_days.append({
                "label": f"{year}",
                "data": year_values,
                "borderColor": color_set["border"],
                "backgroundColor": color_set["bg"],
                "fill": False,
                "tension": 0.4,
                "pointRadius": 4,
                "pointHoverRadius": 6,
                "borderWidth": 2,
            })

        line_data_days = {"labels": chart_labels, "datasets": datasets_days}
        line_options_days = {
            "maintainAspectRatio": False,
            "plugins": {
                "legend": { "display": True, "position": "top", "labels": { "color": tick_color, "usePointStyle": True, "padding": 20, "font": {"family": "'Inter', 'Roboto', sans-serif", "size": 12} } },
                "tooltip": { "backgroundColor": "#1F2937" if theme == "dark" else "#FFFFFF", "titleColor": "#F9FAFB" if theme == "dark" else "#111827", "bodyColor": "#F9FAFB" if theme == "dark" else "#6B7280", "borderColor": "rgba(255,255,255,0.1)" if theme == "dark" else "#E5E7EB", "borderWidth": 1, "padding": 10 }
            },
            "scales": {
                "x": { "ticks": {"color": tick_color, "font": {"family": "'Inter', 'Roboto', sans-serif"}}, "grid": {"color": grid_color} },
                "y": { "ticks": {"color": tick_color, "font": {"family": "'Inter', 'Roboto', sans-serif"}}, "grid": {"color": grid_color}, "beginAtZero": True, "title": {"display": True, "text": "Gün Sayısı", "color": tick_color} }
            }
        }
        render_chartjs("line", line_data_days, line_options_days, key="chart_days", height=350)

    st.markdown("---")

    # ==========================
    # BÖLÜM 3: DETAYLI TABLO
    # ==========================
    
    # Başlık ve Filtre Yan Yana
    # Sol tarafa yaslamak için: Header (2), Select (3), Spacer (6)
    col_header, col_select, _ = st.columns([2, 3, 6])
    
    with col_header:
        section_title("DETAYLI KAYITLAR", margin_top="0rem", show_border=False)
    
    with col_select:
        # Seçim Kutusu (Pill Style Radio)
        selected_year = st.radio("Yıl", [2026, 2025, 2024], horizontal=True, label_visibility="collapsed")
    
    # Filtrele
    df_detail = grouped_df[grouped_df['Yil'] == selected_year]
    
    if df_detail.empty:
        st.info(f"{selected_year} yılı için kayıt bulunamadı.")
    else:
        display_cols = ['Tarih_Gosterim', 'Teknisyen 1', 'Teknisyen 2', 'Müşteri', 'Servis Ürünü', 'Kategori', 'Sure']
        final_cols = [c for c in display_cols if c in df_detail.columns]
        
        st.dataframe(
            df_detail.sort_values(by="Tarih", ascending=False)[final_cols],
            width="stretch",
            hide_index=True,
            column_config={
                "Tarih_Gosterim": st.column_config.TextColumn("Tarih"),
                "Sure": st.column_config.NumberColumn("Gün", help="İşlem süresi (gün)")
            },
            height=400
        )

