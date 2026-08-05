"""Adapter for pathlib Path and PurePath."""

from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.adapters._directory_grouping import (
    FilenameFamily,
    format_family_line,
    group_filename_families,
)
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import format_bytes

# Default configuration for directory scanning. Three independent limits:
#  - DEFAULT_MAX_DEPTH: how many levels deep to recurse.
#  - DEFAULT_MAX_FILES_PER_FOLDER: how many file/family lines ONE directory's
#    own listing may show. A folder with thousands of files (e.g. a sensor
#    archive) can only ever contribute this many lines, so it can never
#    starve sibling files or directories of the global budget below.
#  - DEFAULT_MAX_TOTAL_FILES: a global cap on files actually content-sniffed
#    across the whole walk. Once spent, remaining files are still listed by
#    name (structure stays visible) with a placeholder instead of a real
#    description.
DEFAULT_MAX_DEPTH = 3
DEFAULT_MAX_FILES_PER_FOLDER = 20
DEFAULT_MAX_TOTAL_FILES = 150


class PathlibAdapter:
    """Adapter for Path and PurePath objects."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        return isinstance(obj, PurePath)

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "PathlibAdapter",
        }

        metadata: dict[str, Any] = {
            "type": "path",
            "path": str(obj),
            "name": obj.name,
            "suffix": obj.suffix,
            "parts": list(obj.parts),
        }

        if isinstance(obj, Path):
            try:
                exists = obj.exists()
                metadata["exists"] = exists
                if exists:
                    metadata["is_file"] = obj.is_file()
                    metadata["is_dir"] = obj.is_dir()
                    if obj.is_file():
                        size = obj.stat().st_size
                        metadata["size_bytes"] = size
                        metadata["size"] = format_bytes(size)
                        # Describe the file's *content* with the zero-dependency
                        # sniffer tier (reads only the head; never executes or
                        # fully loads the file).
                        content = _sniff_file(obj)
                        if content:
                            metadata["content"] = content
                    elif obj.is_dir():
                        # Recursively describe directory contents
                        tree_result = _describe_directory_tree(
                            obj,
                            max_depth=DEFAULT_MAX_DEPTH,
                            max_files_per_folder=DEFAULT_MAX_FILES_PER_FOLDER,
                            max_total_files=DEFAULT_MAX_TOTAL_FILES,
                        )
                        metadata["tree"] = tree_result["tree"]
                        metadata["file_count"] = tree_result["file_count"]
                        metadata["dir_count"] = tree_result["dir_count"]
            except Exception:
                pass
        else:
            metadata["pure"] = True

        meta["metadata"] = metadata
        meta["nl_summary"] = _build_nl_summary(metadata)
        return meta


AdapterRegistry.register(PathlibAdapter)


def describe_directory(root_path: Path, deep: bool = False) -> MetaDescription:
    """Describe a directory as a full :class:`MetaDescription`.

    This mirrors what :class:`PathlibAdapter` builds for a directory, but takes
    a ``deep`` flag so callers (``describe_path``) can request that each dataset
    in the tree be fully profiled rather than only head-sniffed.
    """
    tree_result = _describe_directory_tree(
        root_path,
        max_depth=DEFAULT_MAX_DEPTH,
        max_files_per_folder=DEFAULT_MAX_FILES_PER_FOLDER,
        max_total_files=DEFAULT_MAX_TOTAL_FILES,
        deep=deep,
    )
    metadata: dict[str, Any] = {
        "type": "path",
        "path": str(root_path),
        "name": root_path.name,
        "is_dir": True,
        "exists": True,
        "tree": tree_result["tree"],
        "file_count": tree_result["file_count"],
        "dir_count": tree_result["dir_count"],
    }
    meta: MetaDescription = {
        "object_type": "pathlib.PosixPath",
        "adapter_used": "PathlibAdapter",
        "metadata": metadata,
        "nl_summary": _build_nl_summary(metadata),
    }
    return meta


def _describe_directory_tree(
    root_path: Path,
    max_depth: int = DEFAULT_MAX_DEPTH,
    max_files_per_folder: int = DEFAULT_MAX_FILES_PER_FOLDER,
    max_total_files: int = DEFAULT_MAX_TOTAL_FILES,
    deep: bool = False,
) -> dict[str, Any]:
    """
    Recursively describe a directory and its contents.

    Args:
        root_path: Root directory to describe
        max_depth: Maximum depth to traverse
        max_files_per_folder: Maximum number of file/family lines ONE
            directory's own listing may show. Bounding this per folder (not
            globally) means a folder with thousands of files can never
            starve sibling files or folders of display space.
        max_total_files: Global cap on files actually content-described
            (sniffed) across the whole walk. Once spent, further files are
            still listed by name — just without a real description.
        deep: Deep-profile each file (load into a rich object) instead of only
            head-sniffing it.

    Returns:
        Dictionary with tree structure and statistics
    """
    tree_lines: list[str] = []
    file_count = 0
    dir_count = 0
    files_described = 0

    def _describe_for_grouping(path: Path) -> str:
        # Used only to confirm/reject a candidate filename family. Always
        # describes for real — the sampling in group_filename_families
        # already bounds this to a handful of calls per family, so gating
        # it on the global budget too would risk a family "matching" only
        # because every sample hit the placeholder string.
        nonlocal files_described
        files_described += 1
        return _describe_file(path, deep=deep)

    def _describe_or_placeholder(path: Path) -> str:
        nonlocal files_described
        if files_described >= max_total_files:
            return "(not described — total file budget reached)"
        files_described += 1
        return _describe_file(path, deep=deep)

    def _walk_directory(
        path: Path,
        prefix: str = "",
        depth: int = 0,
    ) -> None:
        nonlocal file_count, dir_count

        if depth >= max_depth:
            tree_lines.append(f"{prefix}... (max depth reached)")
            return

        try:
            # Get and sort directory entries
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        except PermissionError:
            tree_lines.append(f"{prefix}... (permission denied)")
            return
        except Exception as e:
            tree_lines.append(f"{prefix}... (error: {e!s})")
            return

        dir_entries = [e for e in entries if e.is_dir()]
        file_entries = [e for e in entries if not e.is_dir()]
        file_count += len(file_entries)
        dir_count += len(dir_entries)

        units = group_filename_families(file_entries, _describe_for_grouping)
        shown_units = units[:max_files_per_folder]
        hidden_units = units[max_files_per_folder:]
        hidden_file_count = sum(
            len(u.members) if isinstance(u, FilenameFamily) else 1 for u in hidden_units
        )

        # Build one combined display list so tree connectors (last-item vs.
        # not) are computed over what's actually shown: subdirectories are
        # never truncated here (a folder is one cheap line regardless of
        # what it contains), only this folder's own file-level units are.
        display_items: list[tuple[str, Any]] = [("dir", d) for d in dir_entries]
        display_items += [
            ("family", u) if isinstance(u, FilenameFamily) else ("file", u)
            for u in shown_units
        ]
        if hidden_file_count:
            display_items.append(("truncated", hidden_file_count))

        for i, (kind, payload) in enumerate(display_items):
            is_last = i == len(display_items) - 1
            connector = "└── " if is_last else "├── "
            extension = "    " if is_last else "│   "

            try:
                if kind == "dir":
                    tree_lines.append(f"{prefix}{connector}{payload.name}/")
                    _walk_directory(payload, prefix + extension, depth + 1)
                elif kind == "family":
                    tree_lines.append(f"{prefix}{connector}{format_family_line(payload)}")
                elif kind == "file":
                    description = _describe_or_placeholder(payload)
                    tree_lines.append(f"{prefix}{connector}{payload.name} - {description}")
                else:  # truncated
                    tree_lines.append(
                        f"{prefix}... ({payload} more files in this folder)"
                    )
            except Exception as e:
                name = payload.name if hasattr(payload, "name") else ""
                tree_lines.append(f"{prefix}{connector}{name} - (error: {e!s})")

    # Start the walk
    _walk_directory(root_path)

    return {
        "tree": "\n".join(tree_lines),
        "file_count": file_count,
        "dir_count": dir_count,
    }


def _sniff_file(file_path: Path) -> dict[str, Any] | None:
    """Return the sniffer's fact document for a file, or None on failure."""
    from pretty_little_summary.sniffers import sniff_path

    try:
        meta = sniff_path(file_path)
    except Exception:
        return None
    if not meta:
        return None
    result: dict[str, Any] = {"summary": meta.get("nl_summary", "")}
    if meta.get("metadata"):
        result["details"] = meta["metadata"]
    return result


