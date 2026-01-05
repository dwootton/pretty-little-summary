ID = "matplotlib_axes_image_hist"
TITLE = "Matplotlib axes (image + hist)"
TAGS = ["matplotlib", "chart"]
REQUIRES = ['matplotlib']
DISPLAY_INPUT = "ax.imshow(...); ax.hist(...)"
EXPECTED = "A matplotlib axes with plotted elements."


def build():
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.imshow([[0, 1], [1, 0]])
    ax.hist([1, 2, 2, 3, 3, 3])
    return ax
