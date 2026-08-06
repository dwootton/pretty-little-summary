ID = "decimal_number"
TITLE = "Decimal"
TAGS = ["primitives", "decimal"]
DISPLAY_INPUT = "Decimal('48219.7563')"
EXPECTED = "A Decimal value 48219.7563 with 9 digits of precision."


def build():
    from decimal import Decimal

    return Decimal("48219.7563")