def _describe_file(file_path: Path, deep: bool = False) -> str:
    """Describe a single file for the directory tree.

    Shallow (default): uses the zero-dependency sniffer tier — reads only the
    head, never loads the whole file, imports a third-party parser, or executes
    contents (e.g. never unpickles). That keeps directory scans fast and safe.

    Deep: loads the file into a rich object and profiles it (row counts, nulls,
    per-column stats for tabular data), falling back to the sniff when a deep
    load isn't possible. Chosen per-file by the directory walker.
    """
    from pretty_little_summary.sniffers import sniff_path
    from pretty_little_summary.sniffers._base import describe_path

    try:
        if deep:
            meta = describe_path(file_path, deep=True)
        else:
            meta = sniff_path(file_path)
        if meta and meta.get("nl_summary"):
            return meta["nl_summary"]
        if meta:
            return meta.get("object_type", "unknown file type")
    except Exception as e:
        try:
            size = file_path.stat().st_size
            return f"{file_path.suffix or 'unknown file'} ({format_bytes(size)})"
        except Exception:
            return f"(error: {str(e)[:50]})"
    return "unknown file type"


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    path = metadata.get("path")
    pure = metadata.get("pure")

    if pure:
        return f"A pure path '{path}'."

    if metadata.get("exists") is True:
        if metadata.get("is_dir"):
            # Directory with tree
            tree = metadata.get("tree")
            if tree:
                file_count = metadata.get("file_count", 0)
                dir_count = metadata.get("dir_count", 0)
                header = f"{path}/ ({file_count} files, {dir_count} subdirectories)\n"
                return header + tree
            return f"A path '{path}' pointing to an existing directory."

        if metadata.get("is_file"):
            size = metadata.get("size")
            content = metadata.get("content") or {}
            content_summary = content.get("summary")
            if content_summary:
                return f"'{path}': {content_summary}"
            if size:
                return f"A path '{path}' pointing to an existing file ({size})."
            return f"A path '{path}' pointing to an existing file."

        return f"A path '{path}' pointing to an existing location."

    if metadata.get("exists") is False:
        return f"A path '{path}' pointing to a non-existent location."

    return f"A path '{path}'."
