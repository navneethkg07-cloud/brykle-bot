from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


def normalize_text(value: str) -> str:
    return " ".join(str(value).strip().split()).lower()


def current_date() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")


def parse_amount(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Amount must be numeric.") from exc


def format_currency(value: float | int | Decimal | str) -> str:
    amount = Decimal(str(value))
    return f"₹{amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,.2f}"
