"""Static contract tests for playground dependency loading."""

from __future__ import annotations

from pathlib import Path

PLAYGROUND = Path(__file__).parents[1] / "docs" / "playground.html"


def test_playground_uses_dynamic_file_requirements_instead_of_tiers() -> None:
    source = PLAYGROUND.read_text()

    assert "const TIERS" not in source
    assert "data-tier=" not in source
    assert "const DYNAMIC_IMPORTS = true" in source
    assert "requirements_for_path" in source
    assert "findFileRequirements(code)" in source


def test_uploaded_and_sidebar_files_opt_into_dynamic_imports() -> None:
    source = PLAYGROUND.read_text()

    assert source.count("dynamic_imports=True") == 2
    assert "ready (dynamic imports)" in source
    assert "could not load required imports" in source
    assert "failed.push(name)" in source
