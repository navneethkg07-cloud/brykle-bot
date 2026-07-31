import json
from typing import Optional

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from config import (
    ACCOUNTS_SHEET_ID,
    CREDS_JSON,
    SALES_SHEET_ID,
    STOCK_SHEET_ID,
    logger,
)
from utils.helpers import normalize_text

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

_client: Optional[gspread.Client] = None
_accounts_sheet: Optional[object] = None
_sales_sheet: Optional[object] = None
_stock_sheet: Optional[object] = None


class InMemorySheet:
    def __init__(self, headers: list[str]):
        self.headers = headers
        self.rows: list[list[object]] = []

    def get_all_values(self) -> list[list[object]]:
        return [self.headers] + list(self.rows)

    def get_all_records(self) -> list[dict[str, object]]:
        return [{self.headers[i]: row[i] for i in range(len(self.headers))} for row in self.rows]

    def append_row(self, row: list[object]) -> None:
        self.rows.append(list(row))

    def update(self, range_name: str, values: list[list[object]]) -> None:
        self.rows = values[1:] if values else []

    def update_cell(self, row_index: int, col_index: int, value: object) -> None:
        while len(self.rows) < row_index - 1:
            self.rows.append([""] * len(self.headers))
        if row_index - 2 < len(self.rows):
            self.rows[row_index - 2][col_index - 1] = value


def _ensure_headers(sheet: object, headers: list[str]) -> None:
    values = sheet.get_all_values()
    if values and values[0]:
        return
    sheet.update("A1:" + chr(64 + len(headers)) + "1", [headers])


def connect() -> None:
    global _client, _accounts_sheet, _sales_sheet, _stock_sheet
    if _client is not None:
        return

    if not CREDS_JSON:
        logger.warning("CREDS_JSON not set; using in-memory sheets for local testing.")
        _accounts_sheet = InMemorySheet(["Date", "Person", "Type", "Amount", "Notes", "Proof"])
        _sales_sheet = InMemorySheet(["Date", "Customer", "Order", "Payment"])
        _stock_sheet = InMemorySheet(["Product", "Stock"])
        return

    try:
        creds_dict = json.loads(CREDS_JSON)
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        _client = gspread.authorize(credentials)
        logger.info("Connected to Google Sheets service account.")

        accounts_workbook = _client.open_by_key(ACCOUNTS_SHEET_ID)
        sales_workbook = _client.open_by_key(SALES_SHEET_ID)
        stock_workbook = _client.open_by_key(STOCK_SHEET_ID)

        _accounts_sheet = accounts_workbook.sheet1
        _sales_sheet = sales_workbook.sheet1
        _stock_sheet = stock_workbook.sheet1

        _ensure_headers(_accounts_sheet, ["Date", "Person", "Type", "Amount", "Notes", "Proof"])
        _ensure_headers(_sales_sheet, ["Date", "Customer", "Order", "Payment"])
        _ensure_headers(_stock_sheet, ["Product", "Stock"])
        logger.info("Google Sheets headers initialized successfully.")
    except Exception:
        logger.exception("Failed to initialize Google Sheets connection.")
        raise


def get_accounts_sheet() -> object:
    connect()
    assert _accounts_sheet is not None
    return _accounts_sheet


def get_sales_sheet() -> object:
    connect()
    assert _sales_sheet is not None
    return _sales_sheet


def get_stock_sheet() -> object:
    connect()
    assert _stock_sheet is not None
    return _stock_sheet


def get_stock_quantity(product_name: str) -> int:
    sheet = get_stock_sheet()
    records = sheet.get_all_records()
    for row in records:
        if normalize_text(row.get("Product", "")) == normalize_text(product_name):
            try:
                return int(row.get("Stock", 0) or 0)
            except (TypeError, ValueError):
                return 0
    return 0

