"""Tests for the zero-dependency file sniffer tier."""

from __future__ import annotations

import json
import sqlite3
import struct
import tarfile
import wave
import zipfile
from pathlib import Path

import pytest

from pretty_little_summary.sniffers import describe_path, sniff_path


def _png_bytes(width: int, height: int) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + b"\x00\x00\x00\rIHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x02\x00\x00\x00"
    )


def _gif_bytes(width: int, height: int) -> bytes:
    return b"GIF89a" + struct.pack("<HH", width, height) + b"\x00" * 4


def _bmp_bytes(width: int, height: int) -> bytes:
    header = b"BM" + b"\x00" * 16
    return header + struct.pack("<ii", width, height) + b"\x00" * 4


def test_png_dimensions(tmp_path: Path) -> None:
    p = tmp_path / "img.png"
    p.write_bytes(_png_bytes(320, 240))
    meta = sniff_path(p)
    assert meta["adapter_used"] == "PngSniffer"
    assert meta["metadata"]["width"] == 320
    assert meta["metadata"]["height"] == 240
    assert "320x240" in meta["nl_summary"]


def test_gif_dimensions(tmp_path: Path) -> None:
    p = tmp_path / "img.gif"
    p.write_bytes(_gif_bytes(16, 32))
    meta = sniff_path(p)
    assert meta["adapter_used"] == "GifSniffer"
    assert (meta["metadata"]["width"], meta["metadata"]["height"]) == (16, 32)


def test_bmp_dimensions(tmp_path: Path) -> None:
    p = tmp_path / "img.bmp"
    p.write_bytes(_bmp_bytes(100, 50))
    meta = sniff_path(p)
    assert meta["adapter_used"] == "BmpSniffer"
    assert (meta["metadata"]["width"], meta["metadata"]["height"]) == (100, 50)


def test_npy_header_without_numpy_import(tmp_path: Path) -> None:
    np = pytest.importorskip("numpy")
    p = tmp_path / "arr.npy"
    np.save(p, np.zeros((4, 3), dtype=np.float32))
    meta = sniff_path(p)
    assert meta["adapter_used"] == "NpySniffer"
    assert meta["metadata"]["shape"] == [4, 3]
    assert "f4" in meta["metadata"]["dtype"]


def test_sqlite_schema(tmp_path: Path) -> None:
    p = tmp_path / "db.sqlite"
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE users(id INTEGER, name TEXT)")
    con.execute("INSERT INTO users VALUES (1, 'a')")
    con.execute("INSERT INTO users VALUES (2, 'b')")
    con.commit()
    con.close()
    meta = sniff_path(p)
    assert meta["adapter_used"] == "SqliteSniffer"
    tables = meta["metadata"]["tables"]
    assert tables[0]["name"] == "users"
    assert tables[0]["columns"] == ["id", "name"]
    assert tables[0]["rows"] == 2


def test_sqlite_read_only_does_not_modify(tmp_path: Path) -> None:
    p = tmp_path / "db.sqlite"
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE t(x)")
    con.commit()
    con.close()
    before = p.stat().st_mtime_ns
    sniff_path(p)
    assert p.stat().st_mtime_ns == before


def test_zip_listing(tmp_path: Path) -> None:
    p = tmp_path / "a.zip"
    with zipfile.ZipFile(p, "w") as zf:
        zf.writestr("one.txt", "x")
        zf.writestr("two.txt", "y")
    meta = sniff_path(p)
    assert meta["adapter_used"] == "ZipSniffer"
    assert meta["metadata"]["entry_count"] == 2


def test_tar_listing(tmp_path: Path) -> None:
    member = tmp_path / "one.txt"
    member.write_text("hello")
    p = tmp_path / "a.tar"
    with tarfile.open(p, "w") as tf:
        tf.add(member, arcname="one.txt")
    meta = sniff_path(p)
    assert meta["adapter_used"] == "TarSniffer"
    assert meta["metadata"]["entry_count"] == 1
    assert meta["metadata"]["entries"] == ["one.txt"]
    assert "1 entry" in meta["nl_summary"]


def test_wav_metadata(tmp_path: Path) -> None:
    p = tmp_path / "sound.wav"
    framerate = 8000
    nframes = 4000  # 0.5 seconds
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(framerate)
        w.writeframes(b"\x00\x00" * nframes)
    meta = sniff_path(p)
    assert meta["adapter_used"] == "WavSniffer"
    assert meta["metadata"]["format"] == "WAV"
    assert meta["metadata"]["channels"] == 1
    assert meta["metadata"]["framerate"] == framerate
    assert meta["metadata"]["frame_count"] == nframes
    assert abs(meta["metadata"]["duration_seconds"] - 0.5) < 1e-6
    assert "0.5s" in meta["nl_summary"]
    assert "8000 Hz" in meta["nl_summary"]


