#!/usr/bin/env python3
"""
generate_gen3_dashboards.py

Classic Dynatrace dashboard JSON -> uploadable Gen3 dashboard JSON.

This version intentionally emits the dashboard CONTENT shape, not the broader
Document API wrapper. In practice, uploading a file with extra top-level document
fields can result in a dashboard that imports but has no usable tiles. The output
is therefore kept close to the model dashboard export:

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

Design goals:
- Use ordinal tile/layout keys starting with "1".
- Remove extraneous fields.
- Keep per-tile fields minimal and model-like.
- Convert classic metrics to Grail metrics using classic_metric_to_grail_metric.yaml.
- Convert classic TOP_LIST tiles to categoricalBarChart.
- Use fieldsAdd to create a scalar aggregation from the timeseries array.
- Set isValueLabelVisible = false.
- Set isCategoryLabelVisible = false.
- Set legend.hidden = true.

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
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import yaml


MODEL_DASHBOARD_VERSION = 21
CLASSIC_GRID_PIXEL_SIZE = 38
GEN3_GRID_WIDTH = 24

DEFAULT_INPUT = Path("input_json")
DEFAULT_OUTPUT_DIR = Path("generated_gen3")
DEFAULT_MAPPING_FILE = Path("../../../../NewPlatform/Dashboards/classic_metric_to_grail_metric.yaml")


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
    Normalize multiple plausible YAML mapping shapes into:
      {classic_metric: grail_metric}

    Supported shapes include:
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


def to_grail_metric(classic_metric_or_selector: str, metric_map: Mapping[str, str]) -> str:
    """Use explicit mapping first, fallback to conservative builtin: -> dt conversion."""
    if classic_metric_or_selector in metric_map:
        return metric_map[classic_metric_or_selector]

    base_metric = extract_metric_key_from_selector(classic_metric_or_selector)
    if base_metric in metric_map:
        return metric_map[base_metric]

    if base_metric.startswith("builtin:"):
        return "dt." + camel_to_snake_metric_path(base_metric.removeprefix("builtin:"))

    return base_metric


# =============================================================================
# Classic tile extraction
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
    queries = tile.get("queries")
    if isinstance(queries, list) and queries:
        return [dict(q) for q in queries if isinstance(q, Mapping) and q.get("metric")]

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
    Return a DQL aggregation. The common classic values AUTO/DEFAULT do not map
    directly, so default to avg unless a specific aggregation is present.
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
    # Metric names with dt.* are valid dotted identifiers; extension/custom names
    # can contain characters that require escaping.
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
# Model-like Gen3 output
# =============================================================================


def markdown_tile_from_classic(tile: Mapping[str, Any]) -> Dict[str, Any]:
    title = tile_title(tile)
    content = tile.get("markdown") or tile.get("content") or title
    if title and not str(content).lstrip().startswith("#"):
        content = f"## {title}"
    # Keep only model-essential fields.
    return {
        "type": "markdown",
        "content": str(content or ""),
    }


def categorical_bar_chart_settings() -> Dict[str, Any]:
    # Deliberately minimal and directly aligned with the requested model behavior.
    return {
        "legend": {
            "hidden": True
        },
        "isValueLabelVisible": False,
        "isCategoryLabelVisible": False
    }


def line_chart_settings() -> Dict[str, Any]:
    # Keep minimal. If the model omits visualizationSettings for line charts,
    # pass --omit-line-chart-settings to remove this entirely.
    return {
        "legend": {
            "hidden": True
        }
    }


def data_tile_from_classic(
    classic_tile: Mapping[str, Any],
    query: Mapping[str, Any],
    metric_map: Mapping[str, str],
    index: int,
    omit_line_chart_settings: bool,
) -> Dict[str, Any]:
    classic_metric = str(query.get("metric") or "").strip()
    grail_metric = to_grail_metric(classic_metric, metric_map)
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


def classic_layout(tile: Mapping[str, Any], fallback_y: int) -> Dict[str, int]:
    bounds = tile.get("bounds") or {}
    if not bounds:
        return {"x": 0, "y": fallback_y, "w": 12, "h": 8}

    x = int(round(float(bounds.get("left", 0)) / CLASSIC_GRID_PIXEL_SIZE))
    y = int(round(float(bounds.get("top", fallback_y * CLASSIC_GRID_PIXEL_SIZE)) / CLASSIC_GRID_PIXEL_SIZE))
    w = int(round(float(bounds.get("width", 12 * CLASSIC_GRID_PIXEL_SIZE)) / CLASSIC_GRID_PIXEL_SIZE))
    h = int(round(float(bounds.get("height", 8 * CLASSIC_GRID_PIXEL_SIZE)) / CLASSIC_GRID_PIXEL_SIZE))

    x = max(0, min(x, GEN3_GRID_WIDTH - 1))
    w = max(1, min(max(1, w), GEN3_GRID_WIDTH - x))
    return {"x": x, "y": max(0, y), "w": w, "h": max(1, h)}


def convert_dashboard(
    classic_dashboard: Mapping[str, Any],
    metric_map: Mapping[str, str],
    omit_markdown: bool = False,
    omit_line_chart_settings: bool = False,
) -> Dict[str, Any]:
    """
    Return model-like dashboard CONTENT JSON.

    Important: keys are ordinal strings starting with "1" for both tiles and layouts.
    """
    tiles: Dict[str, Dict[str, Any]] = {}
    layouts: Dict[str, Dict[str, int]] = {}

    next_key = 1
    fallback_y = 0

    def add_tile(tile_payload: Dict[str, Any], layout_payload: Dict[str, int]) -> None:
        nonlocal next_key, fallback_y
        key = str(next_key)
        tiles[key] = tile_payload
        layouts[key] = layout_payload
        fallback_y = max(fallback_y, layout_payload["y"] + layout_payload["h"])
        next_key += 1

    for classic_tile in classic_dashboard.get("tiles", []):
        if not isinstance(classic_tile, Mapping):
            continue

        if is_markdown_like(classic_tile):
            if not omit_markdown:
                add_tile(markdown_tile_from_classic(classic_tile), classic_layout(classic_tile, fallback_y))
            continue

        queries = extract_classic_queries(classic_tile)
        if not queries:
            continue

        for index, query in enumerate(queries):
            layout = classic_layout(classic_tile, fallback_y)
            if index:
                layout = dict(layout)
                layout["y"] += index * layout["h"]
            add_tile(
                data_tile_from_classic(
                    classic_tile=classic_tile,
                    query=query,
                    metric_map=metric_map,
                    index=index,
                    omit_line_chart_settings=omit_line_chart_settings,
                ),
                layout,
            )

    # Keep top level sparse and model-like. No name/type/description/content wrapper.
    return {
        "version": MODEL_DASHBOARD_VERSION,
        "variables": [],
        "tiles": tiles,
        "layouts": layouts,
    }


def output_file_name(classic_dashboard: Mapping[str, Any], source_path: Path) -> str:
    name = dashboard_name(classic_dashboard, source_path.stem)
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

    print(f"Processed {count} dashboard file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
