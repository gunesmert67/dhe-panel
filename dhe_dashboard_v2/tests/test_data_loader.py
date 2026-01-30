
import pytest
import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from core.data_loader import process_finance_dataframe

def test_process_finance_dataframe_currency_conversion():
    """Test that currency conversion works correctly."""
    
    # Mock input data
    data = {
        "Teklif_No": ["1", "2"],
        "Musteri": ["A", "B"],
        "Personel": ["P1", "P2"],
        "Tarih": ["01.01.2024", "01.01.2024"],
        "Tutar_Ham": [100, 100],
        "Maliyet_Ham": [50, 50],
        "Para_Birimi": ["EUR", "USD"]
    }
    df = pd.DataFrame(data)
    
    # Mock rates map
    # 2024 USD rate comes from constants.py if not in map, but let's provide a map
    monthly_rates = {
        (2024, 1, 'USD'): 0.92,  # 1 USD = 0.92 EUR
        (2024, 1, 'EUR'): 1.0
    }
    
    personel_dict = {"P1": "Person 1", "P2": "Person 2"}
    
    df_result = process_finance_dataframe(df, "Teklif_No", monthly_rates, personel_dict)
    
    # Check EUR row (Rate 1.0)
    assert df_result.iloc[0]["Tutar_EUR"] == 100.0
    assert df_result.iloc[0]["Exchange_Rate"] == 1.0
    
    # Check USD row (Rate 0.92)
    assert df_result.iloc[1]["Tutar_EUR"] == 100.0 * 0.92
    assert df_result.iloc[1]["Exchange_Rate"] == 0.92

def test_process_finance_dataframe_cleaning():
    """Test that data cleaning (money strings, dates) works."""
    data = {
        "Teklif_No": ["1"],
        "Musteri": ["A"],
        "Personel": ["P1"],
        "Tarih": ["01.01.2024"],
        "Tutar_Ham": ["1.000,50"], # String format TR
        "Maliyet_Ham": ["500,00"], 
        "Para_Birimi": ["EUR"]
    }
    df = pd.DataFrame(data)
    monthly_rates = {}
    personel_dict = {}
    
    df_result = process_finance_dataframe(df, "Teklif_No", monthly_rates, personel_dict)
    
    assert df_result.iloc[0]["Tutar_Ham"] == 1000.50
    assert df_result.iloc[0]["Maliyet_Ham"] == 500.00
    assert df_result.iloc[0]["Tutar_EUR"] == 1000.50 # Rate default 1.0 for EUR
