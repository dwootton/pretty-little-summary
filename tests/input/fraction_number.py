ID = "fraction_number"
TITLE = "Fraction"
TAGS = ["primitives", "fraction"]
DISPLAY_INPUT = "Fraction(355, 113)  # pi approximation"
EXPECTED = "A Fraction 355/113."


def build():
    from fractions import Fraction

    return Fraction(355, 113)
