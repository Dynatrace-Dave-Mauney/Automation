import copy
import glob
import json
import os

verbose = False

OLD_DASHBOARD_PATH = '../$Test/Dashboards/CustomCharts'
NEW_DASHBOARD_PATH = '../$Test/Dashboards/DataExplorer'

NEW_TILE_TEMPLATE = '''{
      "name": "$$NAME$$",
      "tileType": "DATA_EXPLORER",
      "configured": true,
      "bounds": {
        "top": $$TOP$$,
        "left": $$LEFT$$,
        "width": $$WIDTH$$,
        "height": $$HEIGHT$$
      },
      "tileFilter": {},
      "customName": "$$NAME$$",
      "queries": $$QUERIES$$,
      "visualConfig": {
        "type": "$$VISUAL_TYPE$$",
        "global": {
          "theme": "DEFAULT",
          "threshold": {
            "axisTarget": "LEFT",
            "rules": [
              {
                "color": "#7dc540"
              },
              {
                "color": "#f5d30f"
              },
              {
                "color": "#dc172a"
              }
            ],
            "visible": true
          },
          "seriesType": "$$SERIES_TYPE$$",
          "hideLegend": $$HIDE_LEGEND$$
        },
        "rules": [],
        "axes": {
          "xAxis": {
            "displayName": "",
            "visible": true
          },
          "yAxes": [
            {
              "displayName": "",
              "visible": true,
              "min": "AUTO",
              "max": "AUTO",
              "position": "LEFT",
              "queryIds": [
                "A"
              ],
              "defaultAxis": true
            }
          ]
        },
        "thresholds": [
          {
            "axisTarget": "LEFT",
            "rules": [
              {
                "color": "#7dc540"
              },
              {
                "color": "#f5d30f"
              },
              {
                "color": "#dc172a"
              }
            ],
            "visible": true
          }
        ]
      }
    }
'''

QUERIES_TEMPLATE = '''        {
          "id": "$$ID$$",
          "metric": "$$METRIC$$",
          "spaceAggregation": "$$AGG$$",
          "timeAggregation": "DEFAULT",
          "splitBy": $$SPLIT$$,
          "filterBy": {
            "filterOperator": "AND",
            "nestedFilters": $$NESTED_FILTERS$$,
            "criteria": []
          },
          "enabled": true
        }'''

NO_NESTED_FILTER = '[]'

DATABASE_NESTED_FILTER = '''[
              {
                "filter": "dt.entity.service",
                "filterType": "ENTITY_ATTRIBUTE",
                "filterOperator": "OR",
                "entityAttribute": "servicetype",
                "nestedFilters": [],
                "criteria": [
                  {
                    "value": "DATABASE_SERVICE",
                    "evaluator": "IN"
                  }
                ]
              }
            ]'''

ID_LIST = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']


def convert_dashboards():
    for filename in glob.glob(OLD_DASHBOARD_PATH + '/*'):
        with open(filename, 'r', encoding='utf-8') as f:
            if verbose:
                print(filename)
            dashboard = f.read()
            new_dashboard = convert_custom_charts(dashboard)
            pretty_new_dashboard = json.dumps(new_dashboard, indent=4, sort_keys=False)
            # (pretty_new_dashboard)
            output_filename = NEW_DASHBOARD_PATH + '/' + os.path.basename(filename)
            if verbose:
                print(output_filename)
            with open(output_filename, 'w') as outfile:
                outfile.write(pretty_new_dashboard)


