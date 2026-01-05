ID = "csv_string"
TITLE = "CSV string"
TAGS = ["text", "csv"]
DISPLAY_INPUT = "a,b,c\\n1,2,3\\n4,5,6\\n"
EXPECTED = "A CSV string with 3 rows and 3 columns (,-delimited). Header: 'a', 'b', 'c'. Sample: [\"'1'\", \"'2'\", \"'3'\"]. Column types: int, int, int. Best displayed as sortable table."


def build():
    return "a,b,c\n1,2,3\n4,5,6\n"
