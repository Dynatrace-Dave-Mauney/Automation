import copy
import glob
import json
import os
import codecs

add_table_for_donut_charts = True

# notebook_input_path = '../$Private/Customers/PRIOR_CUSTOMER/Assets/NewPlatform/Notebooks/*.json'
# notebook_input_path = 'customer_specific/PRIOR_CUSTOMER/NotebookToDashboardInput/NMXP*.json'
# notebook_input_path = 'customer_specific/PRIOR_CUSTOMER/NotebookToDashboardInput/*NMC*.json'
# notebook_input_path = 'customer_specific/PRIOR_CUSTOMER/NotebookToDashboardInput/Dashboard Conversion_  App Tracker.json'
# notebook_input_path = 'customer_specific/PRIOR_CUSTOMER/NotebookToDashboardInput/Dashboard Conversion_ dMHQ.json'
# notebook_input_path = 'customer_specific/PRIOR_CUSTOMER/NotebookToDashboardInput/CONVERT_MIX.json'
# notebook_input_path = 'customer_specific/PRIOR_CUSTOMER/NotebookToDashboardInput/CONVERT_PIE.json'
# notebook_input_path = 'customer_specific/PRIOR_CUSTOMER/NotebookToDashboardInput/*.json'
# notebook_input_path = 'customer_specific/PRIOR_CUSTOMER/DashboardTemplates/TEMPLATE_DONUT.json'

# dashboard_output_path = 'customer_specific/PRIOR_CUSTOMER/ConvertedDashboards'

notebook_input_path = 'customer_specific/$Current/*.json'
dashboard_output_path = '../$Private/Customers/$Current/Assets/NewPlatform/Dashboards'

dashboard_template = {
    "version": 15,
    "variables": [],
    "tiles": {
        "0": {
            "type": "data",
            "title": "",
            "davis": {
                "enabled": False,
                "davisVisualization": {
                    "isAvailable": True
                }
            },
            "visualization": "donutChart",
            "visualizationSettings": {
                "thresholds": [],
                "chartSettings": {
                    "gapPolicy": "connect",
                    "circleChartSettings": {
                        "groupingThresholdType": "relative",
                        "groupingThresholdValue": 0,
                        "valueType": "relative"
                    },
                    "categoryOverrides": {},
                    "curve": "linear",
                    "pointsDisplay": "auto",
                    "truncationMode": "middle",
                    "categoricalBarChartSettings": {
                        "categoryAxis": "state.buttonClicked",
                        "categoryAxisLabel": "state.buttonClicked",
                        "valueAxis": "count",
                        "valueAxisLabel": "count",
                        "tooltipVariant": "single"
                    }
                },
                "singleValue": {
                    "showLabel": True,
                    "label": "",
                    "prefixIcon": "",
                    "recordField": "state.buttonClicked",
                    "autoscale": True,
                    "alignment": "center",
                    "colorThresholdTarget": "value"
                },
                "table": {
                    "rowDensity": "condensed",
                    "enableSparklines": False,
                    "hiddenColumns": [],
                    "lineWrapIds": [],
                    "columnWidths": {},
                    "enableThresholdInRow": False
                },
                "honeycomb": {
                    "shape": "hexagon",
                    "legend": {
                        "hidden": False,
                        "position": "auto"
                    },
                    "colorMode": "color-palette",
                    "colorPalette": "blue",
                    "dataMappings": {
                        "value": "count"
                    },
                    "displayedFields": [
                        "state.buttonClicked"
                    ]
                },
                "histogram": {
                    "dataMappings": [
                        {
                            "valueAxis": "count",
                            "rangeAxis": ""
                        }
                    ]
                }
            },
            "querySettings": {
                "maxResultRecords": 1000,
                "defaultScanLimitGbytes": 500,
                "maxResultMegaBytes": 1,
                "defaultSamplingRatio": 10,
                "enableSampling": False
            }
        }
    },
    "layouts": {
        "0": {
            "x": 0,
            "y": 0,
            "w": 6,
            "h": 7
        }
    },
    "importedWithCode": False
}


