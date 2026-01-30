
from datetime import date, timedelta, datetime
import pandas as pd
import numpy as np

def get_weekday_count(year: int, month: int = None, until_today: bool = True, holidays: set = None):
    """
    Belirtilen yıl ve ay için hafta içi gün sayısını hesaplar (Pazartesi-Cuma).
    Ay belirtilmezse tüm yıl için hesaplar.
    until_today=True ise sadece bugüne kadar olan günleri sayar.
    """
    try:
        today = date.today()
        
        # Başlangıç ve bitiş tarihlerini belirle
        if month:
            start_date = date(year, month, 1)
            # Ayın son gününü bul
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
        else:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            
        # Gelecek kontrolü (until_today=True ise)
        if until_today and end_date > today:
            end_date = today
            
        # Eğer başlangıç tarihi bitişten büyükse (örn: henüz gelmemiş bir ay)
        if start_date > end_date:
            return 0
            
        # İş günlerini oluştur (Pazartesi=0 ... Cuma=4)
        daterange = pd.date_range(start=start_date, end=end_date)
        workdays = daterange[daterange.weekday < 5] # Cumartesi(5) ve Pazar(6) hariç
        
        # Tatilleri düş
        if holidays:
            # Tatil setindeki tarihleri datetime.date objesine çevirelim (garanti olsun)
            holiday_dates = set()
            for h in holidays:
                if isinstance(h, (datetime, pd.Timestamp)):
                    holiday_dates.add(h.date())
                elif isinstance(h, str):
                    try:
                        holiday_dates.add(pd.to_datetime(h, dayfirst=True).date())
                    except:
                        pass
                else:
                    holiday_dates.add(h)
            
            # İş günlerinden tatil günlerini çıkar
            # workdays elemenları timestamp olduğu için .date() ile çevirmek gerekiyor
            workdays = [d for d in workdays if d.date() not in holiday_dates]
            
        return len(workdays)
        
    except Exception as e:
        # Hata durumunda güvenli bir değer döndür veya logla
        print(f"Hafta içi gün hesaplama hatası: {e}")
        return 22 if month else 260 # Yaklaşık değerler


def calculate_effective_workdays(year: int, month: int = None, start_date: date = None, end_date: date = None, holidays: set = None):
    """
    Personelin işe giriş ve çıkış tarihlerine göre efektif iş günü sayısını hesaplar.
    Tatil günlerini hesaptan düşer.
    """
    try:
        current_date = date.today()
        
        # Dönem sınırlarını belirle
        if month:
            period_start = date(year, month, 1)
            if month == 12:
                period_end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                period_end = date(year, month + 1, 1) - timedelta(days=1)
        else:
            period_start = date(year, 1, 1)
            period_end = date(year, 12, 31)
            
        # Dönemi bugünle sınırla
        if period_end > current_date:
            period_end = current_date
            
        # Dönem henüz başlamadıysa
        if period_start > period_end:
            return 0
            
        # Personel çalışma aralığını belirle
        effective_start = period_start
        effective_end = period_end
        
        # --- TARİH TİPİ DÖNÜŞÜMLERİ (Timestamp/String -> date) ---
        # start_date için tip kontrolü
        if pd.isna(start_date):
            start_date = None
        elif isinstance(start_date, str):
            try:
                start_date = pd.to_datetime(start_date, dayfirst=True, errors='coerce')
                start_date = start_date.date() if pd.notna(start_date) else None
            except:
                start_date = None
        elif isinstance(start_date, (pd.Timestamp, datetime)):
            start_date = start_date.date()
        elif not isinstance(start_date, date):
            start_date = None
            
        # end_date için tip kontrolü
        if pd.isna(end_date):
            end_date = None
        elif isinstance(end_date, str):
            try:
                end_date = pd.to_datetime(end_date, dayfirst=True, errors='coerce')
                end_date = end_date.date() if pd.notna(end_date) else None
            except:
                end_date = None
        elif isinstance(end_date, (pd.Timestamp, datetime)):
            end_date = end_date.date()
        elif not isinstance(end_date, date):
            end_date = None

        # İşe giriş tarihi dönemden sonraysa
        if start_date and start_date > period_start:
            effective_start = start_date
            
        # İşten çıkış tarihi dönemden önceyse
        if end_date and end_date < period_end:
            effective_end = end_date
            
        # Geçersiz aralık kontrolü (Örn: Dönem bitmeden işten çıkmış ama dönem başı işe başlamamış gibi)
        if effective_start > effective_end:
            return 0
            
        # Günleri say
        daterange = pd.date_range(start=effective_start, end=effective_end)
        workdays = daterange[daterange.weekday < 5] # Weekdays
        
        # Tatilleri düş
        if holidays:
            holiday_list = []
            for h in holidays:
                if isinstance(h, pd.Timestamp):
                    holiday_list.append(h.date())
                elif isinstance(h, datetime): # datetime is subclass of date, check carefully
                     holiday_list.append(h.date())
                elif isinstance(h, date):
                    holiday_list.append(h)
                
            workdays = [d for d in workdays if d.date() not in holiday_list]
            
        return len(workdays)
        
    except Exception as e:
        print(f"Efektif gün hesaplama hatası: {e}")
        # Hata detayını görmezden gel, 0 dön (production safe)
        return 0

