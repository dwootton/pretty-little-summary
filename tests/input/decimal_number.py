ID = "decimal_number"
TITLE = "Decimal"
TAGS = ["primitives", "decimal"]
DISPLAY_INPUT = "Decimal('12.34')"
EXPECTED = "A Decimal value 12.34 with 4 digits of precision."


def build():
    from decimal import Decimal

    return Decimal("12.34")
