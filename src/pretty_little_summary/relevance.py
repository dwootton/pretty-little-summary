"""Deterministic question-focused projections of tabular PLS metadata."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any, Protocol

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "between",
        "by",
        "do",
        "does",
        "for",
        "from",
        "how",
        "in",
        "is",
        "of",
        "on",
        "or",
        "the",
        "to",
        "what",
        "which",
        "with",
    }
)


@dataclass(frozen=True)
class ColumnCard:
    """Stable facts available to relevance scorers for one column."""

    name: str
    dtype: str | None
    null_count: int | None
    stats: str | None
    cardinality: str | None
    sample_values: tuple[str, ...]
    source_index: int
    description: str | None = None
    relevance_score: float = 0.0


class ColumnScorer(Protocol):
    """One seam for deterministic lexical or learned relevance scoring."""

    name: str

    def score(self, question: str, columns: tuple[ColumnCard, ...]) -> list[float]: ...


@dataclass(frozen=True)
class FocusedProfile:
    """A bounded profile projection plus auditable selection metadata."""

    content: str
    meta: dict[str, Any]
    columns: tuple[ColumnCard, ...]


@dataclass(frozen=True)
class LexicalColumnScorer:
    """Zero-dependency deterministic baseline scorer."""

    name: str = "lexical-v1"

    def score(self, question: str, columns: tuple[ColumnCard, ...]) -> list[float]:
        question_tokens = _tokens(question)
        question_ngrams = _character_ngrams(" ".join(question_tokens))
        normalized_question = " ".join(question_tokens)
        scores: list[float] = []
        for column in columns:
            name_tokens = _tokens(column.name)
            if not name_tokens:
                scores.append(0.0)
                continue
            overlap = len(set(name_tokens) & set(question_tokens)) / len(set(name_tokens))
            phrase = float(" ".join(name_tokens) in normalized_question)
            name_ngrams = _character_ngrams(" ".join(name_tokens))
            union = question_ngrams | name_ngrams
            character_similarity = len(question_ngrams & name_ngrams) / len(union) if union else 0.0
            scores.append(phrase + 0.75 * overlap + 0.25 * character_similarity)
        return scores


def focus_profile(
    description_or_meta: Any,
    question: str,
    *,
    scorer: ColumnScorer | None = None,
    column_descriptions: Mapping[str, str] | None = None,
    max_columns: int = 8,
    max_chars: int = 8_000,
) -> FocusedProfile:
    """Rank every tabular column and render a deterministic bounded projection."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string")
    if max_columns < 1:
        raise ValueError("max_columns must be positive")
    if max_chars < 128:
        raise ValueError("max_chars must be at least 128")

    meta = _coerce_meta(description_or_meta)
    candidates = _column_cards(meta, column_descriptions or {})
    active_scorer = scorer or LexicalColumnScorer()
    raw_scores = active_scorer.score(question, candidates)
    if len(raw_scores) != len(candidates) or any(
        not isinstance(score, (int, float)) or not math.isfinite(float(score))
        for score in raw_scores
    ):
        raise ValueError("scorer must return one finite score per column")

    ranked = tuple(
        sorted(
            (
                replace(column, relevance_score=round(float(score), 8))
                for column, score in zip(candidates, raw_scores, strict=True)
            ),
            key=lambda column: (-column.relevance_score, column.source_index, column.name),
        )
    )
    content, selected = _render(meta, question, ranked[:max_columns], max_chars)
    return FocusedProfile(
        content=content,
        columns=selected,
        meta={
            "profile_kind": "question-focused-tabular",
            "scorer": active_scorer.name,
            "candidate_column_count": len(candidates),
            "selected_column_count": len(selected),
            "max_columns": max_columns,
            "max_chars": max_chars,
            "truncated": len(selected) < min(max_columns, len(candidates)),
            "selected": [
                {"name": column.name, "score": column.relevance_score}
                for column in selected
            ],
        },
    )


