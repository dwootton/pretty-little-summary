ID = "matplotlib_adapter"
TITLE = "Matplotlib figure"
TAGS = ["matplotlib", "chart"]
REQUIRES = ['matplotlib']
DISPLAY_INPUT = "plt.subplots(); ax.plot([1, 2, 3], [3, 2, 1])"


def build():
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [3, 2, 1], label="series")
    return fig


def expected(meta):
    count = meta.get("metadata", {}).get("num_subplots") or "unknown"
    return f"A matplotlib figure with {count} subplots."
