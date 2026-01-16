# DHE Dashboard v2.2.0 - "Google Sheets Edition" 🚀

DHE Endüstriyel için geliştirilmiş, Google Sheets entegrasyonlu Python/Streamlit tabanlı **Gelişmiş Yönetim Portalı**.

## 🌟 Öne Çıkan Özellikler

- **Google Sheets Entegrasyonu**: Veriler gerçek zamanlı olarak Google Sheets'ten çekilir
- **Premium UI**: Minimalist Dark/Light tema desteği
- **Otomatik Kur Dönüşümü**: EUR, USD, GBP, TL/TRY → EUR (aylık bazda)
- **5 Dakika Cache**: Performans için otomatik önbellekleme
- **Responsive Tasarım**: Tüm ekran boyutlarına uyumlu
- **ChartJS Grafikleri**: Etkileşimli ve modern görselleştirmeler

## 📂 Proje Yapısı

```
dhe_dashboard_v2/
├── app.py                  # 🚀 Ana Uygulama
├── requirements.txt        # Bağımlılıklar
├── dhe_baslat.bat          # Windows başlatma scripti
├── loophole_baslat.bat     # Tünel/uzaktan erişim scripti
│
├── config/
│   ├── constants.py        # Kurlar, personel mapping, renk paletleri
│   └── city_coordinates.py # Şehir koordinatları ve bölge tanımları
│
├── core/
│   ├── data_loader.py      # Veri Yükleme Yöneticisi (Orchestrator)
│   ├── gsheets.py          # Google Sheets Bağlantı Modülü
│   ├── transforms.py       # Veri İşleme ve CRM Mantığı
│   ├── date_utils.py       # Tarih ve İş Günü Hesaplamaları
│   ├── utils.py            # Genel Yardımcı Fonksiyonlar
│   ├── validator.py        # Veri Doğrulama
│   └── bellis_loader.py    # Bellis Makine Verileri Yükleyici
│
├── components/
│   ├── cards.py            # KPI Kartları
│   ├── charts.py           # ChartJS Grafik Motoru
│   ├── layout.py           # Layout (Header/Sidebar)
│   ├── styles.py           # CSS ve Tema
│   ├── placeholders.py     # Boş Sayfa Şablonları
│   ├── customer_tabs.py    # Müşteri Sayfası Tab Bileşenleri
│   ├── dashboard_charts.py # Dashboard Grafik Bileşenleri
│   ├── dashboard_financials.py # Finansal Özet Bileşenleri
│   ├── field_charts.py     # Saha Operasyon Grafikleri
│   ├── field_stats.py      # Saha İstatistik Kartları
│   └── field_tables.py     # Saha Tablolar
│
├── views/
│   ├── landing_page.py     # Ana Sayfa
│   ├── integrated_dashboard.py # Servis Performansı View
│   ├── crm.py              # CRM Analizi View
│   ├── customers.py        # Müşteri Yönetimi View
│   ├── field_ops.py        # Saha Ekibi View (Teknisyen)
│   ├── yuksel_ops.py       # İşlem Özeti View
│   └── bellis.py           # Bellis Makine Takip View
│
├── data/
│   └── credentials.json    # Google Sheets API Kimlik Bilgileri
│
├── tests/                  # Unit Testler
└── logs/                   # Uygulama Günlükleri

```

## 📊 Veri Kaynakları (Google Sheets)

### DHE_Data Dosyası
| Sekme | Açıklama | Satır |
|-------|----------|-------|
| `teklif` | Tüm teklifler | ~23,600 |
| `siparis` | Siparişler | ~11,400 |
| `müsteri` | Müşteri listesi | ~5,800 |
| `ürün` | Ürün/Cihaz verileri | ~10,200 |
| `kurlar` | Aylık döviz kurları | ~109 |

### 2025 SERVİS PROGRAMI
| Sekme | Açıklama |
|-------|----------|
| `2025` | 2025 saha operasyonları |
| `2026` | 2026 saha operasyonları |

