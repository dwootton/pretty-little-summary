"""Matplotlib adapter."""

from typing import Any

try:
    import matplotlib.figure
    import matplotlib.axes
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from wut_is.adapters._base import AdapterRegistry
from wut_is.core import MetaDescription


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
            import matplotlib.figure
            import matplotlib.axes

            is_figure = isinstance(obj, matplotlib.figure.Figure)

            meta: MetaDescription = {
                "object_type": "matplotlib.figure.Figure"
                if is_figure
                else "matplotlib.axes.Axes",
                "adapter_used": "MatplotlibAdapter",
                "style": "imperative",  # Flag to prioritize history
            }

            # Get axes
            if is_figure:
                axes_list = obj.axes
                if axes_list:
                    axes = axes_list[0]  # Use first axes
                    meta["metadata"] = {"num_subplots": len(axes_list)}
                else:
                    axes = None
            else:
                axes = obj

            # Extract visual elements
            visual_elements = {}
            if axes is not None:
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
                        visual_elements["legend_labels"] = [
                            t.get_text() for t in legend.get_texts()
                        ]
                except Exception:
                    pass

                try:
                    visual_elements["num_artists"] = len(axes.get_children())
                except Exception:
                    pass

            if visual_elements:
                meta["visual_elements"] = visual_elements

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
