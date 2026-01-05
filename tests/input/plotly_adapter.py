ID = "plotly_adapter"
TITLE = "Plotly figure"
TAGS = ["plotly", "chart"]
REQUIRES = ['plotly']
DISPLAY_INPUT = "go.Figure(data=[go.Scatter(y=[1, 2, 3])])"


def build():
    from plotly import graph_objs as go

    return go.Figure(data=[go.Scatter(y=[1, 2, 3])])


def expected(meta):
    return f"A Plotly figure with {meta['metadata'].get('traces')} traces."
