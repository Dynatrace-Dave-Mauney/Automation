import copy
import glob
import json
import os
import re
import shutil
from inspect import currentframe
from pathlib import Path

DASHBOARD_TEMPLATE_PATH = 'Templates/Overview'
DASHBOARD_FIXED_PATH = 'Templates-Overview-Splits'

by_split_list = []
current_dashboard_name = ''


def fix_dashboards():
    # confirm('fix dashboards from ' + DASHBOARD_TEMPLATE_PATH + ' to ' + DASHBOARD_FIXED_PATH)
    initialize()

    for filename in glob.glob(DASHBOARD_TEMPLATE_PATH + '/00000000-*'):
        base_name = Path(filename).name

        if '-v' in base_name:
            print('DEBUG TESTING: SKIPPING VERSIONED FILE', base_name, current_dashboard_name)
            continue

        # fix_list = [
        #     '00000000-dddd-bbbb-ffff-000000000182.json',
        #     '00000000-dddd-bbbb-ffff-000000000195.json',
        #     '00000000-dddd-bbbb-ffff-000000000196.json',
        #     '00000000-dddd-bbbb-ffff-000000000821.json',
        #     '00000000-dddd-bbbb-ffff-000000000823.json',
        #     '00000000-dddd-bbbb-ffff-000000000824.json',
        #     '00000000-dddd-bbbb-ffff-000000000825.json',
        #     '00000000-dddd-bbbb-ffff-000000000826.json',
        #     '00000000-dddd-bbbb-ffff-000000001008.json',
        #     '00000000-dddd-bbbb-ffff-000000001011.json',
        #     '00000000-dddd-bbbb-ffff-000000001026.json',
        #     '00000000-dddd-bbbb-ffff-000000001027.json',
        #     '00000000-dddd-bbbb-ffff-000000001032.json',
        #     '00000000-dddd-bbbb-ffff-000000001103.json',
        # ]
        #
        # if base_name not in fix_list:
        #     continue

        with open(filename, 'r', encoding='utf-8') as f:
            dashboard = f.read()

            dashboard_json = json.loads(dashboard)
            original_dashboard_json = copy.deepcopy(dashboard_json)

            new_dashboard = fix_dashboard(dashboard)
            if new_dashboard != original_dashboard_json:
                # print('DEBUG TESTING: CHANGES MADE TO', current_dashboard_name)
                pretty_new_dashboard = json.dumps(new_dashboard, indent=4, sort_keys=False)
                # name = new_dashboard.get('dashboardMetadata').get('name')
                output_filename = DASHBOARD_FIXED_PATH + '/' + os.path.basename(filename)
                with open(output_filename, 'w', encoding='utf-8') as outfile:
                    outfile.write(pretty_new_dashboard)

    print('Unique "by" splits:')
    for by_split in sorted(by_split_list):
        print(by_split)


def fix_dashboard(dashboard):
    dashboard_json = json.loads(dashboard)
    new_dashboard_json = copy.deepcopy(dashboard_json)
    name = dashboard_json.get('dashboardMetadata').get('name')

    global current_dashboard_name
    current_dashboard_name = name

    tiles = new_dashboard_json.get('tiles')
    original_tiles = copy.deepcopy(tiles)

    # print('dashboard name:', name)
    for tile in tiles:
        tile_type = tile.get('tileType')
        # print('tile_type:', tile_type)
        if tile_type != 'DATA_EXPLORER':
            continue

        tile_name = tile.get('name')
        tile_custom_name = tile.get('customName')
        tile_queries = tile.get('queries')
        tile_queries_split_by = []
        if tile_queries:
            tile_queries_split_by = tile_queries[0].get('splitBy', [])
        tile_metric_expressions = tile.get('metricExpressions')
        tile_metric_expressions_split_by = ''
        if tile_metric_expressions and len(tile_metric_expressions) > 0:
            tile_metric_expressions_split_by = re.match(r"splitBy(.*)", tile_metric_expressions[0])
            if not tile_metric_expressions_split_by:
                tile_metric_expressions_split_by = ''

        # print(tile_name, tile_custom_name, tile_queries_split_by, str(tile_queries[0]), str(tile_metric_expressions[0]))
        # print(tile_name, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by)

        if not tile_custom_name:
            tile_custom_name = tile_name

        if 'Cohesity' in name:
            fix_cohesity(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by)
        else:
            if 'NAS Storage' in name:
                fix_nas_storage(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by)
            else:
                if 'SAN Storage' in name:
                    fix_san_storage(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by)
                else:
                    if 'Self-Monitoring' in name:
                        fix_self_monitoring(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by)
                    else:
                        if 'AWS' in name:
                            fix_aws(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by)

        collect_by_splits(tile)

    # if tiles != original_tiles:
    #     print('DEBUG TESTING: CHANGES MADE!', current_dashboard_name)

    return new_dashboard_json


def collect_by_splits(tile):
    global by_split_list

    if 'AWS' in current_dashboard_name:
        tile_queries = tile.get('queries')
        if tile_queries:
            tile_queries_metric = tile_queries[0].get('metric')
        else:
            tile_queries_metric = None
        # print("-->", tile_queries, tile_queries_metric)

        if tile_queries_metric and "By" in tile_queries_metric and 'Byte' not in tile_queries_metric:
            by_split = re.sub('.*?By', 'By', tile_queries_metric)
            if by_split not in by_split_list:
                by_split_list.append(by_split)

def fix_cohesity(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by):
    # print('FIXING Cohesity...')

    new_split = None

    if tile_queries_split_by == [] and tile_metric_expressions_split_by == '':
        if 'alert' in tile_custom_name:
            new_split = 'alert_name'
        else:
            if 'job' in tile_custom_name:
                new_split = 'job_name'
            else:
                if 'cluster' in tile_custom_name:
                    new_split = 'cluster_name'
                else:
                    if 'node' in tile_custom_name:
                        new_split = 'node_name'

        # print(tile_custom_name, new_split)

        if new_split:
            tile['queries'][0]['splitBy'] = [new_split]
            tile['metricExpressions'][0] = tile['metricExpressions'][0].replace('splitBy()', f'splitBy({new_split})')


def fix_nas_storage(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by):
    # print('FIXING NAS Storage...')

    new_split = None

    if tile_queries_split_by == [] and tile_metric_expressions_split_by == '':
        if 'alert' in tile_custom_name:
            new_split = 'nas.alert_summary'
        else:
            if 'array' in tile_custom_name:
                new_split = 'nas.source_array'
            else:
                if 'account' in tile_custom_name:
                    new_split = 'nas.account_name'
                else:
                    if 'bucket' in tile_custom_name:
                        new_split = 'nas.bucket_name'
                    else:
                        if 'hardware' in tile_custom_name or 'file_system' in tile_custom_name:
                            new_split = 'nas.component_name'

        # print(tile_custom_name, new_split)

        if new_split:
            tile['queries'][0]['splitBy'] = [new_split]
            tile['metricExpressions'][0] = tile['metricExpressions'][0].replace('splitBy()', f'splitBy({new_split})')


def fix_san_storage(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by):
    # print('FIXING SAN Storage...')

    if tile_queries_split_by == [] and tile_metric_expressions_split_by == '':
        new_split = 'san.array_name'

        # print(tile_custom_name, new_split)

        tile['queries'][0]['splitBy'] = [new_split]
        tile['metricExpressions'][0] = tile['metricExpressions'][0].replace('splitBy()', f'splitBy({new_split})')


def fix_self_monitoring(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by):
    # print('FIXING Self Monitoring...')

    tile_queries = tile.get('queries')[0]
    tile_queries_metric = tile_queries.get('metric')
    # print('tile_queries_metric:', tile_queries_metric)

    new_split = None

    # if tile_queries_split_by == [] and tile_metric_expressions_split_by == '':
    if True:
        if 'active_gate' in tile_queries_metric:
            new_split = 'host.name'
        else:
            if 'extension.engine' in tile_queries_metric:
                new_split = 'host.name'
            else:
                if 'extension' in tile_queries_metric:
                    new_split = 'dt.extension.name'
                else:
                    if 'datasource.wmi' in tile_queries_metric:
                        new_split = 'host.name'
                    else:
                        # For all non-wmi data sources
                        if 'datasource' in tile_queries_metric:
                            new_split = 'dt.metrics.source'
                        else:
                            if 'agent_modules' in tile_queries_metric:
                                new_split = 'dt.oneagent.health_state'
                            else:
                                if 'storage' in tile_queries_metric:
                                    new_split = 'data.type'
                                else:
                                    if 'synthetic' in tile_queries_metric:
                                        new_split = 'dt.entity.synthetic_location'

        # print(tile_custom_name, tile_queries_metric, new_split)

        if new_split:
            tile['queries'][0]['splitBy'] = [new_split]
            tile_metric_expressions = tile.get('metricExpressions')
            if tile_metric_expressions:
                tile['metricExpressions'][0] = tile['metricExpressions'][0].replace('splitBy()', f'splitBy({new_split})')


