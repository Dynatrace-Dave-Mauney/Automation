#!/usr/bin/env python3
"""
generate_gen3_dashboards.py

Convert Dynatrace Classic dashboard JSON files into Gen3 dashboard JSON documents.

Key behaviors implemented for the current migration workflow:
- Read one classic dashboard JSON file or every *.json file in a directory.
- Convert classic metric keys to Grail metric keys using classic_metric_to_grail_metric.yaml.
- Preserve dashboard/tile intent while emitting Gen3 dashboard document JSON.
- Convert classic TOP_LIST visualizations to Gen3 categoricalBarChart tiles.
- For TOP_LIST, aggregate the timeseries array with fieldsAdd, so categoricalBarChart receives scalar values.
- Set isValueLabelVisible = false.
- Set isCategoryLabelVisible = false.
- Hide the legend.

Typical usage from AI/Copilot/Dashboards/Generation:

python generate_gen3_dashboards.py \
  --input input_json/00000000-dddd-bbbb-ffff-000000000008.json \
  --output-dir generated_gen3 \
  --metric-map ../../../../NewPlatform/Dashboards/classic_metric_to_grail_metric.yaml

Or process all JSON files in input_json:

python generate_gen3_dashboards.py \
  --input input_json \
  --output-dir generated_gen3 \
  --metric-map ../../../../NewPlatform/Dashboards/classic_metric_to_grail_metric.yaml
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import yaml


GEN3_DASHBOARD_VERSION = 21
CLASSIC_GRID_PIXEL_SIZE = 38
GEN3_GRID_WIDTH = 24

DEFAULT_INPUT = Path("input_json")
DEFAULT_OUTPUT_DIR = Path("generated_gen3")
DEFAULT_MAPPING_FILE = Path("../../../../NewPlatform/Dashboards/classic_metric_to_grail_metric.yaml")


# -----------------------------------------------------------------------------
# File loading / writing
# -----------------------------------------------------------------------------


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


# -----------------------------------------------------------------------------
# Metric mapping
# -----------------------------------------------------------------------------


def build_metric_map(raw_mapping: Any) -> Dict[str, str]:
    """
    Accept several likely YAML shapes and normalize them to:
        {classic_metric_key: grail_metric_key}

    Supported examples:

    builtin:host.cpu.usage: dt.host.cpu.usage

    metrics:
      - classic: builtin:host.cpu.usage
        grail: dt.host.cpu.usage

    mappings:
      builtin:host.cpu.usage: dt.host.cpu.usage

    - classicMetric: builtin:host.cpu.usage
      grailMetric: dt.host.cpu.usage
    """
    mapping: Dict[str, str] = {}

    def add_pair(classic: Any, grail: Any) -> None:
        if classic is None or grail is None:
            return
        classic_text = str(classic).strip()
        grail_text = str(grail).strip()
        if classic_text and grail_text:
            mapping[classic_text] = grail_text

    def consume_dict(d: Mapping[str, Any]) -> None:
        # If the dictionary itself is a single mapping entry object.
        classic = (
            d.get("classic")
            or d.get("classicMetric")
            or d.get("classic_metric")
            or d.get("classicMetricKey")
            or d.get("classic_metric_key")
            or d.get("source")
            or d.get("from")
        )
        grail = (
            d.get("grail")
            or d.get("grailMetric")
            or d.get("grail_metric")
            or d.get("grailMetricKey")
            or d.get("grail_metric_key")
            or d.get("target")
            or d.get("to")
        )
        if classic and grail:
            add_pair(classic, grail)
            return

        # Otherwise treat simple scalar entries as direct mappings.
        for key, value in d.items():
            if key in {"metrics", "mappings", "metricMappings", "classicToGrail", "classic_to_grail"}:
                consume(value)
            elif isinstance(value, str):
                add_pair(key, value)
            elif isinstance(value, Mapping):
                # Common nested shape:
                # builtin:x:
                #   grail: dt.x
                nested_grail = (
                    value.get("grail")
                    or value.get("grailMetric")
                    or value.get("grail_metric")
                    or value.get("target")
                    or value.get("to")
                )
                if nested_grail:
                    add_pair(key, nested_grail)
                else:
                    consume_dict(value)
            elif isinstance(value, list):
                consume(value)

    def consume(value: Any) -> None:
        if isinstance(value, Mapping):
            consume_dict(value)
        elif isinstance(value, list):
            for item in value:
                consume(item)

    consume(raw_mapping)
    return mapping


def to_grail_metric(classic_metric: str, metric_map: Mapping[str, str]) -> str:
    """
    Convert a classic metric name to a Grail metric name.

    Primary behavior: exact lookup in classic_metric_to_grail_metric.yaml.
    Fallback behavior: conservative builtin: -> dt. plus camelCase-to-snake_case.
    This fallback is intentionally used only when the mapping file lacks an item.
    """
    if classic_metric in metric_map:
        return metric_map[classic_metric]

    # Some classic metric selectors have transformations appended. Extract the metric key.
    base_metric = extract_metric_key_from_selector(classic_metric)
    if base_metric in metric_map:
        return metric_map[base_metric]

    if base_metric.startswith("builtin:"):
        remainder = base_metric.removeprefix("builtin:")
        return "dt." + camel_to_snake_metric_path(remainder)

    # For extension/custom metrics, keep the metric as-is but DQL-escape later.
    return base_metric


def camel_to_snake_metric_path(value: str) -> str:
    parts = []
    for part in value.split("."):
        part = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", part)
        parts.append(part.lower())
    return ".".join(parts)


def extract_metric_key_from_selector(selector: str) -> str:
    """
    Best-effort extraction of the metric key from a classic metric selector.

    Examples:
      builtin:host.cpu.usage:splitBy("dt.entity.host") -> builtin:host.cpu.usage
      resolution=Inf&(builtin:host.cpu.usage:splitBy(...)) -> builtin:host.cpu.usage
    """
    if not selector:
        return selector

    match = re.search(r"(builtin:[A-Za-z0-9_.:-]+|ext:[A-Za-z0-9_.:-]+|calc:[A-Za-z0-9_.:-]+)", selector)
    if match:
        return match.group(1).rstrip(":")

    return selector.split(":splitBy", 1)[0].split(":filter", 1)[0].strip()


# -----------------------------------------------------------------------------
# Classic dashboard extraction
# -----------------------------------------------------------------------------


def dashboard_name(classic_dashboard: Mapping[str, Any], fallback: str) -> str:
    metadata = classic_dashboard.get("dashboardMetadata") or {}
    return (
        metadata.get("name")
        or classic_dashboard.get("name")
        or Path(fallback).stem
    )


def dashboard_description(classic_dashboard: Mapping[str, Any]) -> str:
    metadata = classic_dashboard.get("dashboardMetadata") or {}
    return metadata.get("description") or classic_dashboard.get("description") or ""


def iter_classic_json_files(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        yield input_path
        return

    for path in sorted(input_path.glob("*.json")):
        if path.name.startswith("."):
            continue
        yield path


def is_header_or_markdown(tile: Mapping[str, Any]) -> bool:
    tile_type = str(tile.get("tileType") or "").upper()
    return tile_type in {"HEADER", "MARKDOWN"}


def is_top_list(tile: Mapping[str, Any]) -> bool:
    visual_type = str((tile.get("visualConfig") or {}).get("type") or "").upper()
    chart_type = str(
        (((tile.get("filterConfig") or {}).get("chartConfig") or {}).get("type") or "")
    ).upper()
    return visual_type == "TOP_LIST" or chart_type == "TOP_LIST"


def classic_tile_title(tile: Mapping[str, Any], default: str = "") -> str:
    return (
        tile.get("customName")
        or tile.get("name")
        or tile.get("configuredName")
        or ((tile.get("filterConfig") or {}).get("customName"))
        or ((tile.get("filterConfig") or {}).get("defaultName"))
        or default
    )


def extract_classic_queries(tile: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """
    Return one or more classic metric query definitions from commonly emitted
    dashboard JSON structures.
    """
    queries = tile.get("queries")
    if isinstance(queries, list) and queries:
        return [q for q in queries if isinstance(q, Mapping) and q.get("metric")]

    # Classic custom chart shape: filterConfig.chartConfig.series may be dict or list.
    filter_config = tile.get("filterConfig") or {}
    chart_config = filter_config.get("chartConfig") or {}
    series = chart_config.get("series")

    if isinstance(series, Mapping) and series.get("metric"):
        return [dict(series)]

    if isinstance(series, list):
        return [dict(s) for s in series if isinstance(s, Mapping) and s.get("metric")]

    # Some classic DATA_EXPLORER exports include metricExpressions only.
    metric_expressions = tile.get("metricExpressions")
    if isinstance(metric_expressions, list):
        found = []
        for expression in metric_expressions:
            metric = extract_metric_key_from_selector(str(expression))
            if metric:
                found.append({"metric": metric})
        return found

    return []


def extract_split_by(query: Mapping[str, Any]) -> List[str]:
    split_by = query.get("splitBy") or query.get("dimensions") or []
    if isinstance(split_by, str):
        return [split_by]
    if isinstance(split_by, list):
        return [str(item) for item in split_by if str(item).strip()]
    return []


def extract_limit(query: Mapping[str, Any], tile: Mapping[str, Any], default: int = 20) -> int:
    for candidate in [query.get("limit"), tile.get("limit")]:
        if candidate is None:
            continue
        try:
            return int(candidate)
        except (TypeError, ValueError):
            pass
    return default


def extract_aggregation(query: Mapping[str, Any], tile: Mapping[str, Any]) -> str:
    """
    Classic dashboard values often include AUTO/DEFAULT. For DQL we want an
    explicit function. avg is the safest visual default for most line charts;
    count/sum style metrics can be adjusted in the mapping file or YAML later.
    """
    for key in ("aggregation", "timeAggregation", "spaceAggregation"):
        value = query.get(key)
        if value and str(value).upper() not in {"AUTO", "DEFAULT", "NONE"}:
            return normalize_aggregation(str(value))

    visual_type = str((tile.get("visualConfig") or {}).get("type") or "").upper()
    if visual_type == "SINGLE_VALUE":
        return "avg"

    return "avg"


def normalize_aggregation(value: str) -> str:
    normalized = value.strip().lower()
    aliases = {
        "average": "avg",
        "avg": "avg",
        "sum": "sum",
        "total": "sum",
        "min": "min",
        "max": "max",
        "count": "count",
        "median": "median",
        "percentile": "percentile",
    }
    return aliases.get(normalized, "avg")


# -----------------------------------------------------------------------------
# DQL generation
# -----------------------------------------------------------------------------


def dql_metric(metric_name: str) -> str:
    """DQL-escape metric names that are not plain identifiers."""
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", metric_name):
        return metric_name
    return "`" + metric_name.replace("`", "\\`") + "`"


def dql_dimension(dimension: str) -> str:
    """DQL dimensions are usually plain dotted identifiers; escape odd cases."""
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", dimension):
        return dimension
    return "`" + dimension.replace("`", "\\`") + "`"


def value_alias(grail_metric: str, query_index: int = 0) -> str:
    """
    Stable, readable alias for the timeseries value array.
    """
    last = grail_metric.split(".")[-1]
    alias = re.sub(r"[^A-Za-z0-9_]", "_", last).strip("_") or "value"
    if re.match(r"^\d", alias):
        alias = "value_" + alias
    if query_index:
        alias = f"{alias}_{query_index + 1}"
    return alias


def scalar_alias(array_alias: str) -> str:
    return f"{array_alias}_scalar"


def make_timeseries_query(
    grail_metric: str,
    aggregation: str,
    split_by: Sequence[str],
    top_list: bool,
    limit: int,
    query_index: int = 0,
) -> str:
    array_value = value_alias(grail_metric, query_index)
    metric_expr = dql_metric(grail_metric)

    query = f"timeseries {array_value} = {aggregation}({metric_expr})"

    if split_by:
        split_text = ", ".join(dql_dimension(str(item)) for item in split_by)
        query += f", by: {{{split_text}}}"

    if top_list:
        scalar_value = scalar_alias(array_value)
        category_fields = ", ".join(dql_dimension(str(item)) for item in split_by)
        query += f"\n| fieldsAdd {scalar_value} = arrayAvg({array_value})"
        if category_fields:
            query += f"\n| fieldsKeep {category_fields}, {scalar_value}"
        else:
            query += f"\n| fieldsKeep {scalar_value}"
        query += f"\n| sort {scalar_value} desc"
        query += f"\n| limit {limit}"

    return query


# -----------------------------------------------------------------------------
# Gen3 tile/document generation
# -----------------------------------------------------------------------------


def make_tile_id(prefix: str = "tile") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def make_markdown_tile(tile: Mapping[str, Any]) -> Dict[str, Any]:
    title = classic_tile_title(tile, "")
    markdown = tile.get("markdown") or tile.get("content") or title
    if title and not str(markdown).strip().startswith("#"):
        markdown = f"## {title}"
    return {
        "type": "markdown",
        "content": str(markdown or ""),
    }


def top_list_visualization_settings() -> Dict[str, Any]:
    """
    Keep the explicit settings requested for generated categoricalBarChart tiles.

    The additional nested keys are harmless for versions that use nested settings,
    while the top-level keys make the requested values obvious and easy to diff.
    """
    return {
        "isValueLabelVisible": False,
        "isCategoryLabelVisible": False,
        "legend": {
            "hidden": True,
        },
        "categoricalBarChart": {
            "isValueLabelVisible": False,
            "isCategoryLabelVisible": False,
        },
    }


def default_line_chart_settings() -> Dict[str, Any]:
    return {
        "legend": {
            "hidden": True,
        }
    }


def make_data_tile(
    classic_tile: Mapping[str, Any],
    query: Mapping[str, Any],
    metric_map: Mapping[str, str],
    query_index: int = 0,
) -> Dict[str, Any]:
    classic_metric = str(query.get("metric") or "").strip()
    grail_metric = to_grail_metric(classic_metric, metric_map)
    split_by = extract_split_by(query)
    top_list = is_top_list(classic_tile)
    limit = extract_limit(query, classic_tile)
    aggregation = extract_aggregation(query, classic_tile)

    title = classic_tile_title(classic_tile, grail_metric)
    if query_index:
        title = f"{title} - {query_index + 1}"

    visualization = "categoricalBarChart" if top_list else "lineChart"
    dql_query = make_timeseries_query(
        grail_metric=grail_metric,
        aggregation=aggregation,
        split_by=split_by,
        top_list=top_list,
        limit=limit,
        query_index=query_index,
    )

    tile: Dict[str, Any] = {
        "type": "data",
        "title": title,
        "query": dql_query,
        "visualization": visualization,
        "visualizationSettings": (
            top_list_visualization_settings() if top_list else default_line_chart_settings()
        ),
        "querySettings": {},
    }

    return tile


def classic_bounds_to_gen3_layout(tile: Mapping[str, Any], fallback_y: int) -> Dict[str, int]:
    bounds = tile.get("bounds") or {}

    if not bounds:
        return {"x": 0, "y": fallback_y, "w": 12, "h": 8}

    left = int(round(float(bounds.get("left", 0)) / CLASSIC_GRID_PIXEL_SIZE))
    top = int(round(float(bounds.get("top", fallback_y * CLASSIC_GRID_PIXEL_SIZE)) / CLASSIC_GRID_PIXEL_SIZE))
    width = max(1, int(round(float(bounds.get("width", 12 * CLASSIC_GRID_PIXEL_SIZE)) / CLASSIC_GRID_PIXEL_SIZE)))
    height = max(1, int(round(float(bounds.get("height", 8 * CLASSIC_GRID_PIXEL_SIZE)) / CLASSIC_GRID_PIXEL_SIZE)))

    # Gen3 grid is 24 units wide. Clamp without destroying relative placement.
    x = max(0, min(left, GEN3_GRID_WIDTH - 1))
    w = max(1, min(width, GEN3_GRID_WIDTH - x))

    return {
        "x": x,
        "y": max(0, top),
        "w": w,
        "h": height,
    }


def convert_classic_dashboard(
    classic_dashboard: Mapping[str, Any],
    source_name: str,
    metric_map: Mapping[str, str],
) -> Dict[str, Any]:
    tiles: Dict[str, Dict[str, Any]] = {}
    layouts: Dict[str, Dict[str, int]] = {}

    fallback_y = 0

    for classic_tile in classic_dashboard.get("tiles", []):
        if not isinstance(classic_tile, Mapping):
            continue

        if is_header_or_markdown(classic_tile):
            tile_id = make_tile_id("markdown")
            tiles[tile_id] = make_markdown_tile(classic_tile)
            layouts[tile_id] = classic_bounds_to_gen3_layout(classic_tile, fallback_y)
            fallback_y = max(fallback_y, layouts[tile_id]["y"] + layouts[tile_id]["h"])
            continue

        classic_queries = extract_classic_queries(classic_tile)
        if not classic_queries:
            continue

        for index, query in enumerate(classic_queries):
            tile_id = make_tile_id("data")
            tiles[tile_id] = make_data_tile(
                classic_tile=classic_tile,
                query=query,
                metric_map=metric_map,
                query_index=index,
            )
            layouts[tile_id] = classic_bounds_to_gen3_layout(classic_tile, fallback_y)

            # If a classic tile has multiple metrics, cascade generated tiles vertically.
            if index:
                layouts[tile_id]["y"] += index * layouts[tile_id]["h"]

            fallback_y = max(fallback_y, layouts[tile_id]["y"] + layouts[tile_id]["h"])

    return {
        "name": dashboard_name(classic_dashboard, source_name),
        "description": dashboard_description(classic_dashboard),
        "type": "dashboard",
        "content": {
            "version": GEN3_DASHBOARD_VERSION,
            "variables": [],
            "tiles": tiles,
            "layouts": layouts,
        },
    }


def output_file_name(classic_dashboard: Mapping[str, Any], source_path: Path) -> str:
    name = dashboard_name(classic_dashboard, source_path.stem)
    cleaned = re.sub(r"[\\/:*?\"<>|]+", "_", name).strip() or source_path.stem
    return f"{cleaned}.json"


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert classic Dynatrace dashboard JSON into Gen3 dashboard document JSON."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Classic dashboard JSON file or directory of *.json files. Default: input_json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for generated Gen3 dashboard JSON. Default: generated_gen3",
    )
    parser.add_argument(
        "--metric-map",
        type=Path,
        default=DEFAULT_MAPPING_FILE,
        help="YAML file mapping classic metric keys to Grail metric keys.",
    )
    parser.add_argument(
        "--fail-on-unmapped",
        action="store_true",
        help="Fail if a classic metric is not found in the mapping file.",
    )
    return parser.parse_args(argv)


def find_unmapped_metrics(classic_dashboard: Mapping[str, Any], metric_map: Mapping[str, str]) -> List[str]:
    unmapped: List[str] = []
    for tile in classic_dashboard.get("tiles", []):
        if not isinstance(tile, Mapping):
            continue
        for query in extract_classic_queries(tile):
            metric = str(query.get("metric") or "").strip()
            base_metric = extract_metric_key_from_selector(metric)
            if base_metric and base_metric not in metric_map:
                unmapped.append(base_metric)
    return sorted(set(unmapped))


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    metric_map = build_metric_map(load_yaml(args.metric_map))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    processed = 0

    for source_path in iter_classic_json_files(args.input):
        classic_dashboard = load_json(source_path)

        if args.fail_on_unmapped:
            unmapped = find_unmapped_metrics(classic_dashboard, metric_map)
            if unmapped:
                raise RuntimeError(
                    f"Unmapped metrics in {source_path}: " + ", ".join(unmapped)
                )

        gen3_dashboard = convert_classic_dashboard(
            classic_dashboard=classic_dashboard,
            source_name=source_path.name,
            metric_map=metric_map,
        )

        out_path = args.output_dir / output_file_name(classic_dashboard, source_path)
        write_json(out_path, gen3_dashboard)

        data_tile_count = sum(
            1
            for tile in gen3_dashboard["content"]["tiles"].values()
            if tile.get("type") == "data"
        )
        print(f"Wrote {out_path} ({data_tile_count} data tiles)")
        processed += 1

    print(f"Processed {processed} dashboard file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