def run():
    convert_notebooks(notebook_input_path)


def convert_notebooks(path):
    for filename in glob.glob(path):
        if filename.endswith('.json') and not filename.endswith('.metadata.json'):
            with codecs.open(filename, encoding='utf-8') as f:
                notebook = f.read()
                notebook_json = json.loads(notebook)
                notebook_file_name = os.path.basename(filename)
                notebook_name = os.path.splitext(notebook_file_name)[0]
                # formatted_document = json.dumps(notebook_json, indent=4, sort_keys=False)
                convert_notebook(notebook_name, notebook_file_name, notebook_json)


def convert_notebook(notebook_name, notebook_file_name, notebook_json):
    print(f'Converting "{notebook_name}" ({notebook_file_name})')

    dashboard = copy.deepcopy(dashboard_template)
    tiles = copy.deepcopy(dashboard_template.get('tiles'))
    tile_template = copy.deepcopy(tiles.get('0'))

    new_tiles = {}

    index = 0
    x = 0
    sections = notebook_json.get('sections')

    for section in sections:
        tile = copy.deepcopy(tile_template)
        notebook_section_type = section.get('type')

        tile_state_visualization = None

        if notebook_section_type == 'markdown':
            tile = {'type': 'markdown', 'title': '', 'content': section.get('markdown')}
        else:
            if notebook_section_type == 'dql':
                tile['type'] = 'data'
            else:
                if notebook_section_type == 'function':
                    tile['type'] = 'code'
                else:
                    tile['type'] = notebook_section_type

            section_title = section.get('title', "No Title")
            tile['title'] = section_title
            tile_state = section.get('state')
            if tile_state:
                tile_state_input = tile_state.get('input')
                if tile_state_input:
                    tile_state_input_value = tile_state_input['value']
                    if tile_state_input_value:
                        if notebook_section_type == 'dql':
                            tile['query'] = tile_state_input_value
                        else:
                            if notebook_section_type == 'function':
                                tile['input'] = tile_state_input_value

                        tile_state_visualization = section.get('state').get('visualization')
                        tile_state_visualization_settings = section.get('state').get('visualizationSettings')
                        # tile_state_query_settings = section.get('state').get('querySettings')

                        if tile_state_visualization:
                            tile['visualization'] = tile_state_visualization
                            if tile_state_visualization_settings:
                                tile['visualizationSettings'] = tile_state_visualization_settings
                                if tile_state_visualization_settings:
                                    tile['visualizationSettings'] = tile_state_visualization_settings

        new_tiles[str(index)] = copy.deepcopy(tile)

        index += 1
        x += 7

        # Optionally, add a table below each donut chart
        if add_table_for_donut_charts:
            if tile_state_visualization == 'donutChart':
                tile['visualization'] = 'table'
                new_tiles[str(index)] = copy.deepcopy(tile)
                index += 1
                x += 7

    if new_tiles:
        dashboard['tiles'] = new_tiles

    layouts = generate_layouts(new_tiles)
    dashboard['layouts'] = layouts

    dashboard_json = json.dumps(dashboard, indent=4, sort_keys=False)

    output_file_name = f'{dashboard_output_path}/{notebook_file_name}'
    print(f'Writing to {output_file_name}')
    with open(output_file_name, 'w', encoding='utf-8') as outfile:
        outfile.write(dashboard_json)


def generate_layouts(new_tiles):
    standard_w = 30
    standard_h = 10
    layouts = {}
    x = 0
    y = 0

    for key in new_tiles.keys():
        layouts[key] = {
            "x": x,
            "y": y,
            "w": standard_w,
            "h": standard_h
        }
        y += standard_h

    return layouts


if __name__ == '__main__':
    run()
