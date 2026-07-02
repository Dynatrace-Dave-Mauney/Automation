#
# Generic selected file copy module.
#
# Currently configured for matching on JSON contents, but can be easily modified to process other file types,
#

import glob
import json
import os
import shutil
from json import JSONDecodeError
from pathlib import Path

# INPUT_PATH = '/Temp/builtinoneagent.features_input'
# OUTPUT_PATH = '/Temp/builtinoneagent.features_output'

# INPUT_PATH = '/Temp/builtinmanagement-zones'
# OUTPUT_PATH = '/Temp/builtinmanagement-zones-output'

INPUT_PATH = '../../Dashboards/Templates/Overview'
OUTPUT_PATH = '../../AI/Copilot/Dashboards/Generation/input_json'

confirmation_required = True
remove_directory_at_startup = True

# strings_of_interest = [
#     'SENSOR_DOTNET_LOG_ENRICHMENT',
#     'DOTNET_LOG_ENRICHMENT_UNSTRUCTURED',
#     'SENSOR_DOTNET_BIZEVENTS_HTTP_INCOMING',
#     'DOTNET_HTTP_TAGGING_SENSOR_V2',
#     'SENSOR_DOTNET_KAFKA',
#     'DOTNET_WCF_SENSOR_V2',
#     'SENSOR_APACHE_LOG_ENRICHMENT',
#     'NODE_JS_AMBIENT_SAMPLING_CAPTURING',
#     'ONEAGENT_CROSS_ENV_COORD_SAMPLING',
#     'ONEAGENT_CROSS_ENV_RESP_TAGGING',
#     'DOTNET_WCF_TAGGING',
#     'JAVA_RESOURCE_EXHAUSTED_EVENT_FORWARDING',
#     'DOTNET_ASPNETCORE_UEM',
#     'FRONTEND_AGENT_IMPROVED_SERVER_BALANCING',
#     'GO_LOG_ENRICHMENT',
#     'GO_SQL_PGX',
#     'GO_CASP_SOFTWARE_COMPONENTS',
#     'DOTNET_IN_PROC_TAGGING_V2',
#     'SENSOR_JAVA_LOG_ENRICHMENT',
#     'JAVA_LOG_ENRICHMENT_UNSTRUCTURED',
#     'JAVA_APACHE_HTTP_CLIENT_5',
#     'JAVA_KAFKA_STREAMS',
#     'JAVA_REACTOR3_CORE_TRACING',
#     'JAVA_UEM_INSTRUMENTATION',
#     'SENSOR_JAVA_CASP_FLAW_FINDER',
#     'JAVA_CASP_CALL_COUNTER',
#     'SENSOR_NGINX_LOG_ENRICHMENT',
#     'NODEJS_LOG_ENRICHMENT',
#     'SENSOR_NODEJS_KAFKAJS',
#     'NODEJS_ORACLEDB',
#     'NODEJS_WORKERTHREADS',
#     'SENSOR_DOTNET_OPENTELEMETRY',
#     'SENSOR_GO_OPENTELEMETRY',
#     'JAVA_OPENTELEMETRY',
#     'NODEJS_OPENTELEMETRY',
#     'SENSOR_PHP_OPENTELEMETRY',
#     'JAVA_OPENTELEMETRY_JAVA_INSTRUMENTATION_AGENT',
#     'JAVA_OPENTRACING_OVERRIDE',
#     'JAVA_OPENTRACING',
#     'JAVA_OPENTRACING_TRACERRESOLVER_OVERRIDE',
#     'SENSOR_PHP_LOG_ENRICHMENT',
#     'PHP_AUTOSENSOR_ALL_WORKERS',
#     'SENSOR_PHP_PREDIS',
#     'SENSOR_PHP_GRPC',
#     'JAVA_REACTOR_NETTY_HTTP_CLIENT',
#     'JAVA_SPRING_KAFKA',
#     'METRICS_ENRICHMENT_NON_INSTRUMENTED_TECH',
#     'SENSOR_WEBSERVER_BIZEVENTS_HTTP_INCOMING',
# ]

string_of_interest = 'PMTHB'


