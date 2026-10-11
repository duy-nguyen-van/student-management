"""Kiểm tra dữ liệu học sinh trước khi lưu."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

_CENT = Decimal("0.01")
_MIN_SCORE = Decimal("0")
_MAX_SCORE = Decimal("10")


class ValidationError(ValueError):
    """Dữ liệu người dùng không hợp lệ."""


def validate_student_fields(
    name: object,
    age: object,
    math: object,
    literature: object,
    english: object,
) -> tuple[str, int, Decimal, Decimal, Decimal]:
    cleaned_name = _require_name(name)
    cleaned_age = _require_age(age)
    return (
        cleaned_name,
        cleaned_age,
        _require_score(math, "Toán"),
        _require_score(literature, "Văn"),
        _require_score(english, "Anh"),
    )


def _require_name(name: object) -> str:
    if not isinstance(name, str):
        raise ValidationError("Tên không được để trống.")
    cleaned = " ".join(name.split())
    if not cleaned:
        raise ValidationError("Tên không được để trống.")
    return cleaned


def _require_age(age: object) -> int:
    if isinstance(age, bool) or isinstance(age, float):
        raise ValidationError("Tuổi phải là số nguyên từ 1 đến 120.")
    if isinstance(age, int):
        value = age
    elif isinstance(age, str):
        text = age.strip()
        if not text.isdigit():
            raise ValidationError("Tuổi phải là số nguyên từ 1 đến 120.")
        value = int(text)
    else:
        raise ValidationError("Tuổi phải là số nguyên từ 1 đến 120.")
    if value < 1 or value > 120:
        raise ValidationError("Tuổi phải là số nguyên từ 1 đến 120.")
    return value


def _require_score(score: object, subject: str) -> Decimal:
    try:
        if isinstance(score, bool) or score is None:
            raise InvalidOperation
        if isinstance(score, str):
            text = score.strip().replace(",", ".")
            if not text:
                raise InvalidOperation
            value = Decimal(text)
        else:
            value = Decimal(str(score))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"Điểm {subject} phải từ 0 đến 10.") from exc
    if not value.is_finite():
        raise ValidationError(f"Điểm {subject} phải từ 0 đến 10.")
    quantized = value.quantize(_CENT, rounding=ROUND_HALF_UP)
    if quantized < _MIN_SCORE or quantized > _MAX_SCORE:
        raise ValidationError(f"Điểm {subject} phải từ 0 đến 10.")
    return quantized
