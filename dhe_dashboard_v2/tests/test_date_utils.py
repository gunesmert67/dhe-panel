
import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date, datetime
import pandas as pd
from core.date_utils import get_weekday_count, calculate_effective_workdays

class TestDateUtils(unittest.TestCase):
    def test_get_weekday_count(self):
        # 2024 Mart ayı için hafta içi gün sayısı (21 gün)
        count = get_weekday_count(2024, 3, until_today=False)
        self.assertEqual(count, 21) # Mart 2024: 1 ve 29, 30, 31 hafta sonu degilse kontrol et
        
        # Datetime objesi ile tatil testi
        holidays = {date(2024, 3, 1)} # 1 Mart tatil olsun
        count_holiday = get_weekday_count(2024, 3, until_today=False, holidays=holidays)
        self.assertEqual(count_holiday, 20)

    def test_calculate_effective_workdays_timestamp_input(self):
        # Timestamp girdisi ile test
        start = pd.Timestamp("2024-01-01")
        end = pd.Timestamp("2024-01-31")
        
        # Ocak 2024: 23 iş günü (1 Ocak Pazartesi)
        days = calculate_effective_workdays(2024, 1, start_date=start, end_date=end)
        self.assertTrue(days > 0)
        
    def test_calculate_effective_workdays_nat_input(self):
        # NaT (Not a Time) girdisi ile test - Crash etmemeli
        start = pd.Timestamp("2024-01-01")
        end = pd.NaT # İşten çıkış yok (devam ediyor)
        
        # 2024 Ocak ayı boyunca çalışmış (çıkış yok)
        days = calculate_effective_workdays(2024, 1, start_date=start, end_date=end)
        # Ocak 2024: 23 iş günü
        # 1 Ocak Pazartesi -> Tatil listesinde yoksa iş günü sayılır.
        self.assertEqual(days, 23) 

    def test_calculate_effective_workdays_holiday_subtraction(self):
        # Tatil düşümü testi
        pass

if __name__ == '__main__':
    unittest.main()