def copy_selected_files():
    confirm('Copy selected files from ' + INPUT_PATH + ' to ' + OUTPUT_PATH)
    initialize()

    for filename in glob.glob(INPUT_PATH + '/*'):
        if os.path.isfile(filename):
            process_file(filename)
        else:
            if os.path.isdir(filename):
                process_directory(filename)


def process_directory(path):
    for filename in glob.glob(path + '/*'):
        if os.path.isfile(filename):
            process_file(filename)
        else:
            if os.path.isdir(filename):
                process_directory(filename)


def process_file(filename):
    # print(f'Processing {filename}')

    with open(filename, 'r', encoding='utf-8') as f:
        if filename.endswith('.json'):
            infile_content = f.read()
            try:
                infile_content_json = json.loads(infile_content)

                # Copied from customize_dashboard_templates.py
                include_file_name_list = [
                    '00000000-dddd-bbbb-ffff-000000000001.json',  # Overview
                    # '00000000-dddd-bbbb-ffff-000000000001-v1.json',  # Overview
                    # '00000000-dddd-bbbb-ffff-000000000001-v2.json',  # Overview
                    # '00000000-dddd-bbbb-ffff-000000000001-v3.json',  # Overview
                    # '00000000-dddd-bbbb-ffff-000000000001-v4.json',  # Overview
                    # '00000000-dddd-bbbb-ffff-000000000001-v5.json',  # Overview
                    '00000000-dddd-bbbb-ffff-000000000002.json',  # Web Applications
                    '00000000-dddd-bbbb-ffff-000000000003.json',  # Mobile Applications
                    '00000000-dddd-bbbb-ffff-000000000004.json',  # Synthetics: Browser Monitors
                    '00000000-dddd-bbbb-ffff-000000000005.json',  # Synthetics: HTTP Monitors
                    '00000000-dddd-bbbb-ffff-000000000006.json',  # Services
                    '00000000-dddd-bbbb-ffff-000000000007.json',  # Databases
                    '00000000-dddd-bbbb-ffff-000000000008.json',  # Hosts
                    '00000000-dddd-bbbb-ffff-000000000009.json',  # Processes
                    '00000000-dddd-bbbb-ffff-000000000010.json',  # Java Monitoring
                    '00000000-dddd-bbbb-ffff-000000000011.json',  # .NET Monitoring
                    # '00000000-dddd-bbbb-ffff-000000000011-v1.json',  # .NET Monitoring
                    '00000000-dddd-bbbb-ffff-000000000012.json',  # Tomcat Monitoring
                    '00000000-dddd-bbbb-ffff-000000000013.json',  # Service Errors
                    '00000000-dddd-bbbb-ffff-000000000014.json',  # Service HTTP Errors
                    # '00000000-dddd-bbbb-ffff-000000000015.json',  # Service HTTP Errors from Non-Synthetics
                    # '00000000-dddd-bbbb-ffff-000000000016.json',  # Service HTTP Errors from Synthetics
                    '00000000-dddd-bbbb-ffff-000000000017.json',  # Key Requests
                    '00000000-dddd-bbbb-ffff-000000000018.json',  # Network (Host-Level Details)
                    '00000000-dddd-bbbb-ffff-000000000019.json',  # Network (Process-Level Details)
                    '00000000-dddd-bbbb-ffff-000000000020.json',  # Hosts (Detailed)
                    '00000000-dddd-bbbb-ffff-000000000021.json',  # Synthetics: Browser Monitor Events
                    '00000000-dddd-bbbb-ffff-000000000022.json',  # IBM WebSphere Metrics by Process
                    '00000000-dddd-bbbb-ffff-000000000023.json',  # IBM WebSphere Metrics by Pool
                    '00000000-dddd-bbbb-ffff-000000000024.json',  # IBM WebSphere Metrics by Process and Pool
                    '00000000-dddd-bbbb-ffff-000000000025.json',  # IBM MQ Metrics by Queue Manager
                    '00000000-dddd-bbbb-ffff-000000000026.json',  # IBM MQ Metrics by Best Split
                    '00000000-dddd-bbbb-ffff-000000000027.json',  # IBM MQ Metrics by Queue Manager and Best Split
                    # '00000000-dddd-bbbb-ffff-000000000028.json',  # IBM DataPower by Host
                    # '00000000-dddd-bbbb-ffff-000000000029.json',  # WebLogic by Name
                    # '00000000-dddd-bbbb-ffff-000000000030.json',  # WebLogic by Process
                    # '00000000-dddd-bbbb-ffff-000000000031.json',  # SAP Hana Database
                    # '00000000-dddd-bbbb-ffff-000000000032.json',  # IBM DataPower Overview
                    '00000000-dddd-bbbb-ffff-000000000033.json',  # Third Party Services
                    '00000000-dddd-bbbb-ffff-000000000034.json',  # Key User Actions
                    '00000000-dddd-bbbb-ffff-000000000035.json',  # Web Application Insights
                    '00000000-dddd-bbbb-ffff-000000000036.json',  # Queues
                    '00000000-dddd-bbbb-ffff-000000000037.json',  # Calls To Databases
                    # '00000000-dddd-bbbb-ffff-000000000038.json',  # Executor
                    '00000000-dddd-bbbb-ffff-000000000040.json',  # Application Overview - Home
                    '00000000-dddd-bbbb-ffff-000000000041.json',  # Application Overview (Web, Synthetics, and Services)
                    '00000000-dddd-bbbb-ffff-000000000042.json',
                    # Application Overview (Web, HTTP Monitors, and Services)
                    '00000000-dddd-bbbb-ffff-000000000043.json',  # Application Overview (Synthetics and Services)
                    '00000000-dddd-bbbb-ffff-000000000044.json',  # Application Overview (HTTP Monitors and Services)
                    '00000000-dddd-bbbb-ffff-000000000045.json',  # Application Overview (Services)
                    '00000000-dddd-bbbb-ffff-000000000046.json',  # Redis - Home
                    '00000000-dddd-bbbb-ffff-000000000047.json',  # Web Servers
                    # '00000000-dddd-bbbb-ffff-000000000047-v1.json',  # Web Servers
                    # '00000000-dddd-bbbb-ffff-000000000047-v2.json',  # Web Servers
                    '00000000-dddd-bbbb-ffff-000000000048.json',  # VMware
                    '00000000-dddd-bbbb-ffff-000000000050.json',  # F5 - Home
                    '00000000-dddd-bbbb-ffff-000000000051.json',  # F5 Connections
                    '00000000-dddd-bbbb-ffff-000000000052.json',  # F5 CPU/Memory/Disk
                    '00000000-dddd-bbbb-ffff-000000000053.json',  # F5 Pools/iRules/Misc
                    '00000000-dddd-bbbb-ffff-000000000054.json',  # F5 Requests
                    '00000000-dddd-bbbb-ffff-000000000058.json',  # IBM WebSphere Home
                    '00000000-dddd-bbbb-ffff-000000000060.json',  # Kafka
                    '00000000-dddd-bbbb-ffff-000000000067.json',  # Go
                    '00000000-dddd-bbbb-ffff-000000000068.json',  # IBM WebSphere Overview
                    '00000000-dddd-bbbb-ffff-000000000069.json',  # Node.js
                    # '00000000-dddd-bbbb-ffff-000000000070.json',  # Jetty
                    # '00000000-dddd-bbbb-ffff-000000000071.json',  # SOLR
                    # '00000000-dddd-bbbb-ffff-000000000072.json',  # Microsoft SQL Server
                    '00000000-dddd-bbbb-ffff-000000000073.json',  # Containers
                    '00000000-dddd-bbbb-ffff-000000000074.json',  # Suspicious Activity Audit
                    '00000000-dddd-bbbb-ffff-000000000075.json',  # Java Memory
                    '00000000-dddd-bbbb-ffff-000000000076.json',  # Full Stack Overview
                    # '00000000-dddd-bbbb-ffff-000000000077.json',  # Microsoft SQL Server - Home
                    # '00000000-dddd-bbbb-ffff-000000000077-v1.json',  # Microsoft SQL Server - Home
                    # '00000000-dddd-bbbb-ffff-000000000078.json',  # Microsoft SQL Server External Extension Metrics: Combined
                    # '00000000-dddd-bbbb-ffff-000000000078-v1.json',  # Microsoft SQL Server External Extension Metrics: Combined
                    # '00000000-dddd-bbbb-ffff-000000000079.json',  # Microsoft SQL Server External Extension Metrics: Transactions/Blocks/Locks/Latches
                    # '00000000-dddd-bbbb-ffff-000000000080.json',  # Microsoft SQL Server External Extension Metrics: CPU/Memory
                    # '00000000-dddd-bbbb-ffff-000000000081.json',  # Microsoft SQL Server External Extension Metrics: Redo/Checkpoint/Backup/Filestream
                    # '00000000-dddd-bbbb-ffff-000000000082-v1.json',  # Microsoft SQL Server External Extension Metrics: Log
                    # '00000000-dddd-bbbb-ffff-000000000083.json',  # Microsoft SQL Server External Extension Metrics: Health/State
                    # '00000000-dddd-bbbb-ffff-000000000084.json',  # Microsoft SQL Server External Extension Metrics: Always On
                    # '00000000-dddd-bbbb-ffff-000000000085.json',  # Microsoft SQL Server Databases
                    # '00000000-dddd-bbbb-ffff-000000000086.json',  # Microsoft SQL Server Online Databases
                    # '00000000-dddd-bbbb-ffff-000000000087.json',  # Microsoft SQL Server Offline Databases
                    # '00000000-dddd-bbbb-ffff-000000000088.json',  # Microsoft SQL Server Restoring Databases
                    # '00000000-dddd-bbbb-ffff-000000000089.json',  # Microsoft SQL Server Recovering Databases
                    '00000000-dddd-bbbb-ffff-000000000090.json',  # Oracle Database - Home
                    '00000000-dddd-bbbb-ffff-000000000091.json',  # Oracle Database: CPU/Memory
                    # '00000000-dddd-bbbb-ffff-000000000091-v1.json',  # Oracle Database: CPU/Memory
                    '00000000-dddd-bbbb-ffff-000000000092.json',  # Oracle Database: ASM/Space
                    # '00000000-dddd-bbbb-ffff-000000000092-v1.json',  # Oracle Database: ASM/Space
                    '00000000-dddd-bbbb-ffff-000000000093.json',  # Oracle Database: Redo Log/Reads/Writes
                    '00000000-dddd-bbbb-ffff-000000000094.json',  # Oracle Database: Times/Waits
                    '00000000-dddd-bbbb-ffff-000000000095.json',  # Oracle Database: Sessions/Users/Connections/Limits
                    # '00000000-dddd-bbbb-ffff-000000000095-v1.json',  # Oracle Database: Sessions/Users/Connections/Limits
                    '00000000-dddd-bbbb-ffff-000000000096.json',  # Oracle Database: Combined
                    # '00000000-dddd-bbbb-ffff-000000000096-v1.json',  # Oracle Database: Combined
                    '00000000-dddd-bbbb-ffff-000000000097.json',  # Oracle Database Host, Database, ASM Disk Lists
                    # '00000000-dddd-bbbb-ffff-000000000097-v1.json',  # Oracle Database Host, Database, ASM Disk Lists
                    # '00000000-dddd-bbbb-ffff-000000000098.json',  # Microsoft SQL Server
                    '00000000-dddd-bbbb-ffff-000000000100.json',  # Kubernetes - Home
                    '00000000-dddd-bbbb-ffff-000000000101.json',  # Kubernetes Overview (Simple)
                    '00000000-dddd-bbbb-ffff-000000000102.json',  # Kubernetes Overview
                    '00000000-dddd-bbbb-ffff-000000000103.json',  # Kubernetes Detailed Overview
                    '00000000-dddd-bbbb-ffff-000000000104.json',  # Kubernetes Monitoring Statistics
                    # '00000000-dddd-bbbb-ffff-000000000110.json',  # Azure - Home
                    # '00000000-dddd-bbbb-ffff-000000000111.json',  # Azure Monitoring Overview
                    '00000000-dddd-bbbb-ffff-000000000120.json',  # Monitoring Overview
                    '00000000-dddd-bbbb-ffff-000000000121.json',  # Backend Overview
                    # '00000000-dddd-bbbb-ffff-000000000122.json',  # DB2 - Home
                    # '00000000-dddd-bbbb-ffff-000000000123.json',  # DB2 Details
                    # '00000000-dddd-bbbb-ffff-000000000130.json',  # Google Cloud - Home
                    # '00000000-dddd-bbbb-ffff-000000000131.json',  # CICS
                    '00000000-dddd-bbbb-ffff-000000000132.json',  # Cloud Foundry
                    # '00000000-dddd-bbbb-ffff-000000000133.json',  # ControlM
                    # '00000000-dddd-bbbb-ffff-000000000134.json',  # HikariCP
                    '00000000-dddd-bbbb-ffff-000000000135.json',  # Microsoft Exchange
                    # '00000000-dddd-bbbb-ffff-000000000136.json',  # NGIS
                    # '00000000-dddd-bbbb-ffff-000000000137.json',  # R2DBC
                    # '00000000-dddd-bbbb-ffff-000000000138.json',  # Resilience4j
                    # '00000000-dddd-bbbb-ffff-000000000139.json',  # Snowflake
                    # '00000000-dddd-bbbb-ffff-000000000140.json',  # Spark
                    # '00000000-dddd-bbbb-ffff-000000000141.json',  # Spring
                    '00000000-dddd-bbbb-ffff-000000000142.json',  # IBM MQ Home
                    '00000000-dddd-bbbb-ffff-000000000143.json',  # IBM MQ Channel
                    '00000000-dddd-bbbb-ffff-000000000144.json',  # IBM MQ Func
                    '00000000-dddd-bbbb-ffff-000000000145.json',  # IBM MQ Listener
                    '00000000-dddd-bbbb-ffff-000000000146.json',  # IBM MQ Queue
                    '00000000-dddd-bbbb-ffff-000000000147.json',  # IBM MQ Topic
                    # '00000000-dddd-bbbb-ffff-000000000148.json',  # Custom PMI Metrics
                    # '00000000-dddd-bbbb-ffff-000000000159.json',  # NetApp OnTap
                    # '00000000-dddd-bbbb-ffff-000000000160.json',  # Pure Storage FlashArray
                    # '00000000-dddd-bbbb-ffff-000000000161.json',  # Veritas
                    # '00000000-dddd-bbbb-ffff-000000000170.json',  # VMware Overview
                    # '00000000-dddd-bbbb-ffff-000000000171.json',  # VMware Host
                    # '00000000-dddd-bbbb-ffff-000000000172.json',  # VMware VM
                    # '00000000-dddd-bbbb-ffff-000000000173.json',  # PHP
                    '00000000-dddd-bbbb-ffff-000000000174.json',  # Hosts: AIX
                    '00000000-dddd-bbbb-ffff-000000000175.json',  # Hosts: Linux
                    '00000000-dddd-bbbb-ffff-000000000176.json',  # Hosts: Windows
                    '00000000-dddd-bbbb-ffff-000000000177.json',  # Netscaler 1
                    '00000000-dddd-bbbb-ffff-000000000178.json',  # Netscaler 2
                    # '00000000-dddd-bbbb-ffff-000000000179.json',  # Citrix
                    '00000000-dddd-bbbb-ffff-000000000800.json',  # Administration
                    # '00000000-dddd-bbbb-ffff-000000000800-v1.json',  # Administration
                    # '00000000-dddd-bbbb-ffff-000000000800-v2.json',  # Administration
                    '00000000-dddd-bbbb-ffff-000000000801.json',  # Licensing Overview
                    '00000000-dddd-bbbb-ffff-000000000802.json',  # Host Units Overview
                    '00000000-dddd-bbbb-ffff-000000000803.json',  # DEM Units Overview
                    '00000000-dddd-bbbb-ffff-000000000804.json',  # DDU Overview
                    '00000000-dddd-bbbb-ffff-000000000805.json',  # Billing
                    '00000000-dddd-bbbb-ffff-000000000806.json',  # Dynatrace Self-Monitoring
                    '00000000-dddd-bbbb-ffff-000000000807.json',  # Host Health Breakdown
                    '00000000-dddd-bbbb-ffff-000000000808.json',  # 3rd Party XHR Detection
                    '00000000-dddd-bbbb-ffff-000000000809.json',  # Problem Notifications Health Overview
                    '00000000-dddd-bbbb-ffff-000000000810.json',  # OneAgent Health Overview
                    '00000000-dddd-bbbb-ffff-000000000811.json',  # DPS Usage Details
                    '00000000-dddd-bbbb-ffff-000000000812.json',  # Dynatrace Usage and Billing
                    '00000000-dddd-bbbb-ffff-000000000813.json',  # Management Zone Coverage
                    # '00000000-dddd-bbbb-ffff-000000000813-v1.json',  # Management Zone Coverage
                    '00000000-dddd-bbbb-ffff-000000000820.json',  # Dynatrace Self-Monitoring: Home
                    '00000000-dddd-bbbb-ffff-000000000821.json',  # Dynatrace Self-Monitoring: ActiveGate
                    # '00000000-dddd-bbbb-ffff-000000000821-v1.json',  # Dynatrace Self-Monitoring: ActiveGate
                    '00000000-dddd-bbbb-ffff-000000000822.json',  # Dynatrace Self-Monitoring: Server
                    # '00000000-dddd-bbbb-ffff-000000000822-v1.json',  # Dynatrace Self-Monitoring: Server
                    '00000000-dddd-bbbb-ffff-000000000823.json',  # Dynatrace Self-Monitoring: Extension
                    '00000000-dddd-bbbb-ffff-000000000824.json',  # Dynatrace Self-Monitoring: Extension Engine
                    '00000000-dddd-bbbb-ffff-000000000825.json',  # Dynatrace Self-Monitoring: Datasource
                    # '00000000-dddd-bbbb-ffff-000000000825-v1.json',  # Dynatrace Self-Monitoring: Datasource
                    '00000000-dddd-bbbb-ffff-000000000826.json',  # Dynatrace Self-Monitoring: Miscellaneous
                    # '00000000-dddd-bbbb-ffff-000000000826-v1.json',  # Dynatrace Self-Monitoring: Miscellaneous
                    '00000000-dddd-bbbb-ffff-000000000900.json',  # Detailed Drilldowns Menu
                    '00000000-dddd-bbbb-ffff-000000001000.json',  # AWS Home
                    '00000000-dddd-bbbb-ffff-000000001001.json',  # AWS CLB
                    '00000000-dddd-bbbb-ffff-000000001002.json',  # AWS DynamoDB
                    '00000000-dddd-bbbb-ffff-000000001003.json',  # AWS EBS
                    '00000000-dddd-bbbb-ffff-000000001004.json',  # AWS EC2
                    '00000000-dddd-bbbb-ffff-000000001005.json',  # AWS Lambda Functions
                    '00000000-dddd-bbbb-ffff-000000001006.json',  # AWS NLB
                    '00000000-dddd-bbbb-ffff-000000001007.json',  # AWS RDS
                    '00000000-dddd-bbbb-ffff-000000001008.json',  # AWS API Gateway
                    '00000000-dddd-bbbb-ffff-000000001009.json',  # AWS Cloudfront
                    '00000000-dddd-bbbb-ffff-000000001010.json',  # AWS CloudWatch Logs
                    '00000000-dddd-bbbb-ffff-000000001011.json',  # AWS Connect
                    '00000000-dddd-bbbb-ffff-000000001012.json',  # AWS ECS
                    '00000000-dddd-bbbb-ffff-000000001013.json',  # AWS ECS ContainerInsights
                    '00000000-dddd-bbbb-ffff-000000001014.json',  # AWS Lex
                    '00000000-dddd-bbbb-ffff-000000001015.json',  # AWS NAT Gateways
                    '00000000-dddd-bbbb-ffff-000000001016.json',  # AWS Route 53
                    '00000000-dddd-bbbb-ffff-000000001017.json',  # AWS Route 53 Resolver
                    '00000000-dddd-bbbb-ffff-000000001018.json',  # AWS Site-to-Site VPN
                    '00000000-dddd-bbbb-ffff-000000001019.json',  # AWS Kinesis Data Streams
                    '00000000-dddd-bbbb-ffff-000000001020.json',  # AWS Connect Details
                    '00000000-dddd-bbbb-ffff-000000001021.json',  # AWS EC2 Auto Scaling
                    '00000000-dddd-bbbb-ffff-000000001022.json',  # AWS DynamoDB Accelerator (DAX)
                    '00000000-dddd-bbbb-ffff-000000001023.json',  # AWS ALB
                    '00000000-dddd-bbbb-ffff-000000001024.json',  # AWS ES
                    '00000000-dddd-bbbb-ffff-000000001025.json',  # AWS SQS
                    '00000000-dddd-bbbb-ffff-000000001102.json',  # AWS API Gateway
                    '00000000-dddd-bbbb-ffff-000000001103.json',  # AWS AZ
                    '00000000-dddd-bbbb-ffff-000000001104.json',  # AWS Aurora
                    '00000000-dddd-bbbb-ffff-000000001105.json',  # AWS Auto Scaling
                    '00000000-dddd-bbbb-ffff-000000001106.json',  # AWS Cloudfront
                    '00000000-dddd-bbbb-ffff-000000001107.json',  # AWS EC
                    '00000000-dddd-bbbb-ffff-000000001108.json',  # AWS ECS
                    '00000000-dddd-bbbb-ffff-000000001109.json',  # AWS EFS
                    '00000000-dddd-bbbb-ffff-000000001110.json',  # AWS ES
                    '00000000-dddd-bbbb-ffff-000000001111.json',  # AWS Elastic Transcoder
                    '00000000-dddd-bbbb-ffff-000000001112.json',  # AWS Events
                    '00000000-dddd-bbbb-ffff-000000001113.json',  # AWS Kafka 1
                    '00000000-dddd-bbbb-ffff-000000001114.json',  # AWS Kafka 2
                    '00000000-dddd-bbbb-ffff-000000001115.json',  # AWS Kafka 3
                    '00000000-dddd-bbbb-ffff-000000001116.json',  # AWS Kafka 4
                    '00000000-dddd-bbbb-ffff-000000001117.json',  # AWS Lambda
                    '00000000-dddd-bbbb-ffff-000000001118.json',  # AWS Route 53
                    '00000000-dddd-bbbb-ffff-000000001119.json',  # AWS S3
                    '00000000-dddd-bbbb-ffff-000000001120.json',  # AWS SES
                    '00000000-dddd-bbbb-ffff-000000001121.json',  # AWS SNS
                    '00000000-dddd-bbbb-ffff-000000001122.json',  # AWS SQS
                    '00000000-dddd-bbbb-ffff-000000001123.json',  # AWS SSM Run Command
                    '00000000-dddd-bbbb-ffff-000000001124.json',  # AWS States
                    '00000000-dddd-bbbb-ffff-000000001125.json',  # AWS WAF
                    '00000000-dddd-bbbb-ffff-000000002000.json',  # Dynatrace-owned Dashboards

                    '00000000-dddd-bbbb-ffff-000000000180.json',  # Palo Alto Generic Device Extension
                    '00000000-dddd-bbbb-ffff-000000000181.json',  # Disk Extension
                    '00000000-dddd-bbbb-ffff-000000000182.json',  # SAN Storage
                    '00000000-dddd-bbbb-ffff-000000000183.json',  # IIS
                    '00000000-dddd-bbbb-ffff-000000000184.json',  # Github
                    '00000000-dddd-bbbb-ffff-000000000185.json',  # Active Directory
                    '00000000-dddd-bbbb-ffff-000000000186.json',  # Custom Devices
                    '00000000-dddd-bbbb-ffff-000000000187.json',  # Netracer
                    '00000000-dddd-bbbb-ffff-000000000188.json',  # F5 Extension 2
                    '00000000-dddd-bbbb-ffff-000000000189.json',  # F5 Extension 1
                    '00000000-dddd-bbbb-ffff-000000000190.json',  # F5 Extension 3
                    '00000000-dddd-bbbb-ffff-000000000191.json',  # Log Metrics
                    '00000000-dddd-bbbb-ffff-000000000192.json',  # Scrape
                    '00000000-dddd-bbbb-ffff-000000000193.json',  # JFrog
                    '00000000-dddd-bbbb-ffff-000000000194.json',  # Airflow Dividend
                    '00000000-dddd-bbbb-ffff-000000000195.json',  # Cohesity Backup
                    '00000000-dddd-bbbb-ffff-000000000196.json',  # NAS Storage
                    '00000000-dddd-bbbb-ffff-000000000197.json',  # Splunk Cloud
                    '00000000-dddd-bbbb-ffff-000000000198.json',  # OS Service
                    '00000000-dddd-bbbb-ffff-000000000199.json',  # PostgreSQL
                    '00000000-dddd-bbbb-ffff-000000000200.json',  # Network Device Extension
                    '00000000-dddd-bbbb-ffff-000000000201.json',  # Raft Proxy 1
                    '00000000-dddd-bbbb-ffff-000000000202.json',  # Raft Proxy 2
                    '00000000-dddd-bbbb-ffff-000000001026.json',  # AWS Sagemaker
                    '00000000-dddd-bbbb-ffff-000000001027.json',  # AWS Textract
                    '00000000-dddd-bbbb-ffff-000000001028.json',  # AWS Logs
                    '00000000-dddd-bbbb-ffff-000000001029.json',  # AWS Amazon MQ
                    '00000000-dddd-bbbb-ffff-000000001030.json',  # AWS Usage
                    '00000000-dddd-bbbb-ffff-000000001031.json',  # AWS Kinesis Data Firehose
                    '00000000-dddd-bbbb-ffff-000000001032.json',  # AWS RDS 2
                ]

                # if "'id': '00000000-dddd-bbbb-ffff-000000000009'" not in str(infile_content_json):
                #     return

                # print(infile_content_json)

                match = False

                # tiles = infile_content_json.get('tiles')
                # for tile in tiles:
                #     if "'metricSelector': " in str(tile):
                #         if "'metricSelector': None" not in str(tile):
                #             print(tile)
                #             match = True

                # dashboard_id = infile_content_json.get('id')
                # print(dashboard_id)
                # if f'{dashboard_id}.json' in include_file_name_list:
                path = Path(filename)
                print(path.name)
                if path.name in include_file_name_list:
                    match = True

                if match:
                    output_filename = f'{OUTPUT_PATH}/{os.path.basename(filename)}'
                    with open(output_filename, 'w', encoding='utf-8') as outfile:
                        # To pretty print JSON:
                        # outfile.write(json.dumps(infile_content_json, indent=4, sort_keys=False))
                        # To write file as is
                        outfile.write(infile_content)
            except JSONDecodeError:
                print(f'Skipping due to non-JSON file content: {filename}')
        else:
            print(f'Skipping due to non-JSON file type: {filename}')


def initialize():
    if remove_directory_at_startup:
        confirm('The ' + OUTPUT_PATH + ' directory will now be removed to prepare for the conversion.')
        remove_directory(OUTPUT_PATH)

    if not os.path.isdir(OUTPUT_PATH):
        make_directory(OUTPUT_PATH)


def remove_directory(path):
    try:
        shutil.rmtree(path, ignore_errors=False)

    except OSError:
        print('Directory %s does not exist' % path)
    else:
        print('Removed the directory %s ' % path)


def make_directory(path):
    try:
        os.makedirs(path)
    except OSError:
        print('Creation of the directory %s failed' % path)
        exit()
    else:
        print('Successfully created the directory %s ' % path)


def confirm(message):
    if confirmation_required:
        proceed = input('%s (Y/n) ' % message).upper() == 'Y'
        if not proceed:
            print('Operation aborted')
            exit()


def main():
    copy_selected_files()


if __name__ == '__main__':
    main()
