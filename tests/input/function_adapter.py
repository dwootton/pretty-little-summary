ID = "function_adapter"
TITLE = "Function"
TAGS = ["stdlib", "callable"]
DISPLAY_INPUT = "def haversine_distance(lat1, lon1, lat2, lon2) -> float: ..."
EXPECTED = (
    "A callable function haversine_distance(lat1: float, lon1: float, "
    "lat2: float, lon2: float) -> float. Docstring: 'Great-circle distance "
    "between two lat/lon points, in kilometers.'."
)


def build():
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance between two lat/lon points, in kilometers."""
        return 0.0

    return haversine_distance
