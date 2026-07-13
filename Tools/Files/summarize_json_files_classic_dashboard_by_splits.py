import os
import glob
import json
import re


def main():
    selected_count = 0
    try:
        input_glob_pattern = "../../Dashboards/Templates/Overview/0*.json"

        for file_name in glob.glob(input_glob_pattern, recursive=True):
            if os.path.isfile(file_name) and file_name.endswith('.json'):
                with open(file_name, 'r', encoding='utf-8') as infile:
                    input_json = json.loads(infile.read())
                    formatted_json = json.dumps(input_json, indent=4, sort_keys=False)
                    dashboard_metadata = input_json.get('dashboardMetadata')
                    if dashboard_metadata:
                        dashboard_name = dashboard_metadata.get('name')
                        dashboard_id = input_json.get('id')
                        dashboard_tiles = input_json.get('tiles')
                        for dashboard_tile in dashboard_tiles:
                            dashboard_tile_type = dashboard_tile.get('tileType')

                            # Report metrics that have "By" in the tile name
                            # if 'By' in dashboard_tile_name or 'By' in dashboard_tile_custom_name:
                            #     if 'Byte' not in dashboard_tile_name and 'Byte' not in dashboard_tile_custom_name:
                            #         dashboard_tile_metric_expressions = dashboard_tile.get('metricExpressions')
                            #         if dashboard_tile_metric_expressions:
                            #             dashboard_tile_metric_expression = dashboard_tile_metric_expressions[0]
                            #         dashboard_tile_queries = dashboard_tile.get('queries')
                            #         if dashboard_tile_queries and dashboard_tile_metric_expression:
                            #             dashboard_tile_queries_metric = dashboard_tile_queries[0].get('metric')
                            #             dashboard_tile_queries_split_by = dashboard_tile_queries[0].get('splitBy')
                            #             # print(dashboard_tile)
                            #             print(dashboard_tile_queries_metric, dashboard_tile_name,
                            #                   dashboard_tile_queries_split_by, dashboard_tile_metric_expression)
                            #             # print(dashboard_id, dashboard_name, dashboard_tile_name, dashboard_tile_custom_name, dashboard_tile_queries_metric, dashboard_tile_queries_split_by, dashboard_tile_metric_expression)
                            #             selected_count += 1

                            # Report metrics that have "By" in the metric name
                            if dashboard_tile_type == 'DATA_EXPLORER':
                                dashboard_tile_name = dashboard_tile.get('name')
                                dashboard_tile_custom_name = dashboard_tile.get('customName')
                                # Report metrics that have "By" in the tile name
                                dashboard_tile_metric_expressions = dashboard_tile.get('metricExpressions')
                                if dashboard_tile_metric_expressions:
                                    dashboard_tile_metric_expression = dashboard_tile_metric_expressions[0]
                                else:
                                    dashboard_tile_metric_expression = ''
                                dashboard_tile_queries = dashboard_tile.get('queries')

                                if not dashboard_tile_queries:
                                    dashboard_tile_queries = [{}]

                                match = re.search(r"splitBy\((.+?)\)", dashboard_tile_metric_expression)
                                if match:
                                    inner_content = match.group(1)
                                    inner_content = inner_content.replace('"', '')
                                    result = inner_content.split(",")
                                    tile_metric_expressions_split_by = result
                                else:
                                    tile_metric_expressions_split_by = None

                                if dashboard_tile_queries or dashboard_tile_metric_expression:
                                    dashboard_tile_queries_metric = dashboard_tile_queries[0].get('metric')
                                    dashboard_tile_queries_split_by = dashboard_tile_queries[0].get('splitBy')

                                    if dashboard_tile_queries_metric and 'by' in dashboard_tile_queries_metric.lower() and 'byte' not in dashboard_tile_queries_metric.lower():
                                        # print(dashboard_tile_queries_metric)
                                        if tile_metric_expressions_split_by and dashboard_tile_queries_split_by:
                                            if 'By' in dashboard_tile_queries_metric:
                                                dashboard_tile_queries_metric_by_string = dashboard_tile_queries_metric.split("By")[1]
                                            else:
                                                dashboard_tile_queries_metric_by_string = dashboard_tile_queries_metric.split("by")[1]

                                            me_by = "".join(tile_metric_expressions_split_by).replace(" ", "")
                                            qs_by = "".join(dashboard_tile_queries_split_by).replace(" ", "")

                                            if me_by == '':
                                                me_by = qs_by

                                            if qs_by == '':
                                                qs_by = me_by

                                            if not (me_by == qs_by == dashboard_tile_queries_metric_by_string):
                                                # print(dashboard_id, dashboard_tile_queries_metric, dashboard_tile_queries_metric_by_string, "".join(tile_metric_expressions_split_by).replace(" ", ""), "".join(dashboard_tile_queries_split_by).replace(" ", ""))
                                                print(dashboard_id, dashboard_tile_queries_metric, dashboard_tile_queries_metric_by_string, me_by, qs_by)
                                                selected_count += 1

                                # Check if metric expression splitBy does not match the metric splits.
                                # Found some minor name mismatches only...
                                # match = re.search(r"splitBy\((.+?)\)", dashboard_tile_metric_expression)
                                # if match:
                                #     inner_content = match.group(1)
                                #     inner_content = inner_content.replace('"', '')
                                #     result = inner_content.split(",")
                                #     tile_metric_expressions_split_by = result
                                # else:
                                #     tile_metric_expressions_split_by = None
                                #
                                # if dashboard_tile_queries or dashboard_tile_metric_expression:
                                #     dashboard_tile_queries_metric = dashboard_tile_queries[0].get('metric')
                                #     dashboard_tile_queries_split_by = dashboard_tile_queries[0].get('splitBy')
                                #
                                #     if tile_metric_expressions_split_by and dashboard_tile_queries_split_by:
                                #         if tile_metric_expressions_split_by != dashboard_tile_queries_split_by:
                                #             print(dashboard_id, dashboard_tile_queries_metric, tile_metric_expressions_split_by, dashboard_tile_queries_split_by)
                                #             selected_count += 1

                                    # print(dashboard_tile)
                                    # print(dashboard_id, dashboard_tile_queries_metric, dashboard_tile_name, dashboard_tile_queries_split_by, dashboard_tile_metric_expression)
                                    # print(dashboard_id, dashboard_name, dashboard_tile_name, dashboard_tile_custom_name, dashboard_tile_queries_metric, dashboard_tile_queries_split_by, dashboard_tile_metric_expression)

                                # if dashboard_tile_queries or dashboard_tile_metric_expression:
                                #     dashboard_tile_queries_metric = dashboard_tile_queries[0].get('metric')
                                #     dashboard_tile_queries_split_by = dashboard_tile_queries[0].get('splitBy')
                                #     # print(dashboard_tile)
                                #     print(dashboard_id, dashboard_tile_queries_metric, dashboard_tile_name, dashboard_tile_queries_split_by, dashboard_tile_metric_expression)
                                #     # print(dashboard_id, dashboard_name, dashboard_tile_name, dashboard_tile_custom_name, dashboard_tile_queries_metric, dashboard_tile_queries_split_by, dashboard_tile_metric_expression)
                                #     selected_count += 1
    except FileNotFoundError:
        print('The directory name does not exist')

    print(f'Total Selected: {selected_count}')


if __name__ == '__main__':
    main()