### Bellis Dosyası
| Sekme | Açıklama |
|-------|----------|
| `makine` | Bellis makine veritabanı |
| `sehirler` | Şehir/Bölge eşleştirmeleri |

## 🔧 Desteklenen Formatlar

| Alan | Format | Örnek |
|------|--------|-------|
| **Tarih** | DD.MM.YYYY | `02.01.2017` |
| **Tutar** | Türk formatı | `1.146,10` |
| **Kurlar** | Ondalık virgül | `0,025` |

## 🚀 Kurulum

### 1. Gereksinimler
```bash
pip install -r requirements.txt
```

**Bağımlılıklar:**
- `streamlit==1.52.2` - Web framework
- `pandas==2.3.3` - Veri işleme
- `plotly==6.5.0` - İnteraktif grafikler
- `openpyxl==3.1.5` - Excel desteği
- `gspread` - Google Sheets API
- `oauth2client` - Google OAuth

### 2. Google Sheets API Ayarları
1. Google Cloud Console'dan Service Account oluşturun
2. `credentials.json` dosyasını `data/` klasörüne koyun
3. Google Sheets dosyalarını service account e-postasıyla paylaşın

### 3. Başlatma
```bash
streamlit run app.py
```
*Veya: `dhe_baslat.bat` dosyasını çalıştırın*

## 📈 Modüller

### 🏠 Ana Sayfa
- Şirket özeti ve KPI'lar
- Aylık teklif/sipariş sayıları (YoY karşılaştırma)
- Sahada aktif teknisyen sayısı
- Hızlı erişim menüsü

### 📊 Servis Performansı
- Yıllık/Aylık ciro analizi (EUR)
- Personel performans kartları
- Trend grafikleri
- Detaylı kayıt tablosu (Sipariş/Teklif toggle)

### 🎯 CRM Analizi (Hunter Mode)
- Müşteri segmentasyonu (VIP, Gold, Standart)
- Müşteri yaşlandırma (0-12, 12-24, 24+ ay)
- Teklif odaklı analiz
- Risk takibi

### 👥 Müşteri Yönetimi
- Portföy görüntüleyici
- Servis ürünleri (cihaz listesi)
- Personel dağılımı
- Teklif geçmişi

### 🔧 Teknisyen (Saha Ekibi)
- Teknisyen performans takibi
- Adam-Gün hesaplamaları
- Arıza/Bakım/Devreye alma analizi
- En çok gidilen şehirler
- Günlük operasyon planı

### 📋 İşlem Özeti
- Atölye işlem özeti
- Aylık iş günü ve işlem sayısı grafikleri
- Yıl bazlı filtreleme
- Detaylı kayıt tablosu

### 🗺️ Bellis
- Türkiye haritası üzerinde makine dağılımı
- Servis sağlayıcı analizi
- Bölge bazlı özet
- Detaylı makine listesi

## 🛠️ Teknik Altyapı

- **Backend**: Python 3.11+ / Streamlit
- **Veri**: Google Sheets API (gspread) + Pandas
- **Cache**: `st.cache_data` (5 dakika TTL)
- **Grafik**: ChartJS v4.4.1 + Plotly
- **Harita**: Plotly Express (scatter_mapbox)
- **Tema**: CSS Variables ile dinamik Dark/Light

## 📝 Geliştirme Notları

- Sıfır değerli teklifler (Tutar_EUR=0 ve Maliyet_EUR=0) otomatik filtrelenir
- 2024 verileri artık yüklenmemektedir (sadece 2025-2026)
- Kur dönüşümleri aylık bazda `kurlar` sekmesinden yapılır
- "DHE ENDÜSTRİYEL" müşterisi "ATÖLYE" olarak sınıflandırılır

---
*Geliştirici: Mert Güneş & Antigravity Agent*  
*Sürüm: v2.4.0*  
*Son Güncelleme: Ocak 2026*
