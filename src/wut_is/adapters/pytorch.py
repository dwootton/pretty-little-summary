"""Pytorch adapter."""

from typing import Any

try:
    import torch.nn as nn
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from wut_is.adapters._base import AdapterRegistry
from wut_is.core import MetaDescription


class PytorchAdapter:
    """Adapter for PyTorch nn.Module."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, nn.Module)
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        try:
            meta: MetaDescription = {
                "object_type": f"torch.nn.{obj.__class__.__name__}",
                "adapter_used": "PytorchAdapter",
            }

            # Get architecture via named_children
            try:
                architecture = {name: str(child) for name, child in obj.named_children()}
                if architecture:
                    meta["metadata"] = {"architecture": architecture}
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get architecture: {e}")

            # Calculate parameter counts
            try:
                total_params = sum(p.numel() for p in obj.parameters())
                trainable_params = sum(p.numel() for p in obj.parameters() if p.requires_grad)
                meta["parameter_count"] = total_params
                meta["parameters"] = {
                    "total": total_params,
                    "trainable": trainable_params,
                }
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not count parameters: {e}")

            # Get device
            try:
                params = list(obj.parameters())
                if params:
                    meta["metadata"] = meta.get("metadata", {})
                    meta["metadata"]["device"] = str(params[0].device)
            except Exception:
                pass

            return meta

        except Exception as e:
            return {
                "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
                "adapter_used": "PytorchAdapter (failed)",
                "warnings": [f"Adapter failed: {e}"],
                "raw_repr": repr(obj)[:500],
            }



# Auto-register if library is available
if LIBRARY_AVAILABLE:
    AdapterRegistry.register(PytorchAdapter)
