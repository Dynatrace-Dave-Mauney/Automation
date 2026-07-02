#!/usr/bin/env python3
from metric_selector_support import parse_metric_selector, metric_selector_to_dql

selector = 'builtin:tech.generic.cpu.usage:splitBy("dt.entity.process_group_instance"):avg:auto:parents:sort(value(avg,descending)):limit(10)'
print(parse_metric_selector(selector))
print()
print(metric_selector_to_dql(selector))
