#!/usr/bin/env python3
"""
metric_selector_support.py

Drop-in helper functions for converting common Dynatrace Classic metricSelector
expressions into Gen3 Dashboard DQL query strings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional, Sequence

BUILTIN_CLASSIC_TO_GRAIL_OVERRIDES: Dict[str, str] = {
    "builtin:tech.generic.cpu.usage": "dt.process.cpu.usage",
}

_AGGREGATIONS = {"avg", "sum", "min", "max", "count"}
_SORT_RE = re.compile(
    r"^sort\(\s*value\(\s*(?P<agg>[a-zA-Z_][\w]*)\s*,\s*(?P<order>ascending|descending|asc|desc)\s*\)\s*\)\s*$",
    re.IGNORECASE,
)
_LIMIT_RE = re.compile(r"^limit\(\s*(?P<limit>\d+)\s*\)\s*$", re.IGNORECASE)
_SPLIT_BY_RE = re.compile(r"^splitBy\((?P<body>.*)\)\s*$", re.IGNORECASE | re.DOTALL)
_FILTER_RE = re.compile(r"^filter\((?P<body>.*)\)\s*$", re.IGNORECASE | re.DOTALL)


@dataclass
class ParsedMetricSelector:
    original: str
    metric_key: str
    aggregation: str = "avg"
    rollup: Optional[str] = None
    split_by: List[str] = field(default_factory=list)
    limit: Optional[int] = None
    sort_aggregation: Optional[str] = None
    sort_direction: str = "desc"
    include_names: bool = False
    include_parents: bool = False
    filters: List[str] = field(default_factory=list)
    unsupported_parts: List[str] = field(default_factory=list)


def split_metric_selector(selector: str) -> List[str]:
    """Split a classic selector on ':' while respecting quotes and parentheses."""
    parts: List[str] = []
    buf: List[str] = []
    depth = 0
    in_quote: Optional[str] = None
    escaped = False

    for ch in selector.strip():
        if escaped:
            buf.append(ch)
            escaped = False
            continue
        if ch == "\\":
            buf.append(ch)
            escaped = True
            continue
        if in_quote:
            buf.append(ch)
            if ch == in_quote:
                in_quote = None
            continue
        if ch in {'"', "'"}:
            buf.append(ch)
            in_quote = ch
            continue
        if ch == "(":
            depth += 1
            buf.append(ch)
            continue
        if ch == ")" and depth > 0:
            depth -= 1
            buf.append(ch)
            continue
        if ch == ":" and depth == 0:
            part = "".join(buf).strip()
            if part:
                parts.append(part)
            buf = []
            continue
        buf.append(ch)

    part = "".join(buf).strip()
    if part:
        parts.append(part)
    return parts


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1].replace(r'\"', '"').replace(r"\'", "'")
    return value


def _csv_like_values(body: str) -> List[str]:
    values: List[str] = []
    buf: List[str] = []
    in_quote: Optional[str] = None
    escaped = False
    depth = 0
    for ch in body:
        if escaped:
            buf.append(ch)
            escaped = False
            continue
        if ch == "\\":
            buf.append(ch)
            escaped = True
            continue
        if in_quote:
            buf.append(ch)
            if ch == in_quote:
                in_quote = None
            continue
        if ch in {'"', "'"}:
            buf.append(ch)
            in_quote = ch
            continue
        if ch == "(":
            depth += 1
            buf.append(ch)
            continue
        if ch == ")" and depth > 0:
            depth -= 1
            buf.append(ch)
            continue
        if ch == "," and depth == 0:
            raw = "".join(buf).strip()
            if raw:
                values.append(_unquote(raw))
            buf = []
            continue
        buf.append(ch)
    raw = "".join(buf).strip()
    if raw:
        values.append(_unquote(raw))
    return values


def parse_metric_selector(selector: str) -> ParsedMetricSelector:
    raw_parts = split_metric_selector(selector)
    if not raw_parts:
        raise ValueError("Empty metric selector")

    def _is_transform(part: str) -> bool:
        lower = part.strip().lower()
        return (
            lower in _AGGREGATIONS
            or lower in {"auto", "parents", "names"}
            or _SPLIT_BY_RE.match(part.strip()) is not None
            or _FILTER_RE.match(part.strip()) is not None
            or _SORT_RE.match(part.strip()) is not None
            or _LIMIT_RE.match(part.strip()) is not None
        )

    first_transform_idx = next(
        (idx for idx, part in enumerate(raw_parts) if idx > 0 and _is_transform(part)),
        len(raw_parts),
    )
    metric_key = ":".join(raw_parts[:first_transform_idx])
    parts = [metric_key] + raw_parts[first_transform_idx:]

    parsed = ParsedMetricSelector(original=selector, metric_key=parts[0])

    for part in parts[1:]:
        normalized = part.strip()
        lower = normalized.lower()

        if lower in _AGGREGATIONS:
            parsed.aggregation = lower
            continue
        if lower == "auto":
            parsed.rollup = "avg"
            continue
        if lower == "parents":
            parsed.include_parents = True
            continue
        if lower == "names":
            parsed.include_names = True
            continue

        split_match = _SPLIT_BY_RE.match(normalized)
        if split_match:
            parsed.split_by.extend(_csv_like_values(split_match.group("body")))
            continue

        sort_match = _SORT_RE.match(normalized)
        if sort_match:
            parsed.sort_aggregation = sort_match.group("agg").lower()
            order = sort_match.group("order").lower()
            parsed.sort_direction = "asc" if order in {"ascending", "asc"} else "desc"
            continue

        limit_match = _LIMIT_RE.match(normalized)
        if limit_match:
            parsed.limit = int(limit_match.group("limit"))
            continue

        filter_match = _FILTER_RE.match(normalized)
        if filter_match:
            parsed.filters.append(filter_match.group("body").strip())
            continue

        parsed.unsupported_parts.append(normalized)

    return parsed


def classic_metric_to_grail_metric(metric_key: str, metric_mapping: Optional[Dict[str, Any]] = None) -> str:
    if metric_mapping and metric_key in metric_mapping:
        mapped = metric_mapping[metric_key]
        if isinstance(mapped, str):
            return mapped
        if isinstance(mapped, dict):
            for candidate_key in ("gen3_metric", "grail_metric", "metric", "metricId", "metric_id"):
                value = mapped.get(candidate_key)
                if isinstance(value, str) and value.strip():
                    return value.strip()

    if metric_key in BUILTIN_CLASSIC_TO_GRAIL_OVERRIDES:
        return BUILTIN_CLASSIC_TO_GRAIL_OVERRIDES[metric_key]
    if metric_key.startswith("dt."):
        return metric_key
    if metric_key.startswith("dsfm:"):
        return "dt.sfm." + metric_key[len("dsfm:"):].replace(":", ".")
    if metric_key.startswith("builtin:"):
        return "dt." + metric_key[len("builtin:"):].replace(":", ".")
    return metric_key


def _metric_alias(metric_key: str, aggregation: str) -> str:
    leaf = re.sub(r"[^A-Za-z0-9_]+", "_", metric_key.split(".")[-1]).strip("_")
    if not leaf:
        leaf = "value"
    return leaf if leaf != aggregation else f"{leaf}_value"


def metric_selector_to_dql(
    selector: str,
    metric_mapping: Optional[Dict[str, Any]] = None,
    *,
    alias: Optional[str] = None,
    add_entity_names: bool = True,
    use_scalar_sort_column: bool = False,
) -> str:
    parsed = parse_metric_selector(selector)
    grail_metric = classic_metric_to_grail_metric(parsed.metric_key, metric_mapping)
    aggregation = parsed.aggregation if parsed.aggregation in _AGGREGATIONS else "avg"
    alias = alias or _metric_alias(grail_metric, aggregation)

    metric_args = [grail_metric]
    if parsed.rollup:
        metric_args.append(f"rollup: {parsed.rollup}")

    timeseries_args = [f"{alias} = {aggregation}({', '.join(metric_args)})"]

    scalar_alias = None
    if use_scalar_sort_column:
        scalar_alias = f"{alias}_summary"
        timeseries_args.append(f"{scalar_alias} = {aggregation}({', '.join(metric_args + ['scalar: true'])})")

    if parsed.split_by:
        timeseries_args.append("by: { " + ", ".join(parsed.split_by) + " }")

    lines = ["timeseries " + ",\n  ".join(timeseries_args)]

    if add_entity_names:
        for dimension in parsed.split_by:
            if dimension.startswith("dt.entity."):
                name_field = dimension.replace("dt.entity.", "").replace(".", "_") + "_name"
                lines.append(f"| fieldsAdd {name_field} = entityName({dimension})")

    if parsed.sort_aggregation or parsed.limit is not None:
        if use_scalar_sort_column and scalar_alias:
            sort_expr = scalar_alias
        else:
            sort_fn = {
                "avg": "arrayAvg",
                "sum": "arraySum",
                "min": "arrayMin",
                "max": "arrayMax",
                "count": "arraySum",
            }.get((parsed.sort_aggregation or aggregation).lower(), "arrayAvg")
            sort_expr = f"{sort_fn}({alias})"
        lines.append(f"| sort {sort_expr} {parsed.sort_direction}")

    if parsed.limit is not None:
        lines.append(f"| limit {parsed.limit}")

    return "\n".join(lines)


def find_metric_selectors(value: Any) -> List[str]:
    selectors: List[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "metricSelector" and isinstance(child, str) and child.strip():
                selectors.append(child.strip())
            else:
                selectors.extend(find_metric_selectors(child))
    elif isinstance(value, list):
        for child in value:
            selectors.extend(find_metric_selectors(child))
    return selectors


def convert_metric_selectors_to_dql_queries(value: Any, metric_mapping: Optional[Dict[str, Any]] = None) -> List[str]:
    return [metric_selector_to_dql(selector, metric_mapping=metric_mapping) for selector in find_metric_selectors(value)]
