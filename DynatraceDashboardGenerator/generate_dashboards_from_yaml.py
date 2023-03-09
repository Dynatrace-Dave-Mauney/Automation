"""
Create dashboards from the dashboard controller YAML file.
"""

import copy
import json
import sqlite3
from sqlite3 import Error

import yaml

# For the transition.
# To mainly use old charts...use the first one
# To mainly use new charts...use the second one
USE_NEW_CHARTS = ['Kafka', 'Dynatrace Self-Monitoring', 'Google Cloud 1', 'Google Cloud 2', 'Google Cloud 3']
USE_OLD_CHARTS = []
USE_CODE_MODE_DATA_EXPLORER = ['Processes']

def get_dashboard_controller():
    with open('dashboard_controller.yaml', 'r') as file:
        document = file.read()
        return yaml.load(document, Loader=yaml.FullLoader)


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def get_dashboard_template():
    conn = create_connection(r'DynatraceDashboardGenerator.db')
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT data FROM templates WHERE template_id = "dashboard"')
        return json.loads(cur.fetchone()[0])


def get_tile_template(template_id):
    conn = create_connection(r'DynatraceDashboardGenerator.db')
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT data FROM templates WHERE template_id = "' + template_id + '"')
        return json.loads(cur.fetchone()[0])


def select_metric_by_id(metric_id):
    conn = create_connection(r'DynatraceDashboardGenerator.db')
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT data FROM metrics WHERE metric_id = ?', (metric_id,))
        return json.loads(cur.fetchone()[0])


def select_entity_by_id(entity_id):
    conn = create_connection(r'DynatraceDashboardGenerator.db')
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT data FROM entities WHERE entity_id = ?', (entity_id,))
        return json.loads(cur.fetchone()[0])


def skip_metric(metric_id):
    # Use this temp code to create a simple one metric hosts dashboard for testing
    # if metric_id == 'builtin:host.cpu.usage':
    #     print('NOT Skipping: ' + metric_id + ' because it is equal to "builtin:host.cpu.usage"')
    #     return False
    # else:
    #     return True

    BAD_METRICS = {
                   'builtin:billing.ddu',                                       # Entity Type = NONE
                   'builtin:billing.ddu.metrics.byEntity',                      # Entity Type = APM_AGENT
                   'builtin:billing.ddu.metrics.byEntityRaw',                   # Entity Type = APM_AGENT
                   'builtin:billing.ddu.metrics.byMetric',                      # Entity Type = NONE
                   'builtin:billing.ddu.log.byDescription',
                   'builtin:billing.ddu.log.byEntity',
                   'builtin:billing.ddu.log.total',
                   'builtin:billing.ddu.serverless.byDescription',
                   'builtin:billing.ddu.serverless.byEntity',
                   'builtin:billing.ddu.serverless.total',
                   'builtin:billing.ddu.metrics.total',
                   'builtin:synthetic.http.execution.status',
                   'builtin:tech.cassandra.RangeSlice.Latency.95thPercentile',
                   'builtin:tech.cassandra.Read.Latency.95thPercentile',
                   'builtin:tech.cassandra.Write.Latency.95thPercentile'
                   }

    # if metric_id in BAD_METRICS or \
    #   metric_id.startswith('builtin:billing'):

    if metric_id in BAD_METRICS:
        print('Skipping: ' + metric_id + ' because it is considered a bad metric currently')
        return True

    # These metrics (.NET) seem to work fine now (it affected only aaaaaaaa-bbbb-cccc-dddd-000000000009 before it was fixed.
    # if '#' in metric_id or '%' in metric_id:
    #     print('Skipping: ' + metric_id + ' because it contains an invalid character (#, or %)')
    #     return True

    return False


# This method is not currently necessary, but can be uncommented later if needed
# def skip_entity(metric_id, entity_type):
#     # BAD_ENTITIES = {'SERVICE_METHOD_GROUP', 'CLOUD_APPLICATION_INSTANCE', 'EXTERNAL_SYNTHETIC_TEST_STEP'}
#     BAD_ENTITIES = {}
#
#     if entity_type in BAD_ENTITIES:
#         print('Skipping: ' + metric_id + ' because it has a bad entity: ' + entity_type)
#         return True
#
#     return False


def convert_entity_type_and_dimension_definition(metric_id, entity_type):
    if entity_type == 'AWS_APPLICATION_LOAD_BALANCER':
        entity_type = 'ALB'
    if entity_type == 'AWS_NETWORK_LOAD_BALANCER':
        entity_type = 'NLB'
    if entity_type == 'AUTO_SCALING_GROUP':
        entity_type = 'ASG'
    if entity_type == 'CUSTOM_APPLICATION':
        entity_type = 'DEVICE_APPLICATION'
    if entity_type == 'CUSTOM_APPLICATION_METHOD':
        entity_type = 'DEVICE_APPLICATION_METHOD'
    # Redis Enterprise uses dt.entity.custom_device vs dt.entity.iot...
    # if entity_type == 'CUSTOM_DEVICE':
    #     entity_type = 'IOT'
    if entity_type == 'DYNAMO_DB_TABLE':
        entity_type = 'DYNAMO_DB'
    if entity_type == 'EBS_VOLUME':
        entity_type = 'EBS'
    if entity_type == 'EC2_INSTANCE':
        entity_type = 'EC2'
    if entity_type == 'ELASTIC_LOAD_BALANCER':
        entity_type = 'ELB'
    if entity_type == 'PROCESS_GROUP':
        entity_type = 'PROCESS_GROUP_INSTANCE'
    if entity_type == 'RELATIONAL_DATABASE_SERVICE':
        entity_type = 'RDS'

    dimension_definition = 'dt.entity.' + entity_type.lower()

    if entity_type == 'CLOUD_APPLICATION_INSTANCE':
        entity_type = 'MONITORED_ENTITY˟CLOUD_APPLICATION_INSTANCE'
    if entity_type == 'DCRUM_SERVICE':
        entity_type = 'DCRUM_ENTITY'
    if entity_type == 'EXTERNAL_SYNTHETIC_TEST_STEP':
        entity_type = 'MONITORED_ENTITY˟EXTERNAL_SYNTHETIC_TEST_STEP'
    if entity_type == 'HTTP_CHECK':
        entity_type = 'SYNTHETIC_HTTPCHECK'
    if entity_type == 'HTTP_CHECK_STEP':
        entity_type = 'SYNTHETIC_HTTPCHECK_STEP'
    if entity_type == 'HYPERVISOR':
        entity_type = 'ESXI'
    if entity_type == 'NETWORK_INTERFACE':
        entity_type = 'MONITORED_ENTITY˟NETWORK_INTERFACE'
    if entity_type == 'SERVICE_METHOD':
        entity_type = 'SERVICE_KEY_REQUEST'
    if entity_type == 'VIRTUALMACHINE':
        entity_type = 'VIRTUAL_MACHINE'

    if entity_type.startswith('AZURE_') or \
       entity_type == 'CUSTOM_DEVICE_GROUP' or \
       entity_type == 'DEVICE_APPLICATION' or \
       entity_type == 'DEVICE_APPLICATION_METHOD' or \
       entity_type == 'DOCKER_CONTAINER_GROUP_INSTANCE' or \
       entity_type == 'SERVICE_METHOD_GROUP':
        entity_type = 'MONITORED_ENTITY˟' + entity_type

    # Clean up oddballs individually
    if metric_id == 'builtin:billing.apps.custom.userActionPropertiesByDeviceApplication' or \
       metric_id == 'builtin:billing.apps.custom.sessionsWithoutReplayByApplication':
        entity_type = 'CUSTOM_APPLICATION'

    GLOBAL_BACKGROUND_ACTIVITY = {
        'builtin:tech.generic.count',
        'builtin:tech.generic.cpu.groupSuspensionTime',
        'builtin:tech.generic.cpu.groupTotalTime',
        'builtin:tech.elasticsearch.local.indices.query_cache.cache_count',
        'builtin:tech.elasticsearch.local.indices.query_cache.cache_size',
        'builtin:tech.elasticsearch.local.indices.query_cache.evictions',
        'builtin:tech.elasticsearch.local.indices.segments.count',
        'builtin:tech.elasticsearch.local.number_of_data_nodes',
        'builtin:tech.elasticsearch.local.number_of_nodes',
        'builtin:tech.elasticsearch.local.status-green',
        'builtin:tech.elasticsearch.local.status-red',
        'builtin:tech.elasticsearch.local.status-unknown',
        'builtin:tech.elasticsearch.local.status-yellow',
        'builtin:tech.elasticsearch.local.unassigned_shards',
        'builtin:tech.Hadoop.hdfs.BlocksTotal',
        'builtin:tech.Hadoop.hdfs.CacheCapacity',
        'builtin:tech.Hadoop.hdfs.CacheUsed',
        'builtin:tech.Hadoop.hdfs.CapacityRemaining',
        'builtin:tech.Hadoop.hdfs.CapacityTotal',
        'builtin:tech.Hadoop.hdfs.CapacityUsed',
        'builtin:tech.Hadoop.hdfs.CapacityUsedNonDFS',
        'builtin:tech.Hadoop.hdfs.CorruptBlocks',
        'builtin:tech.Hadoop.hdfs.EstimatedCapacityLostTotal',
        'builtin:tech.Hadoop.hdfs.FilesAppended',
        'builtin:tech.Hadoop.hdfs.FilesCreated',
        'builtin:tech.Hadoop.hdfs.FilesDeleted',
        'builtin:tech.Hadoop.hdfs.FilesRenamed',
        'builtin:tech.Hadoop.hdfs.FilesTotal',
        'builtin:tech.Hadoop.hdfs.NumberOfMissingBlocks',
        'builtin:tech.Hadoop.hdfs.NumDeadDataNodes',
        'builtin:tech.Hadoop.hdfs.NumDecomDeadDataNodes',
        'builtin:tech.Hadoop.hdfs.NumDecomLiveDataNodes',
        'builtin:tech.Hadoop.hdfs.NumDecommissioningDataNodes',
        'builtin:tech.Hadoop.hdfs.NumLiveDataNodes',
        'builtin:tech.Hadoop.hdfs.NumStaleDataNodes',
        'builtin:tech.Hadoop.hdfs.PendingDeletionBlocks',
        'builtin:tech.Hadoop.hdfs.PendingReplicationBlocks',
        'builtin:tech.Hadoop.hdfs.ScheduledReplicationBlocks',
        'builtin:tech.Hadoop.hdfs.TotalLoad',
        'builtin:tech.Hadoop.hdfs.UnderReplicatedBlocks',
        'builtin:tech.Hadoop.hdfs.VolumeFailuresTotal',
        'builtin:tech.Hadoop.yarn.AllocatedContainers',
        'builtin:tech.Hadoop.yarn.AllocatedMB',
        'builtin:tech.Hadoop.yarn.AllocatedVCores',
        'builtin:tech.Hadoop.yarn.AppsCompleted',
        'builtin:tech.Hadoop.yarn.AppsFailed',
        'builtin:tech.Hadoop.yarn.AppsKilled',
        'builtin:tech.Hadoop.yarn.AppsPending',
        'builtin:tech.Hadoop.yarn.AppsRunning',
        'builtin:tech.Hadoop.yarn.AppsSubmitted',
        'builtin:tech.Hadoop.yarn.AvailableMB',
        'builtin:tech.Hadoop.yarn.AvailableVCores',
        'builtin:tech.Hadoop.yarn.NumActiveNMs',
        'builtin:tech.Hadoop.yarn.NumDecommissionedNMs',
        'builtin:tech.Hadoop.yarn.NumLostNMs',
        'builtin:tech.Hadoop.yarn.NumRebootedNMs',
        'builtin:tech.Hadoop.yarn.NumUnhealthyNMs',
        'builtin:tech.Hadoop.yarn.PendingMB',
        'builtin:tech.Hadoop.yarn.PendingVCores',
        'builtin:tech.Hadoop.yarn.ReservedMB',
        'builtin:tech.Hadoop.yarn.ReservedVCores',
        'builtin:tech.jvm.spark.aliveWorkers.gauge',
        'builtin:tech.jvm.spark.aliveWorkers',
        'builtin:tech.jvm.spark.apps',
        'builtin:tech.jvm.spark.apps.gauge',
        'builtin:tech.jvm.spark.driver.Count',
        'builtin:tech.jvm.spark.driver.Count.timer',
        'builtin:tech.jvm.spark.driver.Mean',
        'builtin:tech.jvm.spark.driver.Mean.timer',
        'builtin:tech.jvm.spark.driver.OneMinuteRate',
        'builtin:tech.jvm.spark.driver.OneMinuteRate.timer',
        'builtin:tech.jvm.spark.driver.activeJobs',
        'builtin:tech.jvm.spark.driver.activeJobs.gauge',
        'builtin:tech.jvm.spark.driver.allJobs',
        'builtin:tech.jvm.spark.driver.allJobs.gauge',
        'builtin:tech.jvm.spark.driver.failedStages',
        'builtin:tech.jvm.spark.driver.failedStages.gauge',
        'builtin:tech.jvm.spark.driver.runningStages',
        'builtin:tech.jvm.spark.driver.runningStages.gauge',
        'builtin:tech.jvm.spark.driver.waitingStages',
        'builtin:tech.jvm.spark.driver.waitingStages.gauge',
        'builtin:tech.jvm.spark.waitingApps',
        'builtin:tech.jvm.spark.waitingApps.gauge',
        'builtin:tech.jvm.spark.workers',
        'builtin:tech.jvm.spark.workers.gauge',
        'builtin:tech.kafka.pg.kafka.controller.ControllerStats.LeaderElectionRateAndTimeMs.OneMinuteRate',
        'builtin:tech.kafka.pg.kafka.controller.ControllerStats.UncleanLeaderElectionsPerSec.OneMinuteRate',
        'builtin:tech.kafka.pg.kafka.controller.KafkaController.ActiveControllerCount.Value',
        'builtin:tech.kafka.pg.kafka.controller.KafkaController.OfflinePartitionsCount.Value',
        'builtin:tech.kafka.pg.kafka.server.ReplicaManager.PartitionCount.Value',
        'builtin:tech.kafka.pg.kafka.server.ReplicaManager.UnderReplicatedPartitions.Value'
    }

    # metric_id.startswith('builtin:tech.jvm.spark') or \
    if metric_id in GLOBAL_BACKGROUND_ACTIVITY or \
       'shards' in metric_id or \
       'indices.count' in metric_id or \
       'indices.docs' in metric_id or \
       'indices.fielddata' in metric_id or \
       metric_id.startswith('builtin:tech.couchbase') or \
       metric_id.startswith('builtin:tech.rabbitmq.topN') or \
       metric_id.startswith('builtin:tech.rabbitmq.cluster'):
        entity_type = 'GLOBAL_BACKGROUND_ACTIVITY'
        dimension_definition = 'dt.entity.process_group'
    if metric_id.startswith('builtin:tech.jvm.spark.worker.cores') or \
       metric_id == 'builtin:tech.jvm.spark.worker.executors' or \
       metric_id.startswith('builtin:tech.jvm.spark.worker.mem') or \
       metric_id.startswith('builtin:tech.couchbase.node'):
        entity_type = 'PROCESS_GROUP_INSTANCE'

    return entity_type, dimension_definition


def generate_metric_tile(top, left, metric_id, tile_dictionary):
    if skip_metric(metric_id):
        return None

    custom_charting_template = get_tile_template('CUSTOM_CHARTING')
    tile = copy.deepcopy(custom_charting_template)

    tile['bounds']['top'] = top
    tile['bounds']['left'] = left
    tile['bounds']['width'] = 304
    tile['bounds']['height'] = 304

    name = tile_dictionary['name']
    tile['name'] = name
    tile['tileType'] = 'CUSTOM_CHARTING'
    tile['configured'] = True

    tile['filterConfig']['type'] = 'MIXED'
    tile['filterConfig']['customName'] = name
    tile['filterConfig']['defaultName'] = 'Custom chart'

    tile['filterConfig']['chartConfig']['legendShown'] = True
    tile['filterConfig']['chartConfig']['type'] = 'TIMESERIES'

    tile['filterConfig']['chartConfig']['series'][0]['metric'] = metric_id
    tile['filterConfig']['chartConfig']['series'][0]['aggregation'] = tile_dictionary['aggregation']
    tile['filterConfig']['chartConfig']['series'][0]['percentile'] = None
    tile['filterConfig']['chartConfig']['series'][0]['type'] = tile_dictionary['type']

    metric_dict = select_metric_by_id(metric_id)
    entity_type = 'NONE'
    entity_type_list = metric_dict.get('entityType', ['NONE'])
    # One of the billing metrics has an empty list, so fix it
    if entity_type_list:
        entity_type = entity_type_list[0]
        # Ignore custom apps and focus on mobile apps
        if metric_id.startswith('builtin:apps.other') and \
                len(entity_type_list) == 2 and \
                entity_type_list[1] == 'MOBILE_APPLICATION':
            entity_type = 'MONITORED_ENTITY˟DEVICE_APPLICATION'

    # print(metric_id + ":" + entity_type + ":" + str(len(entity_type) )+ ":" + str(entity_type_list))

    # Not currently necessary
    # if skip_entity(metric_id, entity_type):
    #     continue

    entity_type, dimension_definition = convert_entity_type_and_dimension_definition(metric_id, entity_type)

    tile['filterConfig']['chartConfig']['series'][0]['entityType'] = entity_type
    dimension_dict = {'id': '0', 'name': dimension_definition, 'values': [], 'entityDimension': True}
    tile['filterConfig']['chartConfig']['series'][0]['dimensions'].append(dimension_dict)
    tile['filterConfig']['chartConfig']['series'][0]['sortColumn'] = True
    tile['filterConfig']['chartConfig']['series'][0]['aggregationRate'] = 'TOTAL'

    return tile


def generate_new_metric_tile(top, left, metric_id, tile_dictionary, mode):
    # print('tile_dictionary: ' + str(tile_dictionary))
    if skip_metric(metric_id):
        return None

    metric_selector = ''

    if mode == "code":
        data_explorer_template = get_tile_template('DATA_EXPLORER_CODE')
    else:
        data_explorer_template = get_tile_template('DATA_EXPLORER')

    tile = copy.deepcopy(data_explorer_template)
    # print(tile)

    tile['bounds']['top'] = top
    tile['bounds']['left'] = left
    tile['bounds']['width'] = 304
    tile['bounds']['height'] = 304

    name = tile_dictionary['name']
    tile['name'] = name
    tile['tileType'] = 'DATA_EXPLORER'
    tile['configured'] = True

    tile['customName'] = name

    if mode == "build":
        tile['queries'][0]['metric'] = metric_id
        agg = tile_dictionary['aggregation']
        if agg == 'NONE':
            agg = 'AVG'
        tile['queries'][0]['spaceAggregation'] = agg
    #tile['filterConfig']['chartConfig']['series'][0]['type'] = tile_dictionary['type']

    metric_dict = select_metric_by_id(metric_id)
    entity_type = 'NONE'
    entity_type_list = metric_dict.get('entityType', ['NONE'])
    # print('entity_type_list: ' + str(entity_type_list))

    # One of the billing metrics has an empty list, so fix it
    if entity_type_list:
        entity_type = entity_type_list[0]
        # Ignore custom apps and focus on mobile apps
        if metric_id.startswith('builtin:apps.other') and \
                len(entity_type_list) == 2 and \
                entity_type_list[1] == 'MOBILE_APPLICATION':
            entity_type = 'MONITORED_ENTITY˟DEVICE_APPLICATION'

    entity_type, dimension_definition = convert_entity_type_and_dimension_definition(metric_id, entity_type)
    #tile['queries'][0]['splitBy'] = entity_type
    #dimension_dict = {'id': '0', 'name': dimension_definition, 'values': [], 'entityDimension': True}
    # print(tile['queries'][0])
    # print(tile['queries'][0]['splitBy'])
    # print(type(tile['queries'][0]['splitBy']))
    # print(dimension_definition)

    if metric_id.startswith('builtin:tech.kafka.pg'):
        dimension_definition = 'dt.entity.process_group'
    else:
        if metric_id.startswith('builtin:tech.kafka'):
            dimension_definition = 'dt.entity.process_group_instance'
        else:
            if metric_id.startswith('ext:tech.MSSQL'):
                dimension_definition = 'dt.entity.custom_device'

    if mode == "build":
        tile['queries'][0]['splitBy'] = []
        if dimension_definition != 'dt.entity.none':
            tile['queries'][0]['splitBy'].append(dimension_definition)
    else:
        metric_selector = data_explorer_template['queries'][0]['metricSelector']
        metric_selector = metric_selector.replace('$$METRIC$$', metric_id)
        metric_selector = metric_selector.replace('$$SPLIT$$', dimension_definition)
        tile['queries'][0]['metricSelector'] = metric_selector

    return tile


def convert_entity_type_to_template_id(entity_type, entity_id):
    if entity_type == 'SERVICE':
        entity = select_entity_by_id(entity_id)
        service_type = entity.get('properties').get('serviceType')
        if service_type == 'DATABASE_SERVICE':
            return 'DATABASE'
        else:
            return 'SERVICE_VERSATILE'
    else:
        return None


def generate_entity_tile(top, left, entity_id, tile_dictionary):
    entity_type = entity_id.split('-', 1)[0]

    SUPPORTED_ENTITY_TYPES = {'SERVICE'}

    # SERVICE_VERSATILE|{"name": "", "tileType": "", "configured": false,
    # "bounds": {"top": 0, "left": 0, "width": 0, "height": 0}, "tileFilter": {"timeframe": null, "managementZone": null},
    # "assignedEntities": []}

    if entity_type in SUPPORTED_ENTITY_TYPES:
        template_id = convert_entity_type_to_template_id(entity_type, entity_id)
        entity_template = get_tile_template(template_id)
        tile = copy.deepcopy(entity_template)
        tile['bounds']['top'] = top
        tile['bounds']['left'] = left
        # tile['bounds']['width'] = 304
        # tile['bounds']['height'] = 304
        tile['name'] = tile_dictionary['name']
        tile['tileType'] = template_id
        # tile['configured'] = True
        tile['filterConfig'] = None
        tile['assignedEntities'] = [entity_id]
        return tile
    else:
        return None


def main():
    dashboard_controller = get_dashboard_controller()
    dashboard_template = get_dashboard_template()
    dashboard_counter = 0
    for dashboard_dictionary in dashboard_controller:
        # TODO: Remove temp code!!
        # Temp code to skip metrics dashboards for testing entities dashboards only
        # if dashboard_counter < 56:
        #    dashboard_counter += 1
        #    continue

        if dashboard_dictionary['process'] and dashboard_dictionary['tiles']:
            pass
        else:
            print(f'Skipping {dashboard_dictionary}')
            continue

        dashboard = copy.deepcopy(dashboard_template)
        dashboard['metadata']['configurationVersions'] = [3]
        dashboard['metadata']['clusterVersion'] = dashboard_dictionary['clusterVersion']
        dashboard_id = dashboard_dictionary['id']
        dashboard['id'] = dashboard_id
        dashboard_name = dashboard_dictionary['name']
        dashboard['dashboardMetadata']['name'] = dashboard_name
        share = dashboard_dictionary['share']
        # TODO: Update template with preset and other recent changes...
        # preset = dashboard_dictionary['preset']
        dashboard['dashboardMetadata']['shared'] = share
        dashboard['dashboardMetadata']['owner'] = dashboard_dictionary['owner']
        # dashboard['dashboardMetadata']['preset'] = preset
        dashboard['dashboardMetadata']['preset'] = share
        dashboard['dashboardMetadata']['tilesNameSize'] = 'small'
        dashboard['dashboardMetadata']['hasConsistentColors'] = True

        width = int(dashboard_dictionary['width'])
        height = int(dashboard_dictionary['height'])
        top = 0
        left = 0
        max_left = width - 304
        # This wii be off a bit for smaller tiles (like DATABASE_SERVICE) but not worth worrying about at this point...
        # We could adjust after every tile of entity type in the loop, but that seems absurd
        max_top = height - 304
        # Default to this size, but allow smaller tiles to override in the loop below...
        tile_height = 304
        tiles = []
        for tile_dictionary in dashboard_dictionary['tiles']:
            metric_id = tile_dictionary.get('metric', '')
            entity_id = tile_dictionary.get('entity', '')

            # Layout logic common to all tile types
            if left > max_left:
                top = top + tile_height
                left = 0
            if top > max_top:
                print('too many tiles... ' + dashboard_id)
                print('last metric was: ' + metric_id)
                break

            if metric_id:
                tile = ''
                if dashboard_name in USE_OLD_CHARTS:
                    tile = generate_metric_tile(top, left, metric_id, tile_dictionary)
                else:
                    if dashboard_name in USE_CODE_MODE_DATA_EXPLORER:
                        mode = "code"
                    else:
                        mode = "build"
                    tile = generate_new_metric_tile(top, left, metric_id, tile_dictionary, mode)
                if tile:
                    left += 304
                    tiles.append(tile)

            if entity_id:
                tile = generate_entity_tile(top, left, entity_id, tile_dictionary)
                # Some entities have smaller tiles to account for...
                tile_height = int(tile['bounds']['height'])
                print(tile)
                left += 304
                tiles.append(tile)

        dashboard['tiles'] = tiles

        outfile = dashboard_id + '.json'
        with open(outfile, 'w') as file:
            file.write(json.dumps(dashboard, indent=4))
            print(dashboard_id)
        dashboard_counter += 1


if __name__ == '__main__':
    main()
