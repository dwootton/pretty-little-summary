"""Sniffer protocol, registry, and the file-description entry point."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar, Protocol, runtime_checkable

from pretty_little_summary.core import MetaDescription

# How many leading bytes a sniffer is allowed to look at. Enough to read any
# file header/magic and a useful sample of rows, small enough to stay cheap on
# huge files. Read once and shared across all sniffers for a given file.
HEAD_BYTES = 65_536

# Priority tiers (higher checked first). Binary formats identify themselves with
# unambiguous magic bytes, so they win over content-sniffed text formats, which
# in turn win over the raw-text fallback.
PRIORITY_MAGIC = 100
PRIORITY_TEXT = 50
PRIORITY_FALLBACK = 0


@runtime_checkable
class Sniffer(Protocol):
    """Describes a file from its path and a leading byte sample."""

    name: str

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool: ...

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription: ...


class SnifferRegistry:
    """Priority-ordered registry of file sniffers (mirrors AdapterRegistry)."""

    _entries: ClassVar[list[tuple[int, int, type[Sniffer]]]] = []
    _seq: int = 0

    @classmethod
    def register(cls, sniffer: type[Sniffer], priority: int = PRIORITY_TEXT) -> None:
        if any(existing is sniffer for _, _, existing in cls._entries):
            return
        cls._entries.append((priority, cls._seq, sniffer))
        cls._seq += 1
        cls._entries.sort(key=lambda e: (-e[0], e[1]))

    @classmethod
    def unregister(cls, sniffer: type[Sniffer]) -> None:
        cls._entries = [e for e in cls._entries if e[2] is not sniffer]

    @classmethod
    def sniffers(cls) -> list[type[Sniffer]]:
        return [s for _, _, s in cls._entries]


_loaded = False


def load_all_sniffers() -> None:
    """Import built-in sniffer modules once (idempotent)."""
    global _loaded
    if _loaded:
        return
    from importlib import import_module

    for name in ("binary", "text"):
        import_module(f"pretty_little_summary.sniffers.{name}")
    _loaded = True


def _read_head(path: Path, n: int = HEAD_BYTES) -> bytes:
    with open(path, "rb") as fh:
        return fh.read(n)


def sniff_path(path: Path) -> MetaDescription | None:
    """Describe a file using only zero-dependency sniffers.

    Returns ``None`` only if the path is unreadable; otherwise the highest
    priority sniffer that claims the file wins, falling back to a raw-bytes
    sniffer that always succeeds.
    """
    load_all_sniffers()
    try:
        head = _read_head(path)
    except OSError:
        return None

    for sniffer in SnifferRegistry.sniffers():
        try:
            if sniffer.can_sniff(path, head):
                return sniffer.sniff(path, head)
        except Exception:
            # A sniffer must never break description; try the next one.
            continue
    return None


def describe_path(path: Path, deep: bool = False) -> MetaDescription:
    """Describe a filesystem path.

    By default this uses only the zero-dependency sniffer tier. When
    ``deep=True`` and a suitable library is installed, the file is additionally
    loaded into a rich object (e.g. a DataFrame) and described by the adapter
    system; if deep loading fails or is unavailable, the sniffed result stands.
    """
    meta = sniff_path(path)
    if meta is None:
        return {
            "object_type": "builtins.file",
            "adapter_used": "SnifferRegistry",
            "warnings": [f"Could not read file: {path}"],
        }

    if deep:
        deep_meta = _try_deep_load(path)
        if deep_meta is not None:
            deep_meta.setdefault("metadata", {})["sniffed"] = meta.get("metadata")
            return deep_meta

    return meta


def _try_deep_load(path: Path) -> MetaDescription | None:
    """Best-effort rich load via installed libraries; None if unavailable."""
    from pretty_little_summary.adapters import dispatch_adapter
    from pretty_little_summary.file_loader import load_file

    try:
        obj = load_file(path)
    except Exception:
        return None
    if isinstance(obj, (str, bytes)):
        # load_file fell back to raw text/bytes: the sniffer already does better.
        return None
    try:
        result = dispatch_adapter(obj)
    finally:
        _close_quietly(obj)
    return result


def _close_quietly(obj: Any) -> None:
    close = getattr(obj, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            pass
