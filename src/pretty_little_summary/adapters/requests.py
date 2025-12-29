"""Requests adapter."""

from typing import Any

try:
    import requests
    LIBRARY_AVAILABLE = True
except ImportError:
    LIBRARY_AVAILABLE = False

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class RequestsAdapter:
    """Adapter for Requests Response objects."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        if not LIBRARY_AVAILABLE:
            return False
        try:
            return isinstance(obj, requests.Response)
        except Exception:
            return False

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        try:
            meta: MetaDescription = {
                "object_type": "requests.Response",
                "adapter_used": "RequestsAdapter",
            }

            # Status code and URL
            try:
                meta["status_code"] = obj.status_code
                meta["url"] = obj.url
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get status/url: {e}")

            # Headers
            try:
                meta["headers"] = dict(obj.headers)
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not get headers: {e}")

            # Content type
            try:
                content_type = obj.headers.get("Content-Type", "")
                meta["metadata"] = {"content_type": content_type}

                # If JSON, get top-level keys
                if "json" in content_type.lower():
                    try:
                        json_data = obj.json()
                        if isinstance(json_data, dict):
                            meta["metadata"]["json_keys"] = list(json_data.keys())
                    except Exception:
                        pass
                else:
                    # Text preview
                    try:
                        meta["metadata"]["text_preview"] = obj.text[:500]
                    except Exception:
                        pass
            except Exception as e:
                meta.setdefault("warnings", []).append(f"Could not process content: {e}")

            if "status_code" in meta:
                meta["nl_summary"] = f"An HTTP response with status {meta['status_code']}."
            return meta

        except Exception as e:
            return {
                "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
                "adapter_used": "RequestsAdapter (failed)",
                "warnings": [f"Adapter failed: {e}"],
                "raw_repr": repr(obj)[:500],
            }



# Auto-register if library is available
if LIBRARY_AVAILABLE:
    AdapterRegistry.register(RequestsAdapter)
