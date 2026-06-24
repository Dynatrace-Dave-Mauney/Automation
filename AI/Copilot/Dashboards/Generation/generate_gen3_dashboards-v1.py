# generate_gen3_dashboards.py
import yaml
import json
import uuid
from pathlib import Path


def tile_id():
    return f"tile-{uuid.uuid4().hex[:8]}"


def create_query(metric):
    metric_name = metric["metric"]
    agg = metric.get("aggregation", "avg")

    query = f"timeseries value = {agg}(`{metric_name}`)"

    if metric.get("splitBy"):
        query += f", by: {{{metric['splitBy']}}}"

    return query


def generate_dashboard(dashboard, output_dir):
    tiles = {}
    layouts = {}

    x, y = 0, 0
    width = 12
    height = 8

    for group in dashboard["groups"]:
        # header tile
        header_id = tile_id()
        tiles[header_id] = {
            "type": "markdown",
            "content": f"## {group['name']}"
        }
        layouts[header_id] = {"x": 0, "y": y, "w": 24, "h": 2}
        y += 2

        for metric in group["metrics"]:
            t_id = tile_id()

            tiles[t_id] = {
                "type": "data",
                "title": metric["metric"],
                "query": create_query(metric),
                "visualization": "lineChart"
            }

            layouts[t_id] = {
                "x": x,
                "y": y,
                "w": width,
                "h": height
            }

            x += width
            if x >= 24:
                x = 0
                y += height

        y += height
        x = 0

    document = {
        "name": dashboard["name"],
        "type": "dashboard",
        "content": {
            "version": 21,
            "tiles": tiles,
            "layouts": layouts
        }
    }

    file_path = Path(output_dir) / f"{dashboard['name'].replace(' ', '_')}.json"

    with open(file_path, "w") as f:
        json.dump(document, f, indent=2)


def generate_all(input_yaml, output_dir):
    Path(output_dir).mkdir(exist_ok=True)

    with open(input_yaml) as f:
        data = yaml.safe_load(f)

    for dashboard in data["dashboards"]:
        generate_dashboard(dashboard, output_dir)


if __name__ == "__main__":
    generate_all(
        "canonical/normalized.yaml",
        "generated_gen3"
    )