"""Điểm trung bình và xếp loại học lực."""

from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")
_GIOI = Decimal("8.0")
_KHA = Decimal("6.5")
_TRUNG_BINH = Decimal("5.0")


def average(math: Decimal, literature: Decimal, english: Decimal) -> Decimal:
    total = Decimal(math) + Decimal(literature) + Decimal(english)
    return (total / Decimal(3)).quantize(_CENT, rounding=ROUND_HALF_UP)


def classify(score: Decimal) -> str:
    if score >= _GIOI:
        return "Giỏi"
    elif score >= _KHA:
        return "Khá"
    elif score >= _TRUNG_BINH:
        return "Trung bình"
    else:
        return "Yếu"
