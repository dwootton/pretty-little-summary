"""Zero-dependency file sniffers.

A *sniffer* describes a file by reading only its first bytes/rows with the
standard library — never by materializing the whole file or importing a
third-party parser. This is what lets ``pls`` point at an arbitrary file and say
something useful in a bare, zero-dependency install, and it stays fast and
deterministic on huge inputs (you never load a 2 GB CSV just to report its
shape).

Sniffers are the *resolution/extraction* layer for files. Deep, library-backed
loading (e.g. reading a Parquet file into a pandas DataFrame) is a separate,
opt-in tier layered on top — see :func:`describe_path`.
"""

from pretty_little_summary.sniffers._base import (
    HEAD_BYTES,
    Sniffer,
    SnifferRegistry,
    describe_path,
    load_all_sniffers,
    sniff_path,
)

__all__ = [
    "HEAD_BYTES",
    "Sniffer",
    "SnifferRegistry",
    "describe_path",
    "load_all_sniffers",
    "sniff_path",
]
