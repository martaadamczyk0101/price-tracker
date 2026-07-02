from decimal import ROUND_HALF_UP, Decimal


def format_price(value, currency="zł"):
    if value is None:
        return ""

    price = Decimal(str(value)).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

    return f"{price} {currency}"
