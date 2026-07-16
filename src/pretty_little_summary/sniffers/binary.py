"""Binary file sniffers: identify by magic bytes, extract with the stdlib.

Every extractor here is zero-dependency. Where a format has a documented,
stable header (PNG/GIF/BMP dimensions, the NumPy ``.npy`` header, SQLite) we
read real structure; where deep reading would require the format's library
(Parquet, HDF5) we identify the file and report its size without pretending to
parse it.
"""

from __future__ import annotations

import ast
import struct
from pathlib import Path
from typing import Any

from pretty_little_summary.core import MetaDescription
from pretty_little_summary.descriptor_utils import format_bytes
from pretty_little_summary.sniffers._base import PRIORITY_MAGIC, SnifferRegistry

# Below the text fallback (0): the unknown-binary catch-all only wins when a
# file is neither a known format nor decodable text.
PRIORITY_BINARY_FALLBACK = -100


def _file_size(path: Path) -> int | None:
    try:
        return path.stat().st_size
    except OSError:
        return None


def _base_meta(path: Path, sniffer_name: str, object_type: str) -> MetaDescription:
    size = _file_size(path)
    meta: MetaDescription = {
        "object_type": object_type,
        "adapter_used": sniffer_name,
    }
    metadata: dict[str, Any] = {"path": str(path), "name": path.name}
    if size is not None:
        metadata["size_bytes"] = size
        metadata["size"] = format_bytes(size)
    meta["metadata"] = metadata
    return meta


def _register(cls: type) -> type:
    SnifferRegistry.register(cls, priority=PRIORITY_MAGIC)
    return cls


# --------------------------------------------------------------------------- #
# Images                                                                       #
# --------------------------------------------------------------------------- #


@_register
class PngSniffer:
    name = "PngSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        return head[:8] == b"\x89PNG\r\n\x1a\n"

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "PngSniffer", "image/png")
        md = meta["metadata"]
        md["format"] = "PNG"
        # IHDR is the first chunk: width/height are big-endian uint32 at offset 16.
        if len(head) >= 24:
            width, height = struct.unpack(">II", head[16:24])
            md["width"], md["height"] = width, height
        meta["nl_summary"] = _image_summary(md)
        return meta


@_register
class GifSniffer:
    name = "GifSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        return head[:6] in (b"GIF87a", b"GIF89a")

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "GifSniffer", "image/gif")
        md = meta["metadata"]
        md["format"] = "GIF"
        if len(head) >= 10:
            width, height = struct.unpack("<HH", head[6:10])  # little-endian
            md["width"], md["height"] = width, height
        meta["nl_summary"] = _image_summary(md)
        return meta


@_register
class BmpSniffer:
    name = "BmpSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        return head[:2] == b"BM"

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "BmpSniffer", "image/bmp")
        md = meta["metadata"]
        md["format"] = "BMP"
        # BITMAPINFOHEADER: signed int32 width/height at offset 18.
        if len(head) >= 26:
            width, height = struct.unpack("<ii", head[18:26])
            md["width"], md["height"] = width, abs(height)
        meta["nl_summary"] = _image_summary(md)
        return meta


@_register
class JpegSniffer:
    name = "JpegSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        return head[:3] == b"\xff\xd8\xff"

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "JpegSniffer", "image/jpeg")
        md = meta["metadata"]
        md["format"] = "JPEG"
        dims = _jpeg_dimensions(head)
        if dims:
            md["width"], md["height"] = dims
        meta["nl_summary"] = _image_summary(md)
        return meta


def _jpeg_dimensions(data: bytes) -> tuple[int, int] | None:
    """Scan JPEG segments for a Start-Of-Frame marker carrying dimensions."""
    i = 2  # skip the SOI marker
    n = len(data)
    while i + 9 < n:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        # SOF0..SOF15 hold frame dimensions (excluding non-frame markers).
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack(">HH", data[i + 5 : i + 9])
            return width, height
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        seg_len = struct.unpack(">H", data[i + 2 : i + 4])[0]
        i += 2 + seg_len
    return None


