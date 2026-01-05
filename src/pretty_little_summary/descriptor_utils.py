"""Utilities and shared structures for describing Python objects."""

from __future__ import annotations

import math
import random
import re
import statistics
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Iterator, Protocol, Sequence, TypeVar

T = TypeVar("T")

# Ensure deterministic sampling across runs.
random.seed(0)


# =============================================================================
# CONFIGURATION
# =============================================================================


@dataclass
class RedactionConfig:
    """Configuration for redacting sensitive information."""

    enabled: bool = False
    redact_emails: bool = True
    redact_api_keys: bool = True
    redact_passwords: bool = True
    redact_pii: bool = True
    redact_ip_addresses: bool = False
    hash_identifiers: bool = False
    field_name_patterns: list[str] = field(
        default_factory=lambda: [
            r"password",
            r"secret",
            r"token",
            r"api_key",
            r"apikey",
            r"credential",
            r"auth",
            r"private",
        ]
    )
    custom_patterns: list[re.Pattern] = field(default_factory=list)


@dataclass
class DescribeConfig:
    """Configuration for descriptor generation."""

    sample_size: int = 5
    max_depth: int = 3
    max_string_preview: int = 100
    max_sample_repr: int = 50
    max_sample_elements: int = 1000
    max_sample_cells: int = 2000
    max_sample_rows: int = 10
    allow_iterator_consumption: bool = False
    include_affordances: bool = True
    include_suggested_views: bool = True
    redact: RedactionConfig = field(default_factory=RedactionConfig)
    verbosity: str = "full"  # "full", "compact", "minimal"


# =============================================================================
# OUTPUT STRUCTURES
# =============================================================================


@dataclass
class NLDescriptor:
    """Natural language descriptor output."""

    what: str
    content: str
    stats: str | None
    affordances: str
    suggested_view: str
    type_name: str
    redacted: bool = False
    warnings: list[str] = field(default_factory=list)

    def to_prose(self) -> str:
        parts = [self.what]
        if self.content:
            parts.append(self.content)
        if self.stats:
            parts.append(self.stats)
        if self.affordances:
            parts.append(self.affordances)
        if self.suggested_view:
            parts.append(self.suggested_view)
        return " ".join(parts)

    def to_compact(self) -> str:
        return f"{self.what} {self.suggested_view}".strip()

    def to_minimal(self) -> str:
        return self.what


# =============================================================================
# SAMPLING UTILITIES
# =============================================================================


def safe_sample(
    iterable: Any, n: int = 5, strategy: str = "head"
) -> tuple[list[Any], int, bool]:
    """
    Safely sample from any iterable.

    Returns: (samples, total_length, was_truncated)
    """
    if hasattr(iterable, "__len__"):
        length = len(iterable)
        truncated = length > n

        if strategy == "head":
            if hasattr(iterable, "__getitem__"):
                samples = list(iterable[:n])
            else:
                samples = list(_take(iterable, n))
        elif strategy == "head_tail" and hasattr(iterable, "__getitem__"):
            half = n // 2
            if length <= n:
                samples = list(iterable)
            else:
                samples = list(iterable[:half]) + list(iterable[-half:])
        else:
            samples = list(_take(iterable, n))

        return samples, length, truncated

    samples = list(_take(iterable, n + 1))
    truncated = len(samples) > n
    if truncated:
        samples = samples[:n]
    return samples, -1, truncated


def _take(iterable: Iterator[T], n: int) -> Iterator[T]:
    """Take first n items from iterator."""
    for i, item in enumerate(iterable):
        if i >= n:
            break
        yield item


def safe_repr(obj: Any, max_len: int = 50) -> str:
    """Safe repr with length limit."""
    try:
        r = repr(obj)
        if len(r) > max_len:
            return r[: max_len - 3] + "..."
        return r
    except Exception:
        return f"<{type(obj).__name__}>"


def safe_str(obj: Any, max_len: int = 100) -> str:
    """Safe str with length limit."""
    try:
        s = str(obj)
        if len(s) > max_len:
            return s[: max_len - 3] + "..."
        return s
    except Exception:
        return f"<{type(obj).__name__}>"


# =============================================================================
# NUMERIC STATISTICS
# =============================================================================


