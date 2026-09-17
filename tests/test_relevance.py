from __future__ import annotations

from dataclasses import dataclass

import pytest

from pretty_little_summary.relevance import ColumnCard, focus_profile


def sample_meta() -> dict:
    columns = [f"noise_{index}" for index in range(29)] + ["household_income"]
    return {
        "object_type": "pandas.DataFrame",
        "shape": (100, 30),
        "columns": columns,
        "dtypes": {name: "float64" for name in columns},
        "metadata": {
            "rows": 100,
            "columns": 30,
            # Mimic today's PLS cap: detailed analysis exists only for the first 25.
            "column_analysis": [
                {"name": name, "dtype": "float64", "null_count": 0}
                for name in columns[:25]
            ],
        },
    }


def test_focus_profile_can_select_a_relevant_column_past_detailed_analysis_cap():
    focused = focus_profile(
        sample_meta(),
        "How is household income associated with educational attainment?",
        max_columns=4,
    )

    assert focused.columns[0].name == "household_income"
    assert "household_income" in focused.content
    assert focused.meta["candidate_column_count"] == 30
    assert focused.meta["selected_column_count"] == 4
    assert focused.meta["scorer"] == "lexical-v1"


@dataclass(frozen=True)
class LastColumnScorer:
    name: str = "test-last-column"

    def score(self, question: str, columns: tuple[ColumnCard, ...]) -> list[float]:
        del question
        return [float(index) for index, _ in enumerate(columns)]


def test_focus_profile_accepts_a_learned_scorer_at_one_seam_and_is_deterministic():
    first = focus_profile(sample_meta(), "question", scorer=LastColumnScorer(), max_columns=2)
    second = focus_profile(sample_meta(), "question", scorer=LastColumnScorer(), max_columns=2)

    assert first == second
    assert [column.name for column in first.columns] == ["household_income", "noise_28"]
    assert first.meta["scorer"] == "test-last-column"


def test_focus_profile_enforces_a_hard_character_budget():
    focused = focus_profile(sample_meta(), "household income", max_columns=30, max_chars=320)

    assert len(focused.content) <= 320
    assert focused.meta["truncated"] is True
    assert focused.meta["selected_column_count"] < 30


def test_focus_profile_rejects_invalid_scorer_output():
    class BrokenScorer:
        name = "broken"

        def score(self, question: str, columns: tuple[ColumnCard, ...]) -> list[float]:
            return [1.0]

    with pytest.raises(ValueError, match="one finite score per column"):
        focus_profile(sample_meta(), "question", scorer=BrokenScorer())


def test_focus_profile_exposes_optional_codebook_descriptions_to_scorers_and_output():
    class DescriptionScorer:
        name = "description-aware"

        def score(self, question: str, columns: tuple[ColumnCard, ...]) -> list[float]:
            del question
            return [float("household earnings" in (column.description or "")) for column in columns]

    focused = focus_profile(
        {
            "shape": (10, 2),
            "columns": ["x1", "x2"],
            "dtypes": {"x1": "float64", "x2": "float64"},
        },
        "Which factor predicts income?",
        scorer=DescriptionScorer(),
        column_descriptions={"x2": "Annual household earnings in USD"},
        max_columns=1,
    )

    assert focused.columns[0].name == "x2"
    assert focused.columns[0].description == "Annual household earnings in USD"
    assert "Annual household earnings in USD" in focused.content
