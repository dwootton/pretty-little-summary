ID = "html_string"
TITLE = "HTML string"
TAGS = ["text", "html"]
DISPLAY_INPUT = "<html>... nav, quarterly report table ...</html>"
EXPECTED = "An HTML document or fragment."


def build():
    return (
        "<html>\n"
        "<head><title>Dashboard</title></head>\n"
        "<body>\n"
        '  <nav><a href="/home">Home</a><a href="/reports">Reports</a></nav>\n'
        '  <div class="content">\n'
        "    <h1>Quarterly Report</h1>\n"
        "    <table><tr><th>Q</th><th>Revenue</th></tr>"
        "<tr><td>Q1</td><td>1.2M</td></tr></table>\n"
        "  </div>\n"
        "</body>\n"
        "</html>"
    )
