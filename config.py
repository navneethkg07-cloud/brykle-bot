import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger("brykle_bot")

TOKEN = os.getenv("TOKEN", "").strip()
CREDS_JSON = os.getenv("CREDS_JSON", "").strip()
ACCOUNTS_SHEET_ID = os.getenv("ACCOUNTS_SHEET_ID", "1pDqNEVtNxAjJ8bnv2QQdkGVXYIOnB0dd4BWCajr5dCc").strip()
SALES_SHEET_ID = os.getenv("SALES_SHEET_ID", "1D52RCh0IiyP0MP5wtik4A1LOAZG_Ofkgo6pPnreRGfs").strip()
STOCK_SHEET_ID = os.getenv("STOCK_SHEET_ID", "1Bz_3h-WR6tuQB7ny0tm8_ac3erD289xUpNuXSRpFL9c").strip()
