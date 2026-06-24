# extract_json_to_yaml.py
import json
import yaml
from pathlib import Path
from collections import defaultdict


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_header(tile):
    return tile.get("tileType") == "HEADER"


def extract_metric(tile):
    queries = tile.get("queries", [])
    if queries:
        return queries[0].get("metric")

    series = tile.get("filterConfig", {}).get("chartConfig", {}).get("series", {})
    if isinstance(series, dict):
        return series.get("metric")

    return None


def extract_split_by(tile):
    queries = tile.get("queries", [])
    if queries:
        return queries[0].get("splitBy", [])
    return []


def process_dashboard(path):
    data = load_json(path)
    tiles = data.get("tiles", [])

    current_group = "Ungrouped"
    groups = defaultdict(list)

    for tile in tiles:
        if is_header(tile):
            current_group = tile.get("name")
            continue

        metric = extract_metric(tile)
        if not metric:
            continue

        groups[current_group].append({
            "metric": metric,
            "splitBy": extract_split_by(tile)[0] if extract_split_by(tile) else None
        })

    return {
        "name": data.get("dashboardMetadata", {}).get("name"),
        "groups": [
            {
                "name": group,
                "metrics": metrics
            } for group, metrics in groups.items()
        ]
    }


def extract_all(input_dir, output_file):
    dashboards = []
    for file in Path(input_dir).glob("*.json"):
        dashboards.append(process_dashboard(file))

    with open(output_file, "w") as f:
        yaml.dump({"dashboards": dashboards}, f, sort_keys=False)


if __name__ == "__main__":
    extract_all("input_json", "output_yaml/extracted.yaml")
