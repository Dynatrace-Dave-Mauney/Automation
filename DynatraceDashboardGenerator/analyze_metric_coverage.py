"""

Determine which metrics in the metrics.json file are not covered by a rule in the dashboard_blueprint.yaml file.

"""

import json
import yaml


def main():

    metric_list = []
    with open('metrics.json') as json_file:
        metric_json_list = json.load(json_file)
        for metric_json_dict in metric_json_list:
            metric_id = metric_json_dict.get('metricId')
            metric_list.append(metric_id)

    metric_matcher_list = []
    with open('dashboard_blueprint.yaml', 'r') as file:
        document = file.read()
        dashboard_blueprint = yaml.load(document, Loader=yaml.FullLoader)
        dashboard_list = dashboard_blueprint.get('dashboards')
        for dashboard in dashboard_list:
            metric_matcher = dashboard.get('metrics')
            metric_matcher_list.append(metric_matcher)
            
    for metric in metric_list:
        match_found = False
        for metric_matcher in metric_matcher_list:
            if len(metric_matcher) == 1:
                if metric.startswith(metric_matcher[0]):
                    # print(f'{metric} matches {metric_matcher[0]}')
                    match_found = True
            else:
                if metric_matcher[0] <= metric <= metric_matcher[1]:
                    # print(f'{metric} matches {metric_matcher}')
                    match_found = True
        if not match_found:
            # Filter out the metrics that are always present
            if  not metric.startswith('builtin:cloud.aws') and \
                not metric.startswith('builtin:cloud.openstack') and \
                not metric.startswith('builtin:host.zos') and \
                not metric.startswith('builtin:security') and \
                not metric.startswith('builtin:tech.Hadoop') and \
                not metric.startswith('builtin:tech.couchbase') and \
                not metric.startswith('builtin:tech.couchdb') and \
                not metric.startswith('builtin:tech.customscripts') and \
                not metric.startswith('builtin:tech.haproxy') and \
                not metric.startswith('builtin:tech.hornetq') and \
                not metric.startswith('builtin:tech.jboss') and \
                not metric.startswith('builtin:tech.liberty') and \
                not metric.startswith('builtin:tech.memcached') and \
                not metric.startswith('builtin:tech.varnish') and \
                not metric.startswith('builtin:tech.weblogic') and \
                not metric.startswith('builtin:tech.wso2') and \
                not metric.startswith('builtin:tech.zos') and \
                not metric.startswith('dsfm:azure'):
                    print(f'{metric} lacks coverage')


if __name__ == '__main__':
    main()
