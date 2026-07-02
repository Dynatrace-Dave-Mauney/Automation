#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python apply_metricselector_support.py /path/to/AI/Copilot/Dashboards/Generation")
        return 2

    target_dir = Path(sys.argv[1]).expanduser().resolve()
    target_file = target_dir / "generate_gen3_dashboards.py"
    helper_src = Path(__file__).with_name("metric_selector_support.py")
    helper_dst = target_dir / "metric_selector_support.py"

    if not target_file.exists():
        print(f"ERROR: {target_file} does not exist")
        return 1
    if not helper_src.exists():
        print(f"ERROR: {helper_src} does not exist")
        return 1

    shutil.copy2(helper_src, helper_dst)
    print(f"Copied helper to: {helper_dst}")
    print("\nImport in generate_gen3_dashboards.py:")
    print("    from metric_selector_support import metric_selector_to_dql, find_metric_selectors")
    print("\nIntegration block for the classic-tile -> Gen3 query path:")
    print("    metric_selectors = find_metric_selectors(classic_tile)")
    print("    if metric_selectors:")
    print("        dql = metric_selector_to_dql(metric_selectors[0], metric_mapping=classic_metric_to_grail_metric)")
    print("        # pass dql to your existing Gen3 DQL tile factory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