def convert_custom_charts(dashboard):
    dashboard_json = json.loads(dashboard)
    new_dashboard_json = copy.deepcopy(dashboard_json)
    tiles = []
    for tile in new_dashboard_json.get('tiles'):
        if tile.get('tileType') == 'CUSTOM_CHARTING':
            top = tile.get('bounds').get('top')
            left = tile.get('bounds').get('left')
            width = tile.get('bounds').get('width')
            height = tile.get('bounds').get('height')
            name = tile.get('filterConfig').get('customName')

            # Fix broken name: Invocations Sum \'default\" Event Bus (By Region and RuleName)
            # It has mismatched quote types
            name = name.replace("'default\"", "'default'")

            # Multiple series implementation
            series = tile.get('filterConfig').get('chartConfig').get('series')
            new_series = '['
            i = 0
            for series_item in series:
                metric = series_item.get('metric')
                aggregation = series_item.get('aggregation')
                if aggregation == 'NONE':
                    aggregation = 'AVG'
                if aggregation == 'PERCENTILE':
                    aggregation = 'MEDIAN'
                if aggregation == 'SUM_DIMENSIONS':
                    aggregation = 'SUM'
                dimensions = series_item.get('dimensions')
                new_dimensions = []
                for dimension in dimensions:
                    split = dimension.get('name')
                    new_dimensions.append(split)
                new_series_item = QUERIES_TEMPLATE.replace('$$ID$$', ID_LIST[i])
                new_series_item = new_series_item.replace('$$METRIC$$', metric)
                new_series_item = new_series_item.replace('$$AGG$$', aggregation)
                filter_service_type = tile.get('filterConfig').get('filtersPerEntityType').get('SERVICE', {}).get(
                    'SERVICE_TYPE', ['X'])
                if filter_service_type == ['3']:
                    new_series_item = new_series_item.replace('$$NESTED_FILTERS$$', DATABASE_NESTED_FILTER)
                else:
                    new_series_item = new_series_item.replace('$$NESTED_FILTERS$$', NO_NESTED_FILTER)
                split = '['
                j = 0
                for dim in new_dimensions:
                    if dim:
                        if j > 0:
                            split += ' ,'
                        split += '"' + dim + '"'
                        j += 1
                split += ']'
                new_series_item = new_series_item.replace('$$SPLIT$$', split)
                if i > 0:
                    new_series += ' ,'
                new_series += new_series_item
                i += 1
            new_series += ']'

            visual_type = tile.get('filterConfig').get('chartConfig').get('type')
            legend_shown = tile.get('filterConfig').get('chartConfig').get('legendShown')
            tile_string = NEW_TILE_TEMPLATE.replace('$$TOP$$', str(top))
            tile_string = tile_string.replace('$$LEFT$$', str(left))
            tile_string = tile_string.replace('$$WIDTH$$', str(width))
            tile_string = tile_string.replace('$$HEIGHT$$', str(height))
            tile_string = tile_string.replace('$$NAME$$', name)
            tile_string = tile_string.replace('$$QUERIES$$', str(new_series))
            tile_string = tile_string.replace('$$SERIES_TYPE$$', 'LINE')

            # Change TIMESERIES to GRAPH_CHART, PIE to PIE_CHART.  SINGLE_VALUE and TOP_LIST remain unchanged
            if visual_type == 'TIMESERIES':
                tile_string = tile_string.replace('$$VISUAL_TYPE$$', 'GRAPH_CHART')
            else:
                if visual_type == 'PIE':
                    tile_string = tile_string.replace('$$VISUAL_TYPE$$', 'PIE_CHART')
                else:
                    tile_string = tile_string.replace('$$VISUAL_TYPE$$', visual_type)

            if legend_shown == 'False':
                tile_string = tile_string.replace('$$HIDE_LEGEND$$', 'true')
            else:
                tile_string = tile_string.replace('$$HIDE_LEGEND$$', 'false')

            if verbose:
                print('tile_string begin->')
                print(tile_string)
                print('<-tile_string end')

            tile_json = json.loads(tile_string)
            tiles.append(tile_json)
        else:
            tiles.append(tile)
    new_dashboard_json['tiles'] = copy.deepcopy(tiles)
    return new_dashboard_json


def main():
    convert_dashboards()


if __name__ == '__main__':
    main()
