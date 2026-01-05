ID = "fraction_number"
TITLE = "Fraction"
TAGS = ["primitives", "fraction"]
DISPLAY_INPUT = "Fraction(1, 3)"
EXPECTED = "A Fraction 1/3."


def build():
    from fractions import Fraction

    return Fraction(1, 3)
