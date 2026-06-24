import json
import yaml
from pathlib import Path
from collections import defaultdict


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_header_tile(tile):
    """
    Detect section/group headers.
    """
    if tile.get("tileType") == "HEADER":
        return True
    if tile.get("tileType") == "MARKDOWN":
        content = tile.get("markdown", "").lower()
        return content.strip().startswith("#")
    return False


def extract_metric_from_tile(tile):
    """
    Extract metric name from common classic dashboard structures.
    """
    # DATA_EXPLORER tiles
    queries = tile.get("queries", [])
    if queries:
        metric = queries[0].get("metric")
        if metric:
            return metric

    # Custom chart tiles
    filter_config = tile.get("filterConfig", {})
    chart_config = filter_config.get("chartConfig", {})
    series = chart_config.get("series", {})
    if isinstance(series, dict):
        metric = series.get("metric")
        if metric:
            return metric

    return None


def extract_split_by(tile):
    queries = tile.get("queries", [])
    if queries:
        return queries[0].get("splitBy", [])
    return []


def extract_tile(tile):
    """
    Distill a tile down to YAML-friendly form.
    """
    distilled = {}

    title = (
        tile.get("customName")
        or tile.get("name")
        or tile.get("configuredName")
        or ""
    )

    if title:
        distilled["title"] = title

    distilled["type"] = tile.get("tileType")

    metric = extract_metric_from_tile(tile)
    if metric:
        distilled["metric"] = metric

    split_by = extract_split_by(tile)
    if split_by:
        distilled["splitBy"] = split_by

    return distilled


def process_dashboard(json_path):
    data = load_json(json_path)

    result = {
        "name": data.get("dashboardMetadata", {}).get("name"),
        "tiles": []
    }

    tiles = data.get("tiles", [])

    groups = defaultdict(list)
    current_group = "Ungrouped"

    for tile in tiles:
        if is_header_tile(tile):
            current_group = tile.get("name") or tile.get("customName") or "Group"
            continue

        distilled_tile = extract_tile(tile)

        if distilled_tile:
            groups[current_group].append(distilled_tile)

    # convert grouped structure
    result["groups"] = []
    for group, items in groups.items():
        result["groups"].append({
            "name": group,
            "tiles": items
        })

    return result


def extract_directory(input_dir):
    dashboards_yaml = []

    for file in Path(input_dir).glob("*.json"):
        try:
            if '-v' in str(file) or 'markdown' in str(file):
                continue
            print(f'Processing {file}')
            dashboards_yaml.append(process_dashboard(file))
        except Exception as e:
            print(f"Skipping {file}: {e}")

    return {"dashboards": dashboards_yaml}


def write_yaml(data, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            sort_keys=False,
            default_flow_style=False
        )


# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":
    INPUT_DIR = "../../../../Dashboards/Templates/Overview"
    OUTPUT_FILE = "dashboard_extract.yaml"

    extracted = extract_directory(INPUT_DIR)
    write_yaml(extracted, OUTPUT_FILE)

    print(f"YAML written to {OUTPUT_FILE}")