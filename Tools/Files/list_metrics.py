import json

def main():
    with open('../../DynatraceDashboardGenerator/metrics.json', 'r', encoding='utf-8') as infile:
        original_json = json.loads(infile.read())
        for metric in original_json:
            metric_id = metric.get('metricId')
            dims = metric.get('dimensionDefinitions')
            lower_metric_id = metric_id.lower()
            if 'cloud.azure.microsoft_documentdb' in lower_metric_id:
                # print(metric_id, dims)
                if 'requ' in lower_metric_id:
                    # if 'fail' in lower_metric_id:
                    print(metric_id, dims)


if __name__ == '__main__':
    main()