def fix_aws(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by):
    # print('FIXING AWS...')

    tile_queries = tile.get('queries')[0]
    tile_queries_metric = tile_queries.get('metric')
    # print('tile_queries_metric:', tile_queries_metric)

    new_split = None

    metric_by_dict = {
        'ByContactFlowName': 'ContactFlowName',
        'ByContactFlowNameMetricGroup': 'ContactFlowName,MetricGroup',
        'ByMetricGroupQueueName': 'MetricGroup,QueueName',
        'ByRegion': 'Region',
        'ByRegionEngineName': 'Region,EngineName',
        'ByRegionHost': 'Region,Host',
        'ByRegionOperation': 'Region,Operation',
        'ByRegionRule': 'Region,Rule',
        'ByStageResourceMethod': 'Stage,Resource,Method',
        # TESTING
        'ByBotAliasInputModeOperation': 'Bot,Alias,InputMode,Operation',
        'ByBotAliasOperation': 'Bot,Alias,Operation',
        'ByBrokerID': 'Broker ID',
        'ByCacheNodeId': 'CacheNodeId',
        'ByClassResourceType': 'Class,Resource,Type',
        'ByClientId': 'ClientId',
        'ByConsumerGroupTopic': 'ConsumerGroup,Topic',
        'ByDestinationTypeFilterName': 'DestinationType,FilterName',
        'ByFilterId': 'FilterId',
        'ByMetricGroup': 'MetricGroup',
        'ByNodeId': 'NodeId',
        'ByRegionAPIName': 'Region,APIName',
        'ByRegionActivityArn': 'Region,ActivityArn',
        'ByRegionInstanceIDParticipantStreamTypeTypeofConnection': 'Region,InstanceID,Participant,StreamType,TypeofConnection',
        'ByRegionLambdaFunctionArn': 'Region,LambdaFunctionArn',
        'ByRegionRuleName': 'Region,RuleName',
        'ByRegionServiceIntegrationResourceArn': 'Region,Service,Integration,ResourceArn',
        'ByRegionServiceMetric': 'Region,Service,Metric',
        'ByRegionStateMachineArn': 'Region,StateMachineArn',
        'ByRole': 'Role',
        'ByServiceName': 'ServiceName',
    }

    testing_metric_by_dict = {
        # TESTING
        'ByBotAliasInputModeOperation': 'BotAlias,InputMode,Operation',
        'ByBotAliasOperation': 'BotAlias,Operation',
        'ByBrokerID': 'Broker ID',
        'ByCacheNodeId': 'CacheNodeId',
        'ByClassResourceType': 'Class,Resource,Type',
        'ByClientId': 'ClientId',
        'ByConsumerGroupTopic': 'Consumer Group,Topic',
        'ByDestinationTypeFilterName': 'DestinationType,FilterName',
        'ByFilterId': 'FilterId',
        'ByMetricGroup': 'MetricGroup',
        'ByNodeId': 'NodeId',
        'ByRegionAPIName': 'Region,APIName',
        'ByRegionActivityArn': 'Region,ActivityArn',
        'ByRegionInstanceIDParticipantStreamTypeTypeofConnection': 'Region, Instance ID, Participant, Stream Type, Type of Connection',
        'ByRegionLambdaFunctionArn': 'Region,LambdaFunctionArn',
        'ByRegionRuleName': 'Region,RuleName',
        'ByRegionServiceIntegrationResourceArn': 'Region,ServiceIntegrationResourceArn',
        'ByRegionServiceMetric': 'Region,ServiceMetric',
        'ByRegionStateMachineArn': 'Region,StateMachineArn',
        'ByRole': 'Role',
        'ByServiceName': 'ServiceName',
    }

    if 'By' in tile_queries_metric and 'Byte' not in tile_queries_metric:
        metric_by = re.sub('.*By', 'By', tile_queries_metric)
        new_split = metric_by_dict.get(metric_by)
        if metric_by in testing_metric_by_dict:
            print('DEBUG TESTING:', tile_queries_metric, metric_by, new_split)
    else:
        if 'aws.az' in tile_queries_metric:
            new_split = 'dt.entity.aws_availability_zone'

    if not new_split:
        if 'By' in tile_queries_metric and 'Byte' not in tile_queries_metric:
            print('Unknown By Split:', tile_queries_metric, current_dashboard_name)


    # print(tile_custom_name, tile_queries_metric, new_split)

    if new_split:
        new_split_list = to_list(new_split)
        tile['queries'][0]['splitBy'] = new_split_list
        if tile.get('metricExpressions'):
            tile['metricExpressions'][0] = re.sub('splitBy\(.*?\)', f'splitBy({new_split})', tile['metricExpressions'][0])


def fix_metrics_that_have_splits_mentioned_only_in_tile_name(tile, tile_custom_name, tile_queries_split_by, tile_metric_expressions_split_by):
    # dsfm:server.metrics.ingest.external_datapoints_by_source_address Metrics - Ingest - External Datapoints By Source Address
    # dsfm:server.utilization.by_contributor Utilization - By Contributor
    # dsfm:server.metrics.ingest.external_datapoints_by_source_address Metrics - Ingest - External Datapoints By Source Address
    # dsfm:server.utilization.by_contributor Utilization - By Contributor
    # dsfm:cluster.utilization.by_contributor Utilization - By Contributor
    # ext:cloud.aws.autoscaling.groupMinSizeAverage Group Min Size (By ASG)
    # ext:cloud.aws.autoscaling.groupDesiredCapacityAverage Group Desired Capacity (By ASG)
    # ext:cloud.aws.autoscaling.groupInServiceInstancesAverage Group InService Instances (By ASG)
    # ext:cloud.aws.autoscaling.groupPendingInstancesAverage Group Pending Instances (By ASG)
    # ext:cloud.aws.autoscaling.groupMaxSizeAverage Group Max Size (By ASG)
    # ext:cloud.aws.autoscaling.groupTotalInstancesAverage Group Total Instances (By ASG)
    # ext:cloud.aws.autoscaling.groupStandbyInstancesAverage Group Standby Instances (By ASG)
    # ext:cloud.aws.autoscaling.groupTerminatingInstancesAverage Group Terminating Instances (By ASG)
    # ext:cloud.aws.dax.totalRequestCountSum Total Requests (By Cluster)
    # ext:cloud.aws.dax.itemCacheHitsSum Cache Hits Count (By Cluster)
    # ext:cloud.aws.dax.errorRequestCountSum Error Requests (By Cluster)
    # ext:cloud.aws.dax.clientConnectionsSum Client Connections (By Cluster)
    # ext:cloud.aws.dax.queryRequestCountSum Query & Scan Request Count (By Cluster)
    # ext:cloud.aws.dax.itemCacheMissesSum Cache Misses (By Cluster)
    pass

def to_list(new_split):
    if ',' in new_split:
        return new_split.split(',')
    else:
        return [new_split]


def initialize():
    # confirm('The ' + DASHBOARD_FIXED_PATH + ' directory will now be removed to prepare for the conversion.')
    remove_directory(DASHBOARD_FIXED_PATH)

    if not os.path.isdir(DASHBOARD_FIXED_PATH):
        make_directory(DASHBOARD_FIXED_PATH)


def remove_directory(path):
    print('remove_directory(' + path + ')')

    try:
        shutil.rmtree(path, ignore_errors=False)

    except OSError:
        print('Directory %s does not exist' % path)
    else:
        print('Removed the directory %s ' % path)


def make_directory(path):
    print('make_directory(' + path + ')')
    try:
        os.makedirs(path)
    except OSError:
        print('Creation of the directory %s failed' % path)
        exit()
    else:
        print('Successfully created the directory %s ' % path)


def confirm(message):
    print('confirm(' + message + ')')
    proceed = input('%s (Y/n) ' % message).upper() == 'Y'
    if not proceed:
        exit(get_linenumber())


def get_linenumber():
    print('get_linenumber()')
    cf = currentframe()
    return cf.f_back.f_lineno


def main():
    fix_dashboards()


if __name__ == '__main__':
    main()
