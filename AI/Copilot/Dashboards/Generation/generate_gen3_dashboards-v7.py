#!/usr/bin/env python3
"""
generate_gen3_dashboards.py

Classic Dynatrace dashboard JSON -> uploadable Gen3 dashboard JSON.

This module intentionally emits the dashboard CONTENT shape, not a broader
Document API wrapper. The generated JSON is model-like and upload-friendly:

{
  "version": 21,
  "variables": [],
  "tiles": {
    "1": { ... },
    "2": { ... }
  },
  "layouts": {
    "1": { ... },
    "2": { ... }
  }
}

Key behavior:
- Uses ordinal tile/layout keys starting with "1".
- Removes extraneous fields.
- Converts classic metric keys to Grail metric keys using classic_metric_to_grail_metric.yaml.
- Converts classic TOP_LIST tiles to categoricalBarChart.
- Uses fieldsAdd to aggregate timeseries arrays into scalar values for categoricalBarChart.
- Sets TOP_LIST categoricalBarChart label visibility off and legend hidden.
- Builds section-aware, balanced layouts:
  - Headers/markdown tiles start new logical sections and occupy full-width rows.
  - Data tile height is tuned by visualization type.
  - Rows are auto-balanced for symmetry.
  - Layout respects 24-column grid, min w=6, min h=4, max w=24, max h=16.

Important layout note:
With a 24-column grid and minimum tile width of 6, the maximum feasible number
of tiles per row is 4. Although the high-level target allows 1-6 tiles per row,
choosing 5 or 6 would require width below 6 or overflow beyond 24. This module
therefore enforces the mathematically valid maximum of 4 under the supplied
width constraints.

Typical usage from AI/Copilot/Dashboards/Generation:

python generate_gen3_dashboards.py \
  --input input_json/00000000-dddd-bbbb-ffff-000000000008.json \
  --output-dir generated_gen3 \
  --metric-map ../../../../NewPlatform/Dashboards/classic_metric_to_grail_metric.yaml
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

import yaml


# =============================================================================
# Constants
# =============================================================================

UNMAPPED_METRICS = set()

MODEL_DASHBOARD_VERSION = 21

GRID_WIDTH = 24
REQUESTED_MAX_TILES_PER_ROW = 6
MIN_TILE_WIDTH = 6
MAX_TILE_WIDTH = 24
MIN_TILE_HEIGHT = 4
MAX_TILE_HEIGHT = 16

# Given GRID_WIDTH=24 and MIN_TILE_WIDTH=6, 4 is the largest possible non-overflowing row.
EFFECTIVE_MAX_TILES_PER_ROW = min(REQUESTED_MAX_TILES_PER_ROW, GRID_WIDTH // MIN_TILE_WIDTH)

# DEBUG:
# DEFAULT_INPUT = Path("input_json")
DEFAULT_INPUT = Path("input_json_testing")
DEFAULT_OUTPUT_DIR = Path("generated_gen3")
DEFAULT_MAPPING_FILE = Path("../../Metrics/Conversion/classic_metric_to_grail_metric.yaml")


# =============================================================================
# IO
# =============================================================================


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def load_yaml(path: Optional[Path]) -> Any:
    if not path:
        return {}
    if not path.exists():
        print(f"WARNING: Metric mapping file not found: {path}", file=sys.stderr)
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def iter_json_files(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        yield input_path
        return

    for path in sorted(input_path.glob("*.json")):
        if not path.name.startswith("."):
            yield path


# =============================================================================
# Metric mapping
# =============================================================================


def build_metric_map(raw_mapping: Any) -> Dict[str, str]:
    """
    Normalize multiple likely YAML mapping shapes into:
        {classic_metric: grail_metric}

    Supported examples:

      builtin:host.cpu.usage: dt.host.cpu.usage

      metrics:
        - classic: builtin:host.cpu.usage
          grail: dt.host.cpu.usage

      mappings:
        - classicMetric: builtin:host.cpu.usage
          grailMetric: dt.host.cpu.usage
    """
    result: Dict[str, str] = {}

    def add(classic: Any, grail: Any) -> None:
        if classic is None or grail is None:
            return
        classic_s = str(classic).strip()
        grail_s = str(grail).strip()
        if classic_s and grail_s:
            result[classic_s] = grail_s

    def consume(value: Any) -> None:
        if isinstance(value, list):
            for item in value:
                consume(item)
            return

        if not isinstance(value, Mapping):
            return

        classic = (
            value.get("classic")
            or value.get("classicMetric")
            or value.get("classic_metric")
            or value.get("classicMetricKey")
            or value.get("classic_metric_key")
            or value.get("source")
            or value.get("from")
        )
        grail = (
            value.get("grail")
            or value.get("grailMetric")
            or value.get("grail_metric")
            or value.get("grailMetricKey")
            or value.get("grail_metric_key")
            or value.get("target")
            or value.get("to")
        )
        if classic and grail:
            add(classic, grail)
            return

        for key, item in value.items():
            if key in {"metrics", "mappings", "metricMappings", "classicToGrail", "classic_to_grail"}:
                consume(item)
            elif isinstance(item, str):
                add(key, item)
            elif isinstance(item, Mapping):
                nested = (
                    item.get("grail")
                    or item.get("grailMetric")
                    or item.get("grail_metric")
                    or item.get("target")
                    or item.get("to")
                )
                if nested:
                    add(key, nested)
                else:
                    consume(item)
            elif isinstance(item, list):
                consume(item)

    consume(raw_mapping)
    return result


def extract_metric_key_from_selector(selector: str) -> str:
    """Extract the base metric name from a classic metric selector/expression."""
    if not selector:
        return selector

    match = re.search(r"(builtin:[A-Za-z0-9_.:-]+|ext:[A-Za-z0-9_.:-]+|calc:[A-Za-z0-9_.:-]+)", selector)
    if match:
        return match.group(1).rstrip(":")

    return selector.split(":splitBy", 1)[0].split(":filter", 1)[0].strip()


def camel_to_snake_metric_path(path: str) -> str:
    converted = []
    for part in path.split("."):
        part = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", part)
        converted.append(part.lower())
    return ".".join(converted)


def to_grail_metric(
    classic_metric: str,
    metric_map: Mapping[str, str],
) -> Optional[str]:

    classic_metric = (classic_metric or "").strip()

    if not classic_metric:
        return None

    if classic_metric in metric_map:
        return metric_map[classic_metric]

    # ✅ log + collect
    print(f"WARNING: Unmapped metric: {classic_metric}")
    UNMAPPED_METRICS.add(classic_metric)

    return None

# =============================================================================
# Classic dashboard / tile extraction
# =============================================================================


def dashboard_name(classic_dashboard: Mapping[str, Any], fallback: str) -> str:
    metadata = classic_dashboard.get("dashboardMetadata") or {}
    return metadata.get("name") or classic_dashboard.get("name") or Path(fallback).stem


def tile_title(tile: Mapping[str, Any], default: str = "") -> str:
    filter_config = tile.get("filterConfig") or {}
    return (
        tile.get("customName")
        or tile.get("name")
        or tile.get("configuredName")
        or filter_config.get("customName")
        or filter_config.get("defaultName")
        or default
    )


def tile_type(tile: Mapping[str, Any]) -> str:
    return str(tile.get("tileType") or "").upper()


def is_markdown_like(tile: Mapping[str, Any]) -> bool:
    return tile_type(tile) in {"HEADER", "MARKDOWN"}


def is_top_list(tile: Mapping[str, Any]) -> bool:
    visual_config = tile.get("visualConfig") or {}
    filter_config = tile.get("filterConfig") or {}
    chart_config = filter_config.get("chartConfig") or {}
    return (
        str(visual_config.get("type") or "").upper() == "TOP_LIST"
        or str(chart_config.get("type") or "").upper() == "TOP_LIST"
    )


def extract_classic_queries(tile: Mapping[str, Any]) -> List[Dict[str, Any]]:
    print('DEBUG:', 'extract_classic_queries: starting...')

    print('DEBUG:', 'extract_classic_queries: tile:', tile)

    queries = tile.get("queries")
    if isinstance(queries, list) and queries:
        result = [dict(q) for q in queries if isinstance(q, Mapping) and q.get("metric")]
    else:
        result = [dict(q) for q in queries if isinstance(q, Mapping) and q.get("metricSelector")]

    print('DEBUG:', 'extract_classic_queries: queries:', queries)

    filter_config = tile.get("filterConfig") or {}
    chart_config = filter_config.get("chartConfig") or {}
    series = chart_config.get("series")

    if isinstance(series, Mapping) and series.get("metric"):
        return [dict(series)]

    if isinstance(series, list):
        return [dict(item) for item in series if isinstance(item, Mapping) and item.get("metric")]

    metric_expressions = tile.get("metricExpressions")
    if isinstance(metric_expressions, list):
        extracted = []
        for expression in metric_expressions:
            metric = extract_metric_key_from_selector(str(expression))
            if metric:
                extracted.append({"metric": metric})
        return extracted

    print('DEBUG: Nada!')

    return []


def split_by(query: Mapping[str, Any]) -> List[str]:
    raw = query.get("splitBy") or query.get("dimensions") or []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return [str(item) for item in raw if str(item).strip()]
    return []


def limit_for(query: Mapping[str, Any], default: int = 20) -> int:
    value = query.get("limit")
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def aggregation_for(query: Mapping[str, Any]) -> str:
    """
    Return a DQL aggregation. Classic values AUTO/DEFAULT do not map directly,
    so default to avg unless a specific aggregation is present.
    """
    for key in ("aggregation", "timeAggregation", "spaceAggregation"):
        value = query.get(key)
        if value and str(value).upper() not in {"AUTO", "DEFAULT", "NONE"}:
            return normalize_aggregation(str(value))
    return "avg"


def normalize_aggregation(value: str) -> str:
    aliases = {
        "average": "avg",
        "avg": "avg",
        "mean": "avg",
        "sum": "sum",
        "total": "sum",
        "min": "min",
        "max": "max",
        "count": "count",
        "median": "median",
    }
    return aliases.get(value.strip().lower(), "avg")


# =============================================================================
# DQL helpers
# =============================================================================


def dql_metric(metric: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", metric):
        return metric
    return "`" + metric.replace("`", "\\`") + "`"


def dql_field(field: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", field):
        return field
    return "`" + field.replace("`", "\\`") + "`"


def value_name(metric: str, index: int = 0) -> str:
    base = metric.split(".")[-1]
    base = re.sub(r"[^A-Za-z0-9_]", "_", base).strip("_") or "value"
    if re.match(r"^\d", base):
        base = "value_" + base
    if index:
        base = f"{base}_{index + 1}"
    return base


def make_dql(
    grail_metric: str,
    aggregation: str,
    dimensions: Sequence[str],
    top_list: bool,
    limit: int,
    index: int = 0,
) -> str:
    array_field = value_name(grail_metric, index)
    query = f"timeseries {array_field} = {aggregation}({dql_metric(grail_metric)})"

    if dimensions:
        query += ", by: {" + ", ".join(dql_field(d) for d in dimensions) + "}"

    if top_list:
        scalar_field = f"{array_field}_value"
        query += f"\n| fieldsAdd {scalar_field} = arrayAvg({array_field})"
        if dimensions:
            query += "\n| fields " + ", ".join(dql_field(d) for d in dimensions) + f", {scalar_field}"
        else:
            query += f"\n| fields {scalar_field}"
        query += f"\n| sort {scalar_field} desc"
        query += f"\n| limit {limit}"

    return query


# =============================================================================
# Gen3 tile payloads
# =============================================================================


def markdown_tile_from_classic(tile: Mapping[str, Any]) -> Dict[str, Any]:
    title = tile_title(tile)
    content = tile.get("markdown") or tile.get("content") or title
    if title and not str(content).lstrip().startswith("#"):
        content = f"## {title}"
    return {
        "type": "markdown",
        "content": str(content or ""),
    }


def categorical_bar_chart_settings() -> Dict[str, Any]:
    return {
        "legend": {
            "hidden": True
        },
        "isValueLabelVisible": False,
        "isCategoryLabelVisible": False
    }


def line_chart_settings() -> Dict[str, Any]:
    return {
        "legend": {
            "hidden": True
        }
    }


# DEBUG START
def data_tile_from_classic(
        classic_tile: Mapping[str, Any],
        query: Mapping[str, Any],
        metric_map: Mapping[str, str],
        index: int,
        omit_line_chart_settings: bool,
) -> Dict[str, Any]:
    import html
    import re

    def split_selector(selector):
        parts = []
        buf = []
        depth = 0
        quote = None
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

            if quote:
                buf.append(ch)
                if ch == quote:
                    quote = None
                continue

            if ch in ("'", '"'):
                buf.append(ch)
                quote = ch
                continue

            if ch == "(":
                depth += 1
                buf.append(ch)
                continue

            if ch == ")":
                if depth > 0:
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

    def is_selector_transform(part):
        lower = part.strip().lower()
        return (
                lower in {
            "avg",
            "sum",
            "min",
            "max",
            "count",
            "auto",
            "parents",
            "names",
        }
                or lower.startswith("splitby(")
                or lower.startswith("sort(")
                or lower.startswith("limit(")
                or lower.startswith("filter(")
                or lower.startswith("merge(")
                or lower.startswith("partition(")
                or lower.startswith("fold(")
        )

    def unquote(value):
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            return value[1:-1].replace(r"\'", "'").replace(r"\"", '"')
        return value

    def split_csv_like(value):
        values = []
        buf = []
        depth = 0
        quote = None
        escaped = False

        for ch in value:
            if escaped:
                buf.append(ch)
                escaped = False
                continue

            if ch == "\\":
                buf.append(ch)
                escaped = True
                continue

            if quote:
                buf.append(ch)
                if ch == quote:
                    quote = None
                continue

            if ch in ("'", '"'):
                buf.append(ch)
                quote = ch
                continue

            if ch == "(":
                depth += 1
                buf.append(ch)
                continue

            if ch == ")":
                if depth > 0:
                    depth -= 1
                buf.append(ch)
                continue

            if ch == "," and depth == 0:
                item = "".join(buf).strip()
                if item:
                    values.append(unquote(item))
                buf = []
                continue

            buf.append(ch)

        item = "".join(buf).strip()
        if item:
            values.append(unquote(item))

        return values

    def extract_selector_from_metric_expression(expression):
        """
        Handles classic metricExpressions like:

            resolution=Inf&(builtin:metric.key:splitBy("x"):avg):limit(100):names

        The selector is the balanced parenthesized expression immediately after '&('.
        """
        if not expression:
            return ""

        text = html.unescape(str(expression)).strip()

        start = text.find("&(")
        if start < 0:
            return ""

        pos = start + 1  # points at '('
        depth = 0
        quote = None
        escaped = False
        buf = []

        for ch in text[pos:]:
            if escaped:
                buf.append(ch)
                escaped = False
                continue

            if ch == "\\":
                buf.append(ch)
                escaped = True
                continue

            if quote:
                buf.append(ch)
                if ch == quote:
                    quote = None
                continue

            if ch in ("'", '"'):
                buf.append(ch)
                quote = ch
                continue

            if ch == "(":
                depth += 1
                if depth > 1:
                    buf.append(ch)
                continue

            if ch == ")":
                depth -= 1
                if depth == 0:
                    return "".join(buf).strip()
                buf.append(ch)
                continue

            if depth > 0:
                buf.append(ch)

        return ""

    def metric_selector_for_tile():
        """
        Prefer query.metricSelector. If absent, fall back to classic_tile.metricExpressions.
        This is important because some classic dashboard paths carry the selector only
        in metricExpressions.
        """
        selector = str(query.get("metricSelector") or "").strip()
        if selector:
            return selector

        for expression in classic_tile.get("metricExpressions") or []:
            selector = extract_selector_from_metric_expression(expression)
            if selector:
                return selector

        return ""

    def parse_metric_selector(selector):
        raw_parts = split_selector(selector)

        metric_parts = []
        transform_parts = []

        found_transform = False
        for part in raw_parts:
            if not found_transform and is_selector_transform(part):
                found_transform = True

            if found_transform:
                transform_parts.append(part)
            else:
                metric_parts.append(part)

        classic_metric = ":".join(metric_parts).strip()

        parsed = {
            "metric": classic_metric,
            "aggregation": "avg",
            "dimensions": [],
            "limit": None,
            "sort_aggregation": None,
            "sort_direction": "desc",
            "rollup": None,
        }

        for part in transform_parts:
            text = part.strip()
            lower = text.lower()

            if lower in {"avg", "sum", "min", "max", "count"}:
                parsed["aggregation"] = lower
                continue

            if lower == "auto":
                parsed["rollup"] = "avg"
                continue

            if lower in {"parents", "names"}:
                continue

            split_match = re.match(
                r"^splitBy\((?P<body>.*)\)$",
                text,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if split_match:
                parsed["dimensions"].extend(split_csv_like(split_match.group("body")))
                continue

            sort_match = re.match(
                r"^sort\(\s*value\(\s*(?P<agg>[A-Za-z_][\w]*)\s*,\s*(?P<direction>ascending|descending|asc|desc)\s*\)\s*\)$",
                text,
                flags=re.IGNORECASE,
            )
            if sort_match:
                parsed["sort_aggregation"] = sort_match.group("agg").lower()
                direction = sort_match.group("direction").lower()
                parsed["sort_direction"] = (
                    "asc" if direction in {"ascending", "asc"} else "desc"
                )
                continue

            limit_match = re.match(
                r"^limit\(\s*(?P<limit>\d+)\s*\)$",
                text,
                flags=re.IGNORECASE,
            )
            if limit_match:
                parsed["limit"] = int(limit_match.group("limit"))
                continue

        return parsed

    def alias_for_metric(grail_metric):
        # For CPU usage, make the alias stable and readable.
        if grail_metric.endswith(".cpu.usage"):
            return "usage"

        alias = re.sub(
            r"[^A-Za-z0-9_]+",
            "_",
            str(grail_metric).split(".")[-1],
        ).strip("_")

        return alias or f"value_{index}"

    def make_dql_from_metric_selector(selector):
        parsed = parse_metric_selector(selector)

        classic_metric = str(parsed["metric"] or "").strip()
        grail_metric = to_grail_metric(classic_metric, metric_map)

        if not grail_metric:
            return None  # ✅ skip tile

        aggregation = parsed["aggregation"] or "avg"
        dimensions = parsed["dimensions"] or []
        rollup = parsed["rollup"]
        limit = parsed["limit"]
        sort_aggregation = parsed["sort_aggregation"] or aggregation
        sort_direction = parsed["sort_direction"] or "desc"

        alias = alias_for_metric(grail_metric)

        metric_args = [grail_metric]
        if rollup:
            metric_args.append(f"rollup: {rollup}")

        timeseries_parts = [
            f"{alias} = {aggregation}({', '.join(metric_args)})"
        ]

        if dimensions:
            timeseries_parts.append("by: { " + ", ".join(dimensions) + " }")

        lines = [
            "timeseries " + ",\n  ".join(timeseries_parts)
        ]

        for dimension in dimensions:
            if dimension.startswith("dt.entity."):
                name_field = (
                        dimension
                        .replace("dt.entity.", "")
                        .replace(".", "_")
                        + "_name"
                )
                lines.append(f"| fieldsAdd {name_field} = entityName({dimension})")

        if sort_aggregation or limit is not None:
            sort_function = {
                "avg": "arrayAvg",
                "sum": "arraySum",
                "min": "arrayMin",
                "max": "arrayMax",
                "count": "arraySum",
            }.get(str(sort_aggregation).lower(), "arrayAvg")

            lines.append(f"| sort {sort_function}({alias}) {sort_direction}")

        if limit is not None:
            lines.append(f"| limit {limit}")

        return grail_metric, "\n".join(lines), limit is not None

    # ------------------------------------------------------------------
    # IMPORTANT:
    # Handle metricSelector before classic metric handling.
    # If this does not run, query["metric"] == None can fall into other
    # caller/default behavior and produce bad keys like:
    # dt.tech.generic.cpu.usage:split_by
    # ------------------------------------------------------------------

    metric_selector = metric_selector_for_tile()
    print('DEBUG CURRENT:', classic_tile)

    if metric_selector:
        result = make_dql_from_metric_selector(metric_selector)
        if not result:
            return None  # ✅ skip tile cleanly
        grail_metric, dql, selector_is_top_list = result

        # top_list = selector_is_top_list or is_top_list(classic_tile)
        top_list = is_top_list(classic_tile)
        visualization = "categoricalBarChart" if top_list else "lineChart"

        out: Dict[str, Any] = {
            "type": "data",
            "title": tile_title(classic_tile, grail_metric),
            "query": dql,
            "visualization": visualization,
        }

        if top_list:
            out["visualizationSettings"] = categorical_bar_chart_settings()
        elif not omit_line_chart_settings:
            out["visualizationSettings"] = line_chart_settings()

        return out

    classic_metric = str(query.get("metric") or "").strip()
    grail_metric = to_grail_metric(classic_metric, metric_map)

    if not grail_metric:
        return None  # ✅ skip tile

    top_list = is_top_list(classic_tile)
    aggregation = aggregation_for(query)
    dimensions = split_by(query)

    visualization = "categoricalBarChart" if top_list else "lineChart"

    out: Dict[str, Any] = {
        "type": "data",
        "title": tile_title(classic_tile, grail_metric),
        "query": make_dql(
            grail_metric=grail_metric,
            aggregation=aggregation,
            dimensions=dimensions,
            top_list=top_list,
            limit=limit_for(query),
            index=index,
        ),
        "visualization": visualization,
    }

    if top_list:
        out["visualizationSettings"] = categorical_bar_chart_settings()
    elif not omit_line_chart_settings:
        out["visualizationSettings"] = line_chart_settings()

    return out


# DEBUG END

# =============================================================================
# Section-aware, type-aware, balanced layout engine
# =============================================================================


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def is_header_payload(tile_payload: Mapping[str, Any]) -> bool:
    return str(tile_payload.get("type") or "").lower() == "markdown"


def is_top_list_payload(tile_payload: Mapping[str, Any]) -> bool:
    return str(tile_payload.get("visualization") or "").lower() == "categoricalbarchart"


def tile_height(tile_payload: Mapping[str, Any]) -> int:
    """
    Type-tuned tile height within user constraints.

    - markdown/header: 4
    - categoricalBarChart/TOP_LIST: 6
    - lineChart/default data: 8
    - singleValue, if introduced later: 4
    """
    tile_kind = str(tile_payload.get("type") or "").lower()
    visualization = str(tile_payload.get("visualization") or "").lower()

    if tile_kind == "markdown":
        return MIN_TILE_HEIGHT
    if visualization == "singlevalue":
        return MIN_TILE_HEIGHT
    if visualization == "categoricalbarchart":
        return clamp(6, MIN_TILE_HEIGHT, MAX_TILE_HEIGHT)
    if visualization == "linechart":
        return clamp(8, MIN_TILE_HEIGHT, MAX_TILE_HEIGHT)
    return clamp(8, MIN_TILE_HEIGHT, MAX_TILE_HEIGHT)


def balanced_row_counts(item_count: int, max_per_row: int = EFFECTIVE_MAX_TILES_PER_ROW) -> List[int]:
    """
    Return visually balanced row counts.

    Examples with effective max 4:
      1 -> [1]
      2 -> [2]
      3 -> [3]
      4 -> [4]
      5 -> [3, 2]
      6 -> [3, 3]
      7 -> [4, 3]
      8 -> [4, 4]
      9 -> [3, 3, 3]
     10 -> [4, 3, 3]
     11 -> [4, 4, 3]
     12 -> [4, 4, 4]
    """
    if item_count <= 0:
        return []

    max_per_row = max(1, max_per_row)
    row_count = (item_count + max_per_row - 1) // max_per_row
    base = item_count // row_count
    remainder = item_count % row_count

    counts = []
    for row_index in range(row_count):
        counts.append(base + (1 if row_index < remainder else 0))

    # Defensive: ensure no row exceeds max_per_row.
    if any(count > max_per_row for count in counts):
        counts = []
        remaining = item_count
        while remaining:
            current = min(max_per_row, remaining)
            counts.append(current)
            remaining -= current

    return counts


def row_width_for_count(count: int) -> int:
    """
    Determine tile width for a row count while honoring min/max width.
    """
    if count <= 0:
        return GRID_WIDTH
    width = GRID_WIDTH // count
    return clamp(width, MIN_TILE_WIDTH, MAX_TILE_WIDTH)


def build_section_aware_balanced_layouts(tiles: Mapping[str, Mapping[str, Any]]) -> Dict[str, Dict[str, int]]:
    """
    Build layouts after all tile payloads are known.

    Rules:
    - Ordinal tile order is preserved.
    - Markdown/header tiles start a new section and get a full-width row.
    - Data tiles after a header belong to that section until the next header.
    - Rows inside each section are auto-balanced for symmetry.
    - Tile height is tuned by visualization type.
    """
    layouts: Dict[str, Dict[str, int]] = {}
    ordered_items = list(tiles.items())
    y = 0
    pending_data: List[Tuple[str, Mapping[str, Any]]] = []

    def flush_data_rows() -> None:
        nonlocal y, pending_data
        if not pending_data:
            return

        counts = balanced_row_counts(len(pending_data))
        cursor = 0

        for count in counts:
            row_items = pending_data[cursor: cursor + count]
            cursor += count

            w = row_width_for_count(count)
            used_width = count * w
            # Center the row if exact division ever leaves room.
            x = max(0, (GRID_WIDTH - used_width) // 2)
            h = max(tile_height(tile_payload) for _, tile_payload in row_items)
            h = clamp(h, MIN_TILE_HEIGHT, MAX_TILE_HEIGHT)

            for key, _tile_payload in row_items:
                layouts[key] = {
                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h,
                }
                x += w

            y += h

        pending_data = []

    for key, tile_payload in ordered_items:
        if is_header_payload(tile_payload):
            # Headers start on a new row after any pending data in prior section.
            flush_data_rows()
            h = tile_height(tile_payload)
            layouts[key] = {
                "x": 0,
                "y": y,
                "w": GRID_WIDTH,
                "h": h,
            }
            y += h
        else:
            pending_data.append((key, tile_payload))

    flush_data_rows()
    return layouts


# =============================================================================
# Dashboard conversion
# =============================================================================


def convert_dashboard(
    classic_dashboard: Mapping[str, Any],
    metric_map: Mapping[str, str],
    omit_markdown: bool = False,
    omit_line_chart_settings: bool = False,
) -> Dict[str, Any]:
    """
    Return model-like dashboard CONTENT JSON.

    Important:
    - Tile/layout keys are ordinal strings starting with "1".
    - Layouts are computed after all tiles are created, so row packing can be
      section-aware and type-aware.
    """
    tiles: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
    next_key = 1

    def add_tile(tile_payload: Dict[str, Any]) -> None:
        nonlocal next_key

        if tile_payload:
            tiles[str(next_key)] = tile_payload
            next_key += 1

    for classic_tile in classic_dashboard.get("tiles", []):
        if not isinstance(classic_tile, Mapping):
            continue

        if is_markdown_like(classic_tile):
            if 'Overview' in str(classic_tile):
                print('Skipping Overview Tile!')
                continue

            if not omit_markdown:
                add_tile(markdown_tile_from_classic(classic_tile))
            continue

        # DEBUG:
        queries = extract_classic_queries(classic_tile)
        if not queries:
            print('DEBUG:', 'no queries...')
            continue

        print('DEBUG:', 'data_tile_from_classic being called')

        for index, query in enumerate(queries):
            add_tile(
                data_tile_from_classic(
                    classic_tile=classic_tile,
                    query=query,
                    metric_map=metric_map,
                    index=index,
                    omit_line_chart_settings=omit_line_chart_settings,
                )
            )

    layouts = build_section_aware_balanced_layouts(tiles)

    return {
        "version": MODEL_DASHBOARD_VERSION,
        "variables": [],
        "tiles": dict(tiles),
        "layouts": layouts,
    }


def output_file_name(classic_dashboard: Mapping[str, Any], source_path: Path) -> str:
    name = dashboard_name(classic_dashboard, source_path.stem)
    name = name.replace(':', ' - ')
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name).strip() or source_path.stem
    return f"{name}.json"


def find_unmapped_metrics(classic_dashboard: Mapping[str, Any], metric_map: Mapping[str, str]) -> List[str]:
    missing: List[str] = []
    for tile in classic_dashboard.get("tiles", []):
        if not isinstance(tile, Mapping):
            continue
        for query in extract_classic_queries(tile):
            metric = extract_metric_key_from_selector(str(query.get("metric") or ""))
            if metric and metric not in metric_map:
                missing.append(metric)
    return sorted(set(missing))


# =============================================================================
# CLI
# =============================================================================


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate model-like uploadable Gen3 dashboard JSON from classic dashboard JSON."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--metric-map", type=Path, default=DEFAULT_MAPPING_FILE)
    parser.add_argument("--fail-on-unmapped", action="store_true")
    parser.add_argument(
        "--omit-markdown",
        action="store_true",
        help="Do not emit HEADER/MARKDOWN tiles. Useful if the model contains data tiles only.",
    )
    parser.add_argument(
        "--omit-line-chart-settings",
        action="store_true",
        help="Omit visualizationSettings for non-TOP_LIST line charts if the model does not contain them.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    metric_map = build_metric_map(load_yaml(args.metric_map))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for source_path in iter_json_files(args.input):
        classic_dashboard = load_json(source_path)

        if args.fail_on_unmapped:
            missing = find_unmapped_metrics(classic_dashboard, metric_map)
            if missing:
                raise RuntimeError(f"Unmapped metrics in {source_path}: {', '.join(missing)}")

        generated = convert_dashboard(
            classic_dashboard=classic_dashboard,
            metric_map=metric_map,
            omit_markdown=args.omit_markdown,
            omit_line_chart_settings=args.omit_line_chart_settings,
        )

        output_path = args.output_dir / output_file_name(classic_dashboard, source_path)
        write_json(output_path, generated)
        print(f"Wrote {output_path} ({len(generated['tiles'])} tiles)")
        count += 1

    if UNMAPPED_METRICS:
        print("\n=== UNMAPPED METRICS ===")
        for m in sorted(UNMAPPED_METRICS):
            print(m)

    print(f"Processed {count} dashboard file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
