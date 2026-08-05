"""Matplotlib adapter."""

from typing import Any

try:
    import matplotlib.axes
    import matplotlib.figure
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription

# Bar and hist() both populate .patches with one Patch per bar/bin, so a
# patch count does not distinguish "one bar chart" from "one 10-bin
# histogram" — only line/scatter/image counts are trustworthy per-plot-call.
_PLOT_TYPE_LABELS = {
    "line": "line plot",
    "scatter": "scatter plot",
    "bar": "bar/histogram plot",
    "image": "image",
}
_COUNT_KEYS = {"line": "num_lines", "scatter": "num_collections", "image": "num_images"}


def _join_with_and(items: list[str]) -> str:
    if len(items) <= 1:
        return items[0] if items else ""
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _plot_type_phrase(plot_types: list[str], visual_elements: dict) -> str:
    phrases = []
    for plot_type in plot_types:
        label = _PLOT_TYPE_LABELS.get(plot_type, plot_type)
        count = visual_elements.get(_COUNT_KEYS.get(plot_type, ""))
        if count and count > 1:
            phrases.append(f"{count} {label}s")
        else:
            article = "an" if label[0] in "aeiou" else "a"
            phrases.append(f"{article} {label}")
    return _join_with_and(phrases)


def _axes_summary(visual_elements: dict | None) -> str:
    ve = visual_elements or {}
    plot_types = ve.get("plot_types") or []
    if plot_types:
        sentence = f"A matplotlib axes showing {_plot_type_phrase(plot_types, ve)}"
    else:
        sentence = "An empty matplotlib axes (nothing plotted yet)"
    title = ve.get("title")
    if title:
        sentence += f', titled "{title}"'
    parts = [sentence + "."]

    xlabel, ylabel = ve.get("xlabel"), ve.get("ylabel")
    if xlabel or ylabel:
        parts.append(f"Axis labels: x={xlabel or '(none)'}, y={ylabel or '(none)'}.")

    legend = ve.get("legend_labels")
    if legend:
        parts.append(f"Legend: {', '.join(legend)}.")

    return " ".join(parts)


def _subplot_phrase(ve: dict) -> str:
    plot_types = ve.get("plot_types") or []
    if not plot_types:
        return "an empty subplot"
    phrase = _plot_type_phrase(plot_types, ve)
    title = ve.get("title")
    return f'{phrase} (titled "{title}")' if title else phrase


def _figure_summary(num_subplots: int | None, per_axes: list[dict]) -> str:
    if not num_subplots:
        return "A matplotlib figure with no subplots."
    subplot_word = "subplot" if num_subplots == 1 else "subplots"
    sentence = f"A matplotlib figure with {num_subplots} {subplot_word}"

    if num_subplots == 1:
        ve = per_axes[0] if per_axes else {}
        plot_types = ve.get("plot_types") or []
        if plot_types:
            sentence += f", showing {_plot_type_phrase(plot_types, ve)}"
        sentence += "."
        title = ve.get("title")
        if title:
            sentence += f' Title: "{title}".'
        return sentence

    sentence += f", showing: {_join_with_and([_subplot_phrase(ve) for ve in per_axes])}."
    return sentence


def _axes_visual_elements(axes: Any) -> dict:
    """Introspect one Axes into the plot-type/label/legend facts describe() needs."""
    visual_elements: dict[str, Any] = {}

    try:
        visual_elements["title"] = axes.get_title()
    except Exception:
        pass

    try:
        visual_elements["xlabel"] = axes.get_xlabel()
    except Exception:
        pass

    try:
        visual_elements["ylabel"] = axes.get_ylabel()
    except Exception:
        pass

    try:
        legend = axes.get_legend()
        if legend:
            visual_elements["legend_labels"] = [t.get_text() for t in legend.get_texts()]
    except Exception:
        pass

    try:
        visual_elements["num_artists"] = len(axes.get_children())
    except Exception:
        pass

    try:
        visual_elements["num_lines"] = len(axes.get_lines())
    except Exception:
        pass

    try:
        visual_elements["num_collections"] = len(axes.collections)
    except Exception:
        pass

    try:
        visual_elements["num_patches"] = len(axes.patches)
    except Exception:
        pass

    try:
        visual_elements["num_images"] = len(axes.get_images())
    except Exception:
        pass

    # Plot-type inference
    plot_types = []
    try:
        if axes.get_lines():
            plot_types.append("line")
    except Exception:
        pass
    try:
        if axes.collections:
            plot_types.append("scatter")
    except Exception:
        pass
    try:
        if axes.patches:
            plot_types.append("bar")
    except Exception:
        pass
    try:
        if axes.get_images():
            plot_types.append("image")
    except Exception:
        pass
    if plot_types:
        visual_elements["plot_types"] = list(dict.fromkeys(plot_types))

    try:
        visual_elements["xlim"] = axes.get_xlim()
        visual_elements["ylim"] = axes.get_ylim()
    except Exception:
        pass

    return visual_elements


class MatplotlibAdapter:
    """Adapter for Matplotlib Figure/Axes."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, (matplotlib.figure.Figure, matplotlib.axes.Axes))
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        try:
            import matplotlib.axes
            import matplotlib.figure

            is_figure = isinstance(obj, matplotlib.figure.Figure)

            meta: MetaDescription = {
                "object_type": "matplotlib.figure.Figure"
                if is_figure
                else "matplotlib.axes.Axes",
                "adapter_used": "MatplotlibAdapter",
                "style": "imperative",  # Flag to prioritize history
            }

            if is_figure:
                axes_list = obj.axes
                meta["metadata"] = {"num_subplots": len(axes_list)}
                per_axes = [_axes_visual_elements(ax) for ax in axes_list]
                visual_elements = per_axes[0] if per_axes else {}
            else:
                per_axes = []
                visual_elements = _axes_visual_elements(obj)

            if is_figure:
                try:
                    size = obj.get_size_inches()
                    meta["metadata"] = meta.get("metadata", {})
                    meta["metadata"]["figure_size"] = (float(size[0]), float(size[1]))
                    meta["metadata"]["dpi"] = float(obj.dpi)
                except Exception:
                    pass

            if visual_elements:
                meta["visual_elements"] = visual_elements

            if is_figure:
                subplots = meta.get("metadata", {}).get("num_subplots")
                meta["nl_summary"] = _figure_summary(subplots, per_axes)
            else:
                meta["nl_summary"] = _axes_summary(visual_elements)

            return meta

        except Exception as e:
            return {
                "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
                "adapter_used": "MatplotlibAdapter (failed)",
                "warnings": [f"Adapter failed: {e}"],
                "raw_repr": repr(obj)[:500],
            }



# Auto-register if library is available
if LIBRARY_AVAILABLE:
    AdapterRegistry.register(MatplotlibAdapter)
