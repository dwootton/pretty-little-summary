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


def describe_path(path: Path, deep: bool = True, full: bool = False) -> MetaDescription:
    """Describe a filesystem path.

    By default (``deep=True``) a *file* is loaded into a rich object (e.g. a
    DataFrame) and described by the adapter system when a suitable library is
    installed, and a *directory* is walked with each dataset deep-profiled; if
    deep loading fails or is unavailable, the sniffed (zero-dependency,
    head-bytes-only) result stands. Pass ``deep=False`` to use only the
    zero-dependency sniffer tier.

    Args:
        path: File or directory to describe.
        deep: Load files into rich objects / deep-profile directory contents.
        full: When deep-loading a row-oriented file, read every row instead of
            a bounded sample.
    """
    # Directories: hand off to the directory walker regardless of deep, which
    # sniffs each file (shallow) or deep-profiles each dataset (deep).
    if path.is_dir():
        from pretty_little_summary.adapters.pathlib_adapter import describe_directory

        return describe_directory(path, deep=deep)

    meta = sniff_path(path)
    if meta is None:
        return {
            "object_type": "builtins.file",
            "adapter_used": "SnifferRegistry",
            "warnings": [f"Could not read file: {path}"],
        }

    if deep:
        deep_meta = _try_deep_load(path, full=full)
        if deep_meta is not None:
            deep_meta.setdefault("metadata", {})["sniffed"] = meta.get("metadata")
            return deep_meta

    return meta


def _try_deep_load(path: Path, full: bool = False) -> MetaDescription | None:
    """Best-effort rich load via installed libraries; None if unavailable."""
    import warnings

    from pretty_little_summary.adapters import dispatch_adapter
    from pretty_little_summary.file_loader import load_file_sampled

    try:
        obj, was_sampled, sampled_rows = load_file_sampled(path, full=full)
    except Exception as exc:
        # Deep loading is best-effort: any failure here (missing optional
        # dependency, a malformed file, a library bug) falls back to the
        # zero-dependency sniffed result rather than raising. Surface it as a
        # warning so a real bug isn't mistaken for "library not installed" —
        # this doesn't affect describe()'s returned content, only stderr.
        warnings.warn(
            f"deep load of {path} failed, falling back to sniffed result: "
            f"{exc!r}",
            RuntimeWarning,
            stacklevel=2,
        )
        return None
    if isinstance(obj, (str, bytes)):
        # load_file fell back to raw text/bytes: the sniffer already does better.
        return None
    try:
        result = dispatch_adapter(obj)
    finally:
        _close_quietly(obj)
    if was_sampled:
        md = result.setdefault("metadata", {})
        md["sampled"] = True
        md["sampled_rows"] = sampled_rows
    return result


def _close_quietly(obj: Any) -> None:
    close = getattr(obj, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            pass
