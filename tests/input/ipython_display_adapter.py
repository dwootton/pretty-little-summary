ID = "ipython_display_adapter"
TITLE = "IPython display"
TAGS = ["ipython", "display"]
REQUIRES = ['IPython']
DISPLAY_INPUT = "HTML('<h1>Hi</h1>')"
EXPECTED = "An IPython display object with representations: _repr_html_."


def build():
    from IPython.display import HTML

    return HTML("<h1>Hi</h1>")