def _image_summary(md: dict[str, Any]) -> str:
    fmt = md.get("format", "image")
    if "width" in md and "height" in md:
        return f"A {fmt} image, {md['width']}x{md['height']} pixels ({md.get('size', 'unknown size')})."
    return f"A {fmt} image ({md.get('size', 'unknown size')})."


# --------------------------------------------------------------------------- #
# NumPy .npy (documented, library-free header)                                 #
# --------------------------------------------------------------------------- #


@_register
class NpySniffer:
    name = "NpySniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        return head[:6] == b"\x93NUMPY"

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "NpySniffer", "numpy.ndarray")
        md = meta["metadata"]
        md["format"] = "npy"
        header = _parse_npy_header(head)
        if header:
            md.update(header)
        shape = md.get("shape")
        dtype = md.get("dtype")
        if shape is not None and dtype is not None:
            meta["nl_summary"] = (
                f"A NumPy .npy array with shape {tuple(shape)} and dtype {dtype} "
                f"({md.get('size', 'unknown size')})."
            )
        else:
            meta["nl_summary"] = f"A NumPy .npy file ({md.get('size', 'unknown size')})."
        return meta


def _parse_npy_header(head: bytes) -> dict[str, Any] | None:
    """Parse the .npy header dict without importing numpy.

    Format: magic (6) + version (2) + header-len + a Python-literal dict string
    with keys ``descr``, ``fortran_order``, ``shape``.
    """
    if len(head) < 10:
        return None
    major = head[6]
    if major == 1:
        hlen = struct.unpack("<H", head[8:10])[0]
        start = 10
    else:
        hlen = struct.unpack("<I", head[8:12])[0]
        start = 12
    raw = head[start : start + hlen]
    try:
        info = ast.literal_eval(raw.decode("latin-1").strip())
    except (ValueError, SyntaxError):
        return None
    if not isinstance(info, dict):
        return None
    return {
        "dtype": info.get("descr"),
        "shape": list(info.get("shape", ())),
        "fortran_order": info.get("fortran_order"),
    }


# --------------------------------------------------------------------------- #
# SQLite (stdlib sqlite3 reads real schema)                                    #
# --------------------------------------------------------------------------- #


@_register
class SqliteSniffer:
    name = "SqliteSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        return head[:16] == b"SQLite format 3\x00"

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "SqliteSniffer", "sqlite3.database")
        md = meta["metadata"]
        md["format"] = "SQLite"
        tables = _sqlite_tables(path)
        if tables is not None:
            md["tables"] = tables
            md["table_count"] = len(tables)
            names = ", ".join(t["name"] for t in tables[:6])
            more = "" if len(tables) <= 6 else f", and {len(tables) - 6} more"
            meta["nl_summary"] = (
                f"A SQLite database with {len(tables)} "
                f"{'table' if len(tables) == 1 else 'tables'}"
                f"{': ' + names + more if names else ''} ({md.get('size', 'unknown size')})."
            )
        else:
            meta["nl_summary"] = f"A SQLite database ({md.get('size', 'unknown size')})."
        return meta


def _sqlite_tables(path: Path) -> list[dict[str, Any]] | None:
    import sqlite3

    try:
        # Read-only URI connection so we never modify the file being described.
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        table_names = [row[0] for row in cur.fetchall()]
        tables: list[dict[str, Any]] = []
        for name in table_names:
            cols = [r[1] for r in cur.execute(f'PRAGMA table_info("{name}")').fetchall()]
            row_count = cur.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            tables.append({"name": name, "columns": cols, "rows": row_count})
        return tables
    except sqlite3.Error:
        return None
    finally:
        con.close()


# --------------------------------------------------------------------------- #
# Archives (stdlib listing)                                                    #
# --------------------------------------------------------------------------- #


