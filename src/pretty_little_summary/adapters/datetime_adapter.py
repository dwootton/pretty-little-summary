"""Adapters for datetime-related types."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any

from pretty_little_summary.adapters._base import AdapterRegistry
from pretty_little_summary.core import MetaDescription


class DateTimeAdapter:
    """Adapter for datetime/date/time/timedelta objects."""

    @staticmethod
    def can_handle(obj: Any) -> bool:
        return isinstance(obj, (datetime, date, time, timedelta))

    @staticmethod
    def extract_metadata(obj: Any) -> MetaDescription:
        meta: MetaDescription = {
            "object_type": f"{type(obj).__module__}.{type(obj).__name__}",
            "adapter_used": "DateTimeAdapter",
        }

        metadata: dict[str, Any] = {}

        if isinstance(obj, datetime):
            metadata.update(_describe_datetime(obj))
        elif isinstance(obj, date) and not isinstance(obj, datetime):
            metadata.update(_describe_date(obj))
        elif isinstance(obj, time):
            metadata.update(_describe_time(obj))
        elif isinstance(obj, timedelta):
            metadata.update(_describe_timedelta(obj))

        if metadata:
            meta["metadata"] = metadata
            meta["nl_summary"] = _build_nl_summary(metadata)

        return meta


def _describe_datetime(value: datetime) -> dict[str, Any]:
    tzinfo = value.tzinfo
    metadata: dict[str, Any] = {
        "type": "datetime",
        "iso": value.isoformat(),
        "timezone": str(tzinfo) if tzinfo else None,
        "weekday": value.strftime("%A"),
    }
    now = datetime.now(tzinfo) if tzinfo else datetime.now()
    try:
        delta = value - now
        metadata["relative_days"] = int(delta.total_seconds() // 86400)
    except Exception:
        pass
    return metadata


def _describe_date(value: date) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "type": "date",
        "iso": value.isoformat(),
        "weekday": value.strftime("%A"),
    }
    today = date.today()
    metadata["relative_days"] = (value - today).days
    return metadata


def _describe_time(value: time) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "type": "time",
        "iso": value.isoformat(),
        "timezone": str(value.tzinfo) if value.tzinfo else None,
    }
    metadata["hour"] = value.hour
    metadata["minute"] = value.minute
    return metadata


def _describe_timedelta(value: timedelta) -> dict[str, Any]:
    total_seconds = int(value.total_seconds())
    metadata: dict[str, Any] = {
        "type": "timedelta",
        "total_seconds": total_seconds,
        "days": value.days,
    }
    return metadata


AdapterRegistry.register(DateTimeAdapter)


def _build_nl_summary(metadata: dict[str, Any]) -> str:
    dtype = metadata.get("type")
    if dtype == "datetime":
        iso = metadata.get("iso")
        tz = metadata.get("timezone")
        weekday = metadata.get("weekday")
        parts = [f"A datetime: {iso}."]
        if tz:
            parts.append(f"Timezone: {tz}.")
        else:
            parts.append("Timezone: naive.")
        if weekday:
            parts.append(f"{weekday}.")
        return " ".join(parts)
    if dtype == "date":
        iso = metadata.get("iso")
        weekday = metadata.get("weekday")
        parts = [f"A date: {iso}."]
        if weekday:
            parts.append(f"{weekday}.")
        return " ".join(parts)
    if dtype == "time":
        iso = metadata.get("iso")
        tz = metadata.get("timezone")
        parts = [f"A time: {iso}."]
        if tz:
            parts.append(f"Timezone: {tz}.")
        else:
            parts.append("Timezone: naive.")
        return " ".join(parts)
    if dtype == "timedelta":
        total_seconds = metadata.get("total_seconds")
        days = metadata.get("days")
        if total_seconds is not None:
            if days:
                return f"A duration of {days} days ({total_seconds} seconds)."
            return f"A duration of {total_seconds} seconds."
        return "A duration."
    return "A datetime-related value."


def _format_relative(relative_days: int | None) -> str | None:
    if relative_days is None:
        return None
    if relative_days == 0:
        return "Today."
    if relative_days > 0:
        return f"In {relative_days} days."
    return f"{abs(relative_days)} days ago."
