
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import logging
from typing import Dict, Optional, List, Any
from core.utils import retry_on_exception

logger = logging.getLogger(__name__)

# Constants
CREDENTIALS_PATH = "data/credentials.json"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

@retry_on_exception(max_retries=3, delay=2)
def get_gspread_client():
    """Google Sheets API istemcisini döndürür (Singleton pattern)."""
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, SCOPE)
    client = gspread.authorize(creds)
    return client

@retry_on_exception(max_retries=3, delay=2)
def open_spreadsheet(client, file_name):
    """Google Sheets dosyasını açar (Retry destekli)."""
    return client.open(file_name)

@retry_on_exception(max_retries=3, delay=2)
def fetch_sheet_data(spreadsheet, sheet_name):
    """Sekme verilerini çeker (Retry destekli)."""
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except gspread.exceptions.WorksheetNotFound:
        # Fallback: Case-insensitive arama
        target_name = str(sheet_name).strip().lower()
        found_ws = None
        
        try:
            # Tüm sekmeleri tara
            all_ws = spreadsheet.worksheets()
            for ws in all_ws:
                if ws.title.strip().lower() == target_name:
                    found_ws = ws
                    break
        except:
            pass
            
        if found_ws:
            worksheet = found_ws
        else:
            raise
            
    return worksheet.get_all_values()

def safe_read_gsheet(client, spreadsheet, sheet_name: str, column_mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Google Sheets'ten belirtilen sekmeyi güvenli bir şekilde okur.
    Hata durumunda boş DataFrame döndürür.
    """
    try:
        data = fetch_sheet_data(spreadsheet, sheet_name)
        
        if len(data) < 2:
            logger.warning(f"'{sheet_name}' sekmesinde veri bulunamadı")
            return pd.DataFrame()
        
        # İlk satır başlık, geri kalanı veri
        headers = data[0]
        rows = data[1:]
        
        df = pd.DataFrame(rows, columns=headers)
        
        # Boş satırları temizle
        df = df.replace('', pd.NA).dropna(how='all')
        
        if not df.empty and column_mapping:
            # Sütun isimlerindeki boşlukları temizle
            df.columns = df.columns.astype(str).str.strip()
            
            # Case-insensitive mapping hazırlığı
            lower_to_original = {k.lower(): k for k in column_mapping.keys()}
            
            # DataFrame sütunlarını normalize et
            new_columns = []
            for col in df.columns:
                col_lower = col.lower()
                if col_lower in lower_to_original:
                    # Orijinal key'i kullan (örn: "Tarih")
                    new_columns.append(lower_to_original[col_lower])
                else:
                    new_columns.append(col)
            df.columns = new_columns
            
            # Mapping'de olan sütunları seç ve yeniden adlandır
            cols_to_use = [col for col in df.columns if col in column_mapping]
            
            missing_cols = set(column_mapping.keys()) - set(df.columns)
            if missing_cols:
                logger.warning(f"[{sheet_name}] Eksik sütunlar: {missing_cols}")
            
            df = df[cols_to_use].rename(columns=column_mapping)
        
        logger.info(f"[GSheets] {sheet_name}: {len(df)} satır")
        return df
        
    except gspread.exceptions.WorksheetNotFound:
        logger.error(f"'{sheet_name}' sekmesi bulunamadı")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Google Sheets okuma hatası ({sheet_name}): {e}")
        return pd.DataFrame()
