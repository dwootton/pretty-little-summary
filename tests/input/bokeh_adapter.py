ID = "bokeh_adapter"
TITLE = "Bokeh figure"
TAGS = ["bokeh", "chart"]
REQUIRES = ['bokeh']
DISPLAY_INPUT = "figure().line([1, 2], [3, 4])"


def build():
    from bokeh.plotting import figure

    fig = figure()
    fig.line([1, 2], [3, 4])
    return fig


def expected(meta):
    return f"A Bokeh figure with {meta['metadata'].get('renderers')} renderers."
