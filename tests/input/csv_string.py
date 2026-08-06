ID = "csv_string"
TITLE = "CSV string"
TAGS = ["text", "csv"]
DISPLAY_INPUT = "city,population,state,founded\\nAustin,964254,TX,1839\\n..."
EXPECTED = (
    "A CSV string with 7 rows and 4 columns (,-delimited). Header: 'city', "
    "'population', 'state', 'founded'. Sample: [\"'Austin'\", \"'964254'\", "
    "\"'TX'\", \"'1839'\"]. Column types: str, int, str, int. Best displayed as "
    "sortable table."
)


def build():
    rows = [
        ("Austin", 964254, "TX", 1839),
        ("Denver", 715522, "CO", 1858),
        ("Seattle", 737015, "WA", 1851),
        ("Boston", 654776, "MA", 1630),
        ("Miami", 442241, "FL", 1896),
        ("Portland", 652503, "OR", 1845),
    ]
    lines = ["city,population,state,founded"]
    lines.extend(",".join(str(field) for field in row) for row in rows)
    return "\n".join(lines) + "\n"
