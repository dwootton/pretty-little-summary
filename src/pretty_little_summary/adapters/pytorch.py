"""Pytorch adapter."""

from typing import Any

try:
    import torch
    import torch.nn as nn
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class PytorchAdapter:
    """Adapter for PyTorch nn.Module and Tensor objects."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, (nn.Module, torch.Tensor))
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        try:
            if isinstance(obj, torch.Tensor):
                meta: MetaDescription = {
                    "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
                    "adapter_used": "PytorchAdapter",
                }
                metadata: dict[str, Any] = {
                    "type": "torch_tensor",
                    "shape": tuple(obj.shape),
                    "dtype": str(obj.dtype),
                    "device": str(obj.device),
                    "requires_grad": obj.requires_grad,
                }
                meta["metadata"] = metadata
                meta["nl_summary"] = f"A PyTorch tensor with shape {metadata.get('shape')}."
                return meta

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

            meta["nl_summary"] = f"A PyTorch model {meta['object_type']}."
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