def _coerce_meta(value: Any) -> dict[str, Any]:
    meta = getattr(value, "meta", value)
    if not isinstance(meta, dict):
        raise TypeError("description_or_meta must be a Description or metadata dictionary")
    return meta


def _column_cards(
    meta: dict[str, Any], column_descriptions: Mapping[str, str]
) -> tuple[ColumnCard, ...]:
    raw_columns = meta.get("columns") or []
    if not isinstance(raw_columns, (list, tuple)):
        raise ValueError("metadata does not contain a tabular columns list")
    raw_dtypes = meta.get("dtypes")
    dtypes: dict[Any, Any] = raw_dtypes if isinstance(raw_dtypes, dict) else {}
    raw_metadata = meta.get("metadata")
    metadata: dict[str, Any] = raw_metadata if isinstance(raw_metadata, dict) else {}
    analysis = metadata.get("column_analysis") if isinstance(metadata, dict) else []
    analysis_by_name: dict[str, dict[str, Any]] = {
        str(item.get("name")): item
        for item in analysis or []
        if isinstance(item, dict) and item.get("name") is not None
    }
    cards: list[ColumnCard] = []
    for index, raw_name in enumerate(raw_columns):
        name = str(raw_name)
        details = analysis_by_name.get(name, {})
        samples = details.get("sample_values") or []
        cards.append(
            ColumnCard(
                name=name,
                dtype=str(dtypes.get(raw_name) or details.get("dtype"))
                if dtypes.get(raw_name) is not None or details.get("dtype") is not None
                else None,
                null_count=details.get("null_count") if isinstance(details.get("null_count"), int) else None,
                stats=str(details["stats"]) if details.get("stats") is not None else None,
                cardinality=str(details["cardinality"])
                if details.get("cardinality") is not None
                else None,
                sample_values=tuple(str(value) for value in samples[:3]),
                source_index=index,
                description=str(column_descriptions[name])[:500]
                if name in column_descriptions
                else None,
            )
        )
    return tuple(cards)


def _render(
    meta: dict[str, Any],
    question: str,
    ranked: tuple[ColumnCard, ...],
    max_chars: int,
) -> tuple[str, tuple[ColumnCard, ...]]:
    shape = meta.get("shape")
    question_line = " ".join(question.split())
    header = f"Question-focused tabular profile | shape={shape}\nQuestion: {question_line}\n"
    if len(header) > max_chars:
        allowance = max(1, max_chars - len("Question-focused tabular profile\nQuestion: …"))
        header = f"Question-focused tabular profile\nQuestion: {question_line[:allowance]}…"
    chunks = [header.rstrip()]
    selected: list[ColumnCard] = []
    for column in ranked:
        line = _column_line(column)
        candidate = "\n".join([*chunks, line])
        if len(candidate) > max_chars:
            continue
        chunks.append(line)
        selected.append(column)
    return "\n".join(chunks), tuple(selected)


def _column_line(column: ColumnCard) -> str:
    details = [f"score={column.relevance_score:.4f}"]
    if column.dtype:
        details.append(f"dtype={column.dtype}")
    if column.description:
        details.append(f"description={column.description}")
    if column.null_count is not None:
        details.append(f"nulls={column.null_count}")
    if column.stats:
        details.append(f"stats={column.stats}")
    elif column.cardinality:
        details.append(f"cardinality={column.cardinality}")
    if column.sample_values:
        details.append(f"sample=[{', '.join(column.sample_values)}]")
    return f"- {column.name}: " + "; ".join(details)


def _tokens(value: str) -> tuple[str, ...]:
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value).replace("_", "-")
    return tuple(token for token in _TOKEN_RE.findall(expanded.lower()) if token not in _STOPWORDS)


def _character_ngrams(value: str, width: int = 3) -> set[str]:
    padded = f"  {value}  "
    return {padded[index : index + width] for index in range(max(0, len(padded) - width + 1))}
