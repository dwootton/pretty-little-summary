ID = "matplotlib_axes_inference"
TITLE = "Matplotlib axes (scatter + bar)"
TAGS = ["matplotlib", "chart"]
REQUIRES = ['matplotlib']
DISPLAY_INPUT = "ax.scatter(...); ax.bar(...)"
EXPECTED = "A matplotlib axes showing a scatter plot and a bar/histogram plot."


def build():
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.scatter([1, 2, 3], [3, 2, 1])
    ax.bar([1, 2, 3], [3, 2, 1])
    return ax