def test_toml_file(tmp_path: Path) -> None:
    p = tmp_path / "config.toml"
    p.write_text('title = "demo"\n\n[server]\nhost = "localhost"\nport = 8080\n')
    meta = sniff_path(p)
    assert meta["adapter_used"] == "TomlSniffer"
    assert meta["metadata"]["format"] == "toml"
    # tomllib is stdlib on 3.11+; guard only the key extraction assertion.
    pytest.importorskip("tomllib")
    assert meta["metadata"]["keys"] == ["title", "server"]
    assert "title" in meta["nl_summary"]
    assert "server" in meta["nl_summary"]


def test_parquet_identify_only(tmp_path: Path) -> None:
    p = tmp_path / "data.parquet"
    p.write_bytes(b"PAR1" + b"\x00" * 32 + b"PAR1")
    meta = sniff_path(p)
    assert meta["adapter_used"] == "ParquetSniffer"
    assert meta["metadata"]["format"] == "Parquet"


def test_pickle_is_not_executed(tmp_path: Path) -> None:
    import pickle

    p = tmp_path / "obj.pkl"
    p.write_bytes(pickle.dumps({"a": [1, 2, 3]}))
    meta = sniff_path(p)
    assert meta["adapter_used"] == "PickleSniffer"
    # Protocol byte read; contents deliberately NOT unpickled.
    assert "protocol" in meta["metadata"]


def test_json_file(tmp_path: Path) -> None:
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"name": "x", "age": 3}))
    meta = sniff_path(p)
    assert meta["metadata"]["format"] == "json"
    assert meta["metadata"]["keys"] == ["name", "age"]


def test_jsonl_file(tmp_path: Path) -> None:
    p = tmp_path / "d.jsonl"
    p.write_text('{"a": 1}\n{"a": 2}\n{"a": 3}\n')
    meta = sniff_path(p)
    assert meta["metadata"]["format"] == "jsonl"


def test_csv_file(tmp_path: Path) -> None:
    p = tmp_path / "d.csv"
    p.write_text("name,age,city\nalice,30,nyc\nbob,25,la\n")
    meta = sniff_path(p)
    assert meta["metadata"]["format"] == "csv"
    assert meta["metadata"]["columns"] == 3


def test_plain_text_not_misdetected_as_csv(tmp_path: Path) -> None:
    p = tmp_path / "notes.txt"
    p.write_text("hello world\nthis is prose\nnothing structured here\n")
    meta = sniff_path(p)
    assert meta["adapter_used"] == "PlainTextSniffer"
    assert meta["metadata"]["format"] == "text"


def test_unknown_binary_gets_catchall_description(tmp_path: Path) -> None:
    # Random binary with no known magic and null bytes -> not text, no magic.
    p = tmp_path / "blob.bin"
    p.write_bytes(bytes(range(256)) * 4)
    meta = sniff_path(p)
    # Any readable file always gets a description via the catch-all sniffer.
    assert meta is not None
    assert meta["adapter_used"] == "UnknownBinarySniffer"
    assert meta["metadata"]["format"] == "binary"


def test_missing_file_returns_none() -> None:
    assert sniff_path(Path("/nonexistent/does/not/exist.xyz")) is None


# --- invariants across all sniffed files ------------------------------------- #


def _all_fixtures(tmp_path: Path) -> list[Path]:
    (tmp_path / "img.png").write_bytes(_png_bytes(8, 8))
    (tmp_path / "d.json").write_text('{"k": 1}')
    (tmp_path / "d.csv").write_text("a,b\n1,2\n")
    (tmp_path / "notes.txt").write_text("just text\n")
    with zipfile.ZipFile(tmp_path / "a.zip", "w") as zf:
        zf.writestr("f", "x")
    return sorted(tmp_path.iterdir())


@pytest.mark.parametrize("make_index", range(5))
def test_sniff_results_are_json_serializable_and_bounded(
    tmp_path: Path, make_index: int
) -> None:
    fixtures = _all_fixtures(tmp_path)
    meta = sniff_path(fixtures[make_index])
    json.dumps(meta)  # must be serializable
    assert len(meta["nl_summary"]) <= 50_000


def test_sniff_is_deterministic(tmp_path: Path) -> None:
    p = tmp_path / "d.csv"
    p.write_text("a,b,c\n1,2,3\n4,5,6\n")
    first = sniff_path(p)
    second = sniff_path(p)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_describe_path_deep_falls_back_to_sniff_when_no_library(tmp_path: Path) -> None:
    # describe_path(deep=True) must still return a valid result even if deep
    # loading is unavailable/fails.
    p = tmp_path / "d.csv"
    p.write_text("a,b\n1,2\n")
    meta = describe_path(p, deep=True)
    assert meta["object_type"]
    assert meta["adapter_used"]
