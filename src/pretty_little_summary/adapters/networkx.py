"""NetworkX adapter."""

from typing import Any

try:
    import networkx as nx
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class NetworkXAdapter:
    """Adapter for NetworkX graphs."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, nx.Graph)
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        try:
            import networkx as nx

            meta: MetaDescription = {
                "object_type": f"networkx.{obj.__class__.__name__}",
                "adapter_used": "NetworkXAdapter",
            }

            # Node and edge counts
            try:
                meta["node_count"] = obj.number_of_nodes()
                meta["edge_count"] = obj.number_of_edges()
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get node/edge count: {e}")

            # Density
            try:
                meta["density"] = nx.density(obj)
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get density: {e}")

            # Directed or not
            try:
                meta["metadata"] = {"is_directed": obj.is_directed()}
            except Exception:
                pass

            # Sample first node with attributes
            try:
                nodes = list(obj.nodes(data=True))
                if nodes:
                    meta["metadata"] = meta.get("metadata", {})
                    meta["metadata"]["sample_node"] = nodes[0]
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get sample node: {e}")

            if meta.get("node_count") is not None and meta.get("edge_count") is not None:
                meta["nl_summary"] = (
                    f"A networkx graph with {meta['node_count']} nodes and {meta['edge_count']} edges."
                )
            return meta

        except Exception as e:
            return {
                "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
                "adapter_used": "NetworkXAdapter (failed)",
                "warnings": [f"Adapter failed: {e}"],
                "raw_repr": repr(obj)[:500],
            }



# Auto-register if library is available
if LIBRARY_AVAILABLE:
    AdapterRegistry.register(NetworkXAdapter)
