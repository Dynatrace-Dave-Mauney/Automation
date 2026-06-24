# normalize_yaml.py
import yaml


def normalize(input_file, output_file):
    with open(input_file) as f:
        data = yaml.safe_load(f)

    for dashboard in data["dashboards"]:
        for group in dashboard["groups"]:
            for metric in group["metrics"]:
                metric.setdefault("aggregation", "avg")

    with open(output_file, "w") as f:
        yaml.dump(data, f, sort_keys=False)


if __name__ == "__main__":
    normalize(
        "output_yaml/extracted.yaml",
        "canonical/normalized.yaml")