@_register
class ZipSniffer:
    name = "ZipSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        # PK\x03\x04 (local file), PK\x05\x06 (empty archive).
        return head[:4] in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "ZipSniffer", "zip.archive")
        md = meta["metadata"]
        md["format"] = "ZIP"
        import zipfile

        try:
            with zipfile.ZipFile(path) as zf:
                names = zf.namelist()
            md["entry_count"] = len(names)
            md["entries"] = names[:10]
        except (zipfile.BadZipFile, OSError):
            pass
        count = md.get("entry_count")
        if count is not None:
            entry_word = "entry" if count == 1 else "entries"
            meta["nl_summary"] = (
                f"A ZIP archive with {count} {entry_word} ({md.get('size', 'unknown size')})."
            )
        else:
            meta["nl_summary"] = f"A ZIP archive ({md.get('size', 'unknown size')})."
        return meta


@_register
class TarSniffer:
    name = "TarSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        # The ustar magic lives at offset 257 in the first (512-byte) header
        # block. Gzip-compressed tars (.tar.gz) carry gzip magic instead and are
        # claimed by GzipSniffer, so we only match uncompressed tar here.
        return len(head) >= 262 and head[257:262] == b"ustar"

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "TarSniffer", "tar.archive")
        md = meta["metadata"]
        md["format"] = "TAR"
        import tarfile

        try:
            with tarfile.open(path) as tf:
                names = tf.getnames()
            md["entry_count"] = len(names)
            md["entries"] = names[:10]
        except (tarfile.TarError, OSError):
            pass
        count = md.get("entry_count")
        if count is not None:
            entry_word = "entry" if count == 1 else "entries"
            meta["nl_summary"] = (
                f"A TAR archive with {count} {entry_word} ({md.get('size', 'unknown size')})."
            )
        else:
            meta["nl_summary"] = f"A TAR archive ({md.get('size', 'unknown size')})."
        return meta


# --------------------------------------------------------------------------- #
# Audio (stdlib wave reads real header)                                        #
# --------------------------------------------------------------------------- #


@_register
class WavSniffer:
    name = "WavSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        # RIFF container tagged WAVE; bytes 4-8 hold the chunk size we ignore.
        return len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WAVE"

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "WavSniffer", "audio/wav")
        md = meta["metadata"]
        md["format"] = "WAV"
        info = _wav_info(path)
        if info is not None:
            md.update(info)
            meta["nl_summary"] = (
                f"A WAV audio file, {info['duration_seconds']:.1f}s, "
                f"{info['channels']} channel(s), {info['framerate']} Hz "
                f"({md.get('size', 'unknown size')})."
            )
        else:
            meta["nl_summary"] = f"A WAV audio file ({md.get('size', 'unknown size')})."
        return meta


def _wav_info(path: Path) -> dict[str, Any] | None:
    """Read WAV header fields via the stdlib; None on any malformed input."""
    import wave

    wav = None
    try:
        wav = wave.open(str(path), "rb")
        channels = wav.getnchannels()
        framerate = wav.getframerate()
        sampwidth = wav.getsampwidth()
        nframes = wav.getnframes()
    except (wave.Error, OSError, EOFError):
        return None
    finally:
        # Always release the file handle, even on a partial read.
        if wav is not None:
            wav.close()
    duration = nframes / framerate if framerate else 0.0
    return {
        "channels": channels,
        "framerate": framerate,
        "sample_width_bytes": sampwidth,
        "frame_count": nframes,
        "duration_seconds": duration,
    }


@_register
class GzipSniffer:
    name = "GzipSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        return head[:2] == b"\x1f\x8b"

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "GzipSniffer", "gzip.archive")
        md = meta["metadata"]
        md["format"] = "gzip"
        meta["nl_summary"] = f"A gzip-compressed file ({md.get('size', 'unknown size')})."
        return meta


# --------------------------------------------------------------------------- #
# Identify-only: format has magic but deep read needs its own library          #
# --------------------------------------------------------------------------- #


@_register
class ParquetSniffer:
    name = "ParquetSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        return head[:4] == b"PAR1"

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "ParquetSniffer", "parquet.file")
        md = meta["metadata"]
        md["format"] = "Parquet"
        meta["nl_summary"] = (
            f"An Apache Parquet file ({md.get('size', 'unknown size')}). "
            "Install pyarrow/pandas and use deep mode to read its schema."
        )
        return meta


@_register
class Hdf5Sniffer:
    name = "Hdf5Sniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        return head[:8] == b"\x89HDF\r\n\x1a\n"

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "Hdf5Sniffer", "hdf5.file")
        md = meta["metadata"]
        md["format"] = "HDF5"
        meta["nl_summary"] = (
            f"An HDF5 file ({md.get('size', 'unknown size')}). "
            "Install h5py and use deep mode to read its datasets."
        )
        return meta


@_register
class PdfSniffer:
    name = "PdfSniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        return head[:5] == b"%PDF-"

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "PdfSniffer", "pdf.document")
        md = meta["metadata"]
        md["format"] = "PDF"
        try:
            md["pdf_version"] = head[5:8].decode("ascii")
        except (UnicodeDecodeError, IndexError):
            pass
        version = md.get("pdf_version")
        meta["nl_summary"] = (
            f"A PDF document{f' (v{version})' if version else ''} "
            f"({md.get('size', 'unknown size')})."
        )
        return meta


@_register
class PickleSniffer:
    name = "PickleSniffer"

    # Common pickle protocol openers: PROTO (0x80) for v2+, or classic opcodes.
    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        if path.suffix.lower() not in {".pkl", ".pickle"}:
            return False
        return bool(head) and head[:1] in (b"\x80", b"(", b"]", b"}", b"c")

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "PickleSniffer", "pickle.file")
        md = meta["metadata"]
        md["format"] = "pickle"
        # NEVER unpickle untrusted data (arbitrary code execution). Read the
        # protocol byte and, safely, the referenced global names via pickletools.
        if head[:1] == b"\x80" and len(head) >= 2:
            md["protocol"] = head[1]
        md["referenced_globals"] = _pickle_globals(head)
        meta["nl_summary"] = (
            f"A Python pickle file ({md.get('size', 'unknown size')}). "
            "Contents are not unpickled by default for safety."
        )
        return meta


class UnknownBinarySniffer:
    """Catch-all so any readable file gets *some* description.

    Registered below every other sniffer, so it only wins when a file matches no
    known magic and is not decodable text. Reports size and the leading bytes as
    hex — deterministic and never raises.
    """

    name = "UnknownBinarySniffer"

    @staticmethod
    def can_sniff(path: Path, head: bytes) -> bool:
        return True

    @staticmethod
    def sniff(path: Path, head: bytes) -> MetaDescription:
        meta = _base_meta(path, "UnknownBinarySniffer", "application/octet-stream")
        md = meta["metadata"]
        md["format"] = "binary"
        md["magic_hex"] = head[:8].hex()
        meta["nl_summary"] = (
            f"A binary file of unknown type ({md.get('size', 'unknown size')}, "
            f"starts with 0x{md['magic_hex']})."
        )
        return meta


SnifferRegistry.register(UnknownBinarySniffer, priority=PRIORITY_BINARY_FALLBACK)


def _pickle_globals(head: bytes) -> list[str]:
    """Extract referenced global/class names without executing the pickle."""
    import pickletools

    names: list[str] = []
    try:
        for opcode, arg, _pos in pickletools.genops(head):
            if opcode.name in ("GLOBAL", "STACK_GLOBAL", "INST") and arg:
                name = arg if isinstance(arg, str) else " ".join(map(str, arg))
                if name not in names:
                    names.append(name)
            if len(names) >= 10:
                break
    except Exception:
        # Truncated head or unknown opcode: return whatever we gathered.
        pass
    return names
