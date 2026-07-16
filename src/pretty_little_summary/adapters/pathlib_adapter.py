"""Adapter for pathlib Path and PurePath."""

from __future__ import annotations

from pathlib import Path, PurePath
from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import format_bytes

# Default configuration for directory scanning
DEFAULT_MAX_DEPTH = 3
DEFAULT_MAX_FILES = 100


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
                            max_files=DEFAULT_MAX_FILES
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


def _describe_directory_tree(
    root_path: Path,
    max_depth: int = DEFAULT_MAX_DEPTH,
    max_files: int = DEFAULT_MAX_FILES,
) -> dict[str, Any]:
    """
    Recursively describe a directory and its contents.

    Args:
        root_path: Root directory to describe
        max_depth: Maximum depth to traverse
        max_files: Maximum number of files to describe

    Returns:
        Dictionary with tree structure and statistics
    """
    tree_lines: list[str] = []
    file_count = 0
    dir_count = 0
    files_processed = 0

    def _walk_directory(
        path: Path,
        prefix: str = "",
        depth: int = 0,
    ) -> None:
        nonlocal file_count, dir_count, files_processed

        if depth >= max_depth:
            tree_lines.append(f"{prefix}... (max depth reached)")
            return

        if files_processed >= max_files:
            tree_lines.append(f"{prefix}... (max files reached)")
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

        for i, entry in enumerate(entries):
            if files_processed >= max_files:
                tree_lines.append(f"{prefix}... (max files reached)")
                break

            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            extension = "    " if is_last else "│   "

            try:
                if entry.is_dir():
                    dir_count += 1
                    tree_lines.append(f"{prefix}{connector}{entry.name}/")
                    _walk_directory(entry, prefix + extension, depth + 1)
                else:
                    file_count += 1
                    files_processed += 1

                    # Try to describe the file
                    description = _describe_file(entry)
                    tree_lines.append(f"{prefix}{connector}{entry.name} - {description}")

            except Exception as e:
                tree_lines.append(f"{prefix}{connector}{entry.name} - (error: {e!s})")

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


def _describe_file(file_path: Path) -> str:
    """Describe a single file using the zero-dependency sniffer tier.

    This never loads the whole file, imports a third-party parser, or executes
    file contents (e.g. it does not unpickle) — it reads only the head. That
    keeps directory scans fast and safe regardless of what is on disk.
    """
    from pretty_little_summary.sniffers import sniff_path

    try:
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