@dataclass
class NumericStats:
    """Statistics for numeric data."""

    min: float
    max: float
    mean: float
    std: float | None
    median: float | None
    q1: float | None = None
    q3: float | None = None
    n_zeros: int = 0
    n_nan: int = 0
    n_inf: int = 0
    total: int = 0

    def to_prose(self, precision: int = 2) -> str:
        parts = [f"range {self.min:.{precision}g} to {self.max:.{precision}g}"]
        parts.append(f"mean {self.mean:.{precision}g}")
        if self.std is not None:
            parts.append(f"std {self.std:.{precision}g}")

        extras = []
        if self.n_nan > 0:
            pct = 100 * self.n_nan / max(self.total, 1)
            extras.append(f"{pct:.1f}% NaN")
        if self.n_inf > 0:
            extras.append(f"{self.n_inf} infinite values")
        if self.n_zeros > self.total * 0.5:
            pct = 100 * self.n_zeros / max(self.total, 1)
            extras.append(f"{pct:.0f}% zeros")

        result = ", ".join(parts)
        if extras:
            result += f" ({', '.join(extras)})"
        return result


def compute_numeric_stats(
    values: Sequence[float | int], sample_limit: int = 10000
) -> NumericStats | None:
    """Compute statistics for numeric sequence."""
    if values is None or len(values) == 0:
        return None

    if len(values) > sample_limit:
        import random

        values = random.sample(list(values), sample_limit)

    finite_vals = []
    n_nan = 0
    n_inf = 0
    n_zeros = 0

    for v in values:
        try:
            if math.isnan(v):
                n_nan += 1
                continue
            if math.isinf(v):
                n_inf += 1
                continue
        except (TypeError, ValueError):
            pass

        try:
            v_float = float(v)
        except (TypeError, ValueError):
            continue

        finite_vals.append(v_float)
        if v_float == 0:
            n_zeros += 1

    if not finite_vals:
        return None

    sorted_vals = sorted(finite_vals)
    n = len(sorted_vals)

    return NumericStats(
        min=sorted_vals[0],
        max=sorted_vals[-1],
        mean=statistics.mean(finite_vals),
        std=statistics.stdev(finite_vals) if n > 1 else None,
        median=statistics.median(finite_vals),
        q1=sorted_vals[n // 4] if n >= 4 else None,
        q3=sorted_vals[3 * n // 4] if n >= 4 else None,
        n_zeros=n_zeros,
        n_nan=n_nan,
        n_inf=n_inf,
        total=len(values),
    )


# =============================================================================
# CARDINALITY ANALYSIS
# =============================================================================


@dataclass
class CardinalityInfo:
    """Information about unique values."""

    unique_count: int
    total_count: int
    ratio: float
    is_categorical: bool
    is_id_like: bool
    is_constant: bool
    top_values: list[tuple[Any, int]] | None

    def to_prose(self) -> str:
        if self.is_constant:
            return "constant (single value)"
        if self.is_id_like:
            return f"{self.unique_count} unique values (likely identifiers)"
        if self.is_categorical:
            if self.top_values:
                top_str = ", ".join(f"'{v}'" for v, _ in self.top_values[:3])
                return f"{self.unique_count} categories including {top_str}"
            return f"{self.unique_count} categories"
        return f"{self.unique_count} unique values out of {self.total_count}"


def compute_cardinality(
    values: Sequence[Any], sample_limit: int = 10000
) -> CardinalityInfo:
    """Analyze cardinality of a sequence."""
    if values is None or len(values) == 0:
        return CardinalityInfo(0, 0, 0, False, False, True, None)

    total = len(values)

    if total > sample_limit:
        import random

        sample = random.sample(list(values), sample_limit)
    else:
        sample = list(values)

    counter = Counter(sample)
    unique = len(counter)
    ratio = unique / max(len(sample), 1)

    is_constant = unique == 1
    is_categorical = unique <= 20 or (unique <= 50 and ratio < 0.05)
    is_id_like = ratio > 0.95 and unique > 10

    top_values = counter.most_common(5) if is_categorical else None

    return CardinalityInfo(
        unique_count=unique,
        total_count=total,
        ratio=ratio,
        is_categorical=is_categorical,
        is_id_like=is_id_like,
        is_constant=is_constant,
        top_values=top_values,
    )


# =============================================================================
# PATTERN DETECTION
# =============================================================================


class PatternType(Enum):
    """Known patterns that can be detected in data."""

    URL = auto()
    EMAIL = auto()
    ISO_DATE = auto()
    ISO_DATETIME = auto()
    UUID = auto()
    JSON_STRING = auto()
    FILE_PATH = auto()
    CODE_PYTHON = auto()
    CODE_SQL = auto()
    CODE_HTML = auto()
    MARKDOWN = auto()
    PHONE_NUMBER = auto()
    IP_ADDRESS = auto()
    CREDIT_CARD = auto()
    HEX_COLOR = auto()

    PERCENT_0_1 = auto()
    PERCENT_0_100 = auto()
    CURRENCY = auto()
    LATITUDE = auto()
    LONGITUDE = auto()
    TIMESTAMP_UNIX = auto()
    TIMESTAMP_UNIX_MS = auto()
    YEAR = auto()

    MONOTONIC_INC = auto()
    MONOTONIC_DEC = auto()
    MOSTLY_ZEROS = auto()
    BINARY = auto()


@dataclass
class PatternMatch:
    """A detected pattern."""

    pattern: PatternType
    confidence: float
    details: dict[str, Any] = field(default_factory=dict)


class PatternDetector(Protocol):
    """Protocol for pattern detectors."""

    def detect(self, samples: list[Any]) -> PatternMatch | None: ...


class PatternLibrary:
    """Registry of pattern detectors."""

    def __init__(self) -> None:
        self._detectors: list[PatternDetector] = []

    def register(self, detector: PatternDetector) -> None:
        self._detectors.append(detector)

    def detect_all(self, samples: list[Any]) -> list[PatternMatch]:
        matches: list[PatternMatch] = []
        for detector in self._detectors:
            try:
                match = detector.detect(samples)
            except Exception:
                match = None
            if match:
                matches.append(match)
        return sorted(matches, key=lambda m: -m.confidence)


# =============================================================================
# REDACTION
# =============================================================================


class Redactor:
    """Redact sensitive information from samples."""

    PATTERNS = {
        "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
        "api_key": re.compile(r"(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36})"),
        "credit_card": re.compile(
            r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
        ),
        "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "phone": re.compile(
            r"\b(\+?1?[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        ),
        "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    }

    def __init__(self, config: RedactionConfig):
        self.config = config
        self._active_patterns: dict[str, re.Pattern] = {}

        if config.redact_emails:
            self._active_patterns["email"] = self.PATTERNS["email"]
        if config.redact_api_keys:
            self._active_patterns["api_key"] = self.PATTERNS["api_key"]
        if config.redact_pii:
            self._active_patterns["credit_card"] = self.PATTERNS["credit_card"]
            self._active_patterns["ssn"] = self.PATTERNS["ssn"]
            self._active_patterns["phone"] = self.PATTERNS["phone"]
        if config.redact_ip_addresses:
            self._active_patterns["ip_address"] = self.PATTERNS["ip_address"]

    def redact(self, value: Any) -> tuple[Any, bool]:
        """Redact a value. Returns (redacted_value, was_redacted)."""
        if isinstance(value, str):
            return self._redact_string(value)
        if isinstance(value, dict):
            return self._redact_dict(value)
        if isinstance(value, (list, tuple)):
            redacted = []
            any_redacted = False
            for item in value:
                r, was = self.redact(item)
                redacted.append(r)
                any_redacted |= was
            return (type(value)(redacted) if isinstance(value, tuple) else redacted), any_redacted
        return value, False

    def _redact_string(self, s: str) -> tuple[str, bool]:
        was_redacted = False
        for name, pattern in self._active_patterns.items():
            if pattern.search(s):
                s = pattern.sub(f"[REDACTED:{name.upper()}]", s)
                was_redacted = True
        return s, was_redacted

    def _redact_dict(self, d: dict) -> tuple[dict, bool]:
        result: dict[Any, Any] = {}
        was_redacted = False

        for key, value in d.items():
            if self.config.redact_passwords and any(
                re.search(pat, str(key), re.I) for pat in self.config.field_name_patterns
            ):
                result[key] = "[REDACTED:SENSITIVE_FIELD]"
                was_redacted = True
            else:
                result[key], r = self.redact(value)
                was_redacted |= r

        return result, was_redacted


# =============================================================================
# STRING FORMATTING HELPERS
# =============================================================================


def pluralize(n: int, singular: str, plural: str | None = None) -> str:
    """Pluralize a word based on count."""
    if plural is None:
        plural = singular + "s"
    return singular if n == 1 else plural


def format_count(n: int, singular: str, plural: str | None = None) -> str:
    """Format count with pluralized word."""
    return f"{n:,} {pluralize(n, singular, plural)}"


def format_percent(ratio: float, precision: int = 1) -> str:
    """Format ratio as percentage."""
    return f"{ratio * 100:.{precision}f}%"


def format_bytes(n: int) -> str:
    """Format byte count as human-readable."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(n) < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration as human-readable."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    if seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    hours = seconds / 3600
    return f"{hours:.1f} hours"


def oxford_comma(items: list[str], conjunction: str = "and") -> str:
    """Format list with oxford comma."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    return f"{', '.join(items[:-1])}, {conjunction} {items[-1]}"


def truncate_list(items: list[str], max_items: int = 5, total: int | None = None) -> str:
    """Format list with truncation."""
    if len(items) <= max_items:
        return oxford_comma(items)

    shown = items[:max_items]
    remaining = (total or len(items)) - max_items
    return f"{', '.join(shown)}, and {remaining} more"


# =============================================================================
# AFFORDANCE AND VIEW SUGGESTIONS
# =============================================================================


class Affordance(Enum):
    """Things you can do with data."""

    INDEXABLE = "access by index or key"
    SLICEABLE = "take ranges or slices"
    ITERABLE = "iterate over items"
    SEARCHABLE = "search contents"
    EXPANDABLE = "drill into nested structure"
    SORTABLE = "sort"
    FILTERABLE = "filter"
    GROUPABLE = "group by values"
    AGGREGATABLE = "compute aggregates"
    JOINABLE = "join with other data"
    PLOT_LINE = "plot as line chart"
    PLOT_BAR = "plot as bar chart"
    PLOT_SCATTER = "plot as scatter plot"
    PLOT_HISTOGRAM = "plot as histogram"
    PLOT_HEATMAP = "plot as heatmap"
    MAPPABLE = "display on map"
    EXPORTABLE = "export to file"
    DOWNLOADABLE = "download"
    SERIALIZABLE = "serialize to JSON"
    EDITABLE = "edit values"
    APPENDABLE = "add items"
    CALLABLE = "call or invoke"
    RENDERABLE = "render as formatted content"
    PLAYABLE = "play as audio or video"
    DISPLAYABLE = "display as image"


def format_affordances(affordances: list[Affordance]) -> str:
    """Format list of affordances as prose."""
    if not affordances:
        return ""

    actions = [a.value for a in affordances[:6]]
    return f"You can {oxford_comma(actions, 'or')}."


@dataclass
class ViewSuggestion:
    """Suggested way to display the data."""

    widget: str
    confidence: float
    reason: str
    config: dict[str, Any] = field(default_factory=dict)


def format_view_suggestion(suggestions: list[ViewSuggestion]) -> str:
    """Format view suggestions as prose."""
    if not suggestions:
        return ""

    best = suggestions[0]
    widget_descriptions = {
        "table": "a table",
        "json_tree": "a collapsible JSON tree",
        "line_chart": "a line chart",
        "bar_chart": "a bar chart",
        "scatter_plot": "a scatter plot",
        "histogram": "a histogram",
        "heatmap": "a heatmap",
        "image": "an image viewer",
        "image_grid": "an image grid",
        "map": "an interactive map",
        "network_graph": "a network diagram",
        "code_editor": "a code editor with syntax highlighting",
        "markdown": "rendered markdown",
        "form": "an editable form",
        "audio_player": "an audio player",
        "video_player": "a video player",
        "timeline": "a timeline",
        "tree": "a tree view",
        "figure": "an interactive figure",
    }

    widget_desc = widget_descriptions.get(best.widget, best.widget)

    if len(suggestions) > 1:
        alts = [widget_descriptions.get(s.widget, s.widget) for s in suggestions[1:3]]
        return f"Best displayed as {widget_desc}, or alternatively {oxford_comma(alts, 'or')}."

    return f"Best displayed as {widget_desc}."
