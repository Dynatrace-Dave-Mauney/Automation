import copy
import glob
import json
import os
import shutil
import yaml
from inspect import currentframe

from Reuse import dynatrace_api

env_name = 'Prod'
# env_name = 'NonProd'
# env_name = 'Sandbyox'
# env_name = 'Personal'
# env_name = 'Demo'

# OLD:
# env_name = 'Upper'
# env_name = 'Lower'
# env_name = 'PreProd'
# env_name = 'Dev'

tenant = os.getenv(f'DYNATRACE_{env_name.upper()}_TENANT')
env = f'https://{tenant}.live.dynatrace.com'
token = os.getenv(f'DYNATRACE_AUTOMATION_REPORTING_{env_name.upper()}_TOKEN')

PREFIX = f'{env_name}:'
DASHBOARD_CUSTOM_PATH = f'Custom/Overview-{env_name}'
DASHBOARD_TEMPLATE_PATH = 'Templates/Overview'

OWNER = os.environ.get('DYNATRACE_DASHBOARD_OWNER', 'nobody@example.com')
# OWNER = 'nobody@example.com'
# OWNER = 'dave.mauney@dynatrace.com'

SHARED = True
PRESET = True
MENU_PRESET = True

skip_file_name_list = [
    '00000000-dddd-bbbb-ffff-000000000001.json',
    '00000000-dddd-bbbb-ffff-000000000001-v1.json',
    '00000000-dddd-bbbb-ffff-000000000001-v2.json',
    '00000000-dddd-bbbb-ffff-000000000001-v2a.json',
    '00000000-dddd-bbbb-ffff-000000000001-v3.json',
    '00000000-dddd-bbbb-ffff-000000000001-v3a.json',
    '00000000-dddd-bbbb-ffff-000000000001-v3b.json',
    '00000000-dddd-bbbb-ffff-000000000001-v3c.json',
    '00000000-dddd-bbbb-ffff-000000000001-v4_Lower.json',
    '00000000-dddd-bbbb-ffff-000000000001-v4_Upper.json',
    '00000000-dddd-bbbb-ffff-000000000014-v1.json',
    '00000000-dddd-bbbb-ffff-000000000015.json',
    '00000000-dddd-bbbb-ffff-000000000016.json',
    '00000000-dddd-bbbb-ffff-000000000025.json',
    '00000000-dddd-bbbb-ffff-000000000026.json',
    '00000000-dddd-bbbb-ffff-000000000027.json',
    '00000000-dddd-bbbb-ffff-000000000028.json',
    '00000000-dddd-bbbb-ffff-000000000029.json',
    '00000000-dddd-bbbb-ffff-000000000030.json',
    '00000000-dddd-bbbb-ffff-000000000031.json',
    '00000000-dddd-bbbb-ffff-000000000032.json',
    '00000000-dddd-bbbb-ffff-000000000046.json',
    '00000000-dddd-bbbb-ffff-000000000060.json',
    '00000000-dddd-bbbb-ffff-000000000061.json',
    '00000000-dddd-bbbb-ffff-000000000062.json',
    '00000000-dddd-bbbb-ffff-000000000063.json',
    '00000000-dddd-bbbb-ffff-000000000064.json',
    '00000000-dddd-bbbb-ffff-000000000065.json',
    '00000000-dddd-bbbb-ffff-000000000066.json',
    '00000000-dddd-bbbb-ffff-000000000071.json',
    '00000000-dddd-bbbb-ffff-000000000072.json',
    '00000000-dddd-bbbb-ffff-000000000077.json',
    '00000000-dddd-bbbb-ffff-000000000078.json',
    '00000000-dddd-bbbb-ffff-000000000079.json',
    '00000000-dddd-bbbb-ffff-000000000080.json',
    '00000000-dddd-bbbb-ffff-000000000081.json',
    '00000000-dddd-bbbb-ffff-000000000082.json',
    '00000000-dddd-bbbb-ffff-000000000083.json',
    '00000000-dddd-bbbb-ffff-000000000084.json',
    '00000000-dddd-bbbb-ffff-000000000085.json',
    '00000000-dddd-bbbb-ffff-000000000086.json',
    '00000000-dddd-bbbb-ffff-000000000087.json',
    '00000000-dddd-bbbb-ffff-000000000088.json',
    '00000000-dddd-bbbb-ffff-000000000089.json',
    '00000000-dddd-bbbb-ffff-000000000090.json',
    '00000000-dddd-bbbb-ffff-000000000091.json',
    '00000000-dddd-bbbb-ffff-000000000092.json',
    '00000000-dddd-bbbb-ffff-000000000093.json',
    '00000000-dddd-bbbb-ffff-000000000094.json',
    '00000000-dddd-bbbb-ffff-000000000095.json',
    '00000000-dddd-bbbb-ffff-000000000096.json',
    '00000000-dddd-bbbb-ffff-000000000097.json',
    '00000000-dddd-bbbb-ffff-000000000110.json',
    '00000000-dddd-bbbb-ffff-000000000110-v1.json',
    '00000000-dddd-bbbb-ffff-000000000111.json',
    '00000000-dddd-bbbb-ffff-000000000130.json',
    '00000000-dddd-bbbb-ffff-000000000800.json',
    '00000000-dddd-bbbb-ffff-000000000800-v1.json',
    '00000000-dddd-bbbb-ffff-000000000800-v2.json',
    '00000000-dddd-bbbb-ffff-000000000800-v3_BACKUP.json',
    '00000000-dddd-bbbb-ffff-000000000800-v3_BACKUP2.json',
    '00000000-dddd-bbbb-ffff-000000000806.json',
    '00000000-dddd-bbbb-ffff-000000000807.json',
    '00000000-dddd-bbbb-ffff-000000000900.json',
    '00000000-dddd-bbbb-ffff-000000000900-v1.json',
    '00000000-dddd-bbbb-ffff-000000001001.json',
    '00000000-dddd-bbbb-ffff-000000001002.json',
    '00000000-dddd-bbbb-ffff-000000001003.json',
    '00000000-dddd-bbbb-ffff-000000001004.json',
    '00000000-dddd-bbbb-ffff-000000001005.json',
    '00000000-dddd-bbbb-ffff-000000001006.json',
    '00000000-dddd-bbbb-ffff-000000001007.json',
    '00000000-dddd-bbbb-ffff-000000001008.json',
    '00000000-dddd-bbbb-ffff-000000001009.json',
    '00000000-dddd-bbbb-ffff-000000001010.json',
    '00000000-dddd-bbbb-ffff-000000001011.json',
    '00000000-dddd-bbbb-ffff-000000001012.json',
    '00000000-dddd-bbbb-ffff-000000001013.json',
    '00000000-dddd-bbbb-ffff-000000001014.json',
    '00000000-dddd-bbbb-ffff-000000001015.json',
    '00000000-dddd-bbbb-ffff-000000001016.json',
    '00000000-dddd-bbbb-ffff-000000001017.json',
    '00000000-dddd-bbbb-ffff-000000001018.json',
    '00000000-dddd-bbbb-ffff-000000001019.json',
    '00000000-dddd-bbbb-ffff-000000001020.json',
    '00000000-dddd-bbbb-ffff-000000001021.json',
    '00000000-dddd-bbbb-ffff-000000001022.json',
    '00000000-dddd-bbbb-ffff-000000001023.json',
    '00000000-dddd-bbbb-ffff-000000001024.json',
    '00000000-dddd-bbbb-ffff-000000001025.json',

]

# Used when no API token was available, so ID renames were done
# DASHBOARD_TEMPLATE_PATH = 'Templates/Overview-Customer2-NonProd'
# DASHBOARD_TEMPLATE_PATH = 'Templates/Overview-Customer2-Prod'

# Typical Names
# WEB_APPLICATION_TAGS = ['Environment', 'Application', 'Web Application Name']
# SERVICE_TAGS = ['Application', 'Environment', 'Host Group', 'IIS App Pool', 'Kubernetes Base Pod Name', 'Kubernetes Cluster', 'Kubernetes Container Name', 'Kubernetes Namespace', 'OS', 'Service Name']
# DATABASE_SERVICE_TAGS = ['Application', 'Environment', 'Service Name']
# PROCESS_GROUP_TAGS = ['Process Group Name', 'Environment', 'HostGroup', 'Application', 'IIS App Pool', 'Kubernetes Base Pod Name', 'Kubernetes Cluster', 'Kubernetes Container Name', 'Kubernetes Namespace', 'OS']
# HOST_TAGS = ['Application', 'Environment', 'Host Group', 'Host Name', 'IIS App Pool', 'IP', 'Kubernetes Cluster', 'Kubernetes Namespace']
# KUBERNETES_TAGS = ['Kubernetes Base Pod Name', 'Kubernetes Cluster', 'Kubernetes Container Name', 'Kubernetes Namespace']
# IIS_TAGS = ['IIS App Pool']

# Customer Specific Tags with "BETA" prefix
# WEB_APPLICATION_TAGS = ['Application', 'Company', 'Environment', 'BETA Web Application Name']
# SERVICE_TAGS = ['Application', 'Company', 'Environment', 'BETA Service Name', 'BETA AWS Availability Zone', 'BETA Apache Config Path', 'BETA Asp Dot Net Core Application Path', 'BETA Catalina Base', 'BETA Catalina Home', 'BETA Cloud Provider', 'BETA Command Line Args', 'BETA Data Center', 'BETA Dot Net Command', 'BETA Dot Net Command Path', 'BETA Exe Name', 'BETA Exe Path', 'BETA Geolocation', 'BETA Host CPU Cores', 'BETA Host Group', 'BETA Host Name', 'BETA IBM Integration Node Name', 'BETA IBM Integration Server Name', 'BETA IIS App Pool', 'BETA IP Address', 'BETA Java Jar File', 'BETA Java Jar Path', 'BETA Kubernetes Base Pod Name', 'BETA Kubernetes Cluster', 'BETA Kubernetes Container Name', 'BETA Kubernetes Full Pod Name', 'BETA Kubernetes Namespace', 'BETA Kubernetes Pod UID', 'BETA Node JS Script Name', 'BETA NodeJS App Base Director', 'BETA NodeJS App Name', 'BETA OS', 'BETA Process Group Name', 'BETA SpringBootAppName', 'BETA SpringBootProfileName', 'BETA SpringBootStartupClass', 'BETA Technology', 'BETA VMWare Data Center Name', 'BETA VMWare VM Name', 'BETA Web Application ID', 'BETA Web Context Root', 'BETA Web Server Name', 'BETA Web Service Name', 'BETA Web Service Namespace', 'BETA WebLogic Cluster', 'BETA WebLogic Domain', 'BETA WebLogic Home', 'BETA WebLogic Name', 'BETA WebSphere Cell', 'BETA WebSphere Cluster', 'BETA WebSphere Node', 'BETA WebSphere Server']
# DATABASE_SERVICE_TAGS = ['DATABASE_VENDOR', 'SERVICE_TYPE', 'Application', 'Company', 'Environment', 'BETA Service Name', 'BETA Database Vendor']
# PROCESS_GROUP_TAGS = ['Application', 'Company', 'Environment', 'BETA Process Group Name', 'BETA AWS Availability Zone', 'BETA Apache Config Path', 'BETA Asp Dot Net Core Application Path', 'BETA Catalina Base', 'BETA Catalina Home', 'BETA Cloud Provider', 'BETA Command Line Args', 'BETA Data Center', 'BETA Dot Net Command', 'BETA Dot Net Command Path', 'BETA Exe Name', 'BETA Exe Path', 'BETA Geolocation', 'BETA Host CPU Cores', 'BETA Host Group', 'BETA Host Name', 'BETA IBM Integration Node Name', 'BETA IBM Integration Server Name', 'BETA IIS App Pool', 'BETA IP Address', 'BETA Java Jar File', 'BETA Java Jar Path', 'BETA Kubernetes Base Pod Name', 'BETA Kubernetes Cluster', 'BETA Kubernetes Container Name', 'BETA Kubernetes Full Pod Name', 'BETA Kubernetes Namespace', 'BETA Kubernetes Pod UID', 'BETA Node JS Script Name', 'BETA NodeJS App Base Director', 'BETA NodeJS App Name', 'BETA OS', 'BETA Process Group Name', 'BETA SpringBootAppName', 'BETA SpringBootProfileName', 'BETA SpringBootStartupClass', 'BETA Technology', 'BETA VMWare Data Center Name', 'BETA VMWare VM Name', 'BETA Web Application ID', 'BETA Web Context Root', 'BETA Web Server Name', 'BETA Web Service Name', 'BETA Web Service Namespace', 'BETA WebLogic Cluster', 'BETA WebLogic Domain', 'BETA WebLogic Home', 'BETA WebLogic Name', 'BETA WebSphere Cell', 'BETA WebSphere Cluster', 'BETA WebSphere Node', 'BETA WebSphere Server']
# HOST_TAGS = ['HOST_MONITORING_MODE', 'HOST_VIRTUALIZATION_TYPE', 'OS_TYPE', 'Application', 'Company', 'Environment', 'BETA AWS Availability Zone', 'BETA Apache Config Path', 'BETA Asp Dot Net Core Application Path', 'BETA Catalina Base', 'BETA Catalina Home', 'BETA Cloud Provider', 'BETA Command Line Args', 'BETA Data Center', 'BETA Dot Net Command', 'BETA Dot Net Command Path', 'BETA Exe Name', 'BETA Exe Path', 'BETA Geolocation', 'BETA Host CPU Cores', 'BETA Host Group', 'BETA Host Name', 'BETA IBM Integration Node Name', 'BETA IBM Integration Server Name', 'BETA IIS App Pool', 'BETA IP Address', 'BETA Java Jar File', 'BETA Java Jar Path', 'BETA Kubernetes Base Pod Name', 'BETA Kubernetes Cluster', 'BETA Kubernetes Container Name', 'BETA Kubernetes Full Pod Name', 'BETA Kubernetes Namespace', 'BETA Kubernetes Pod UID', 'BETA Node JS Script Name', 'BETA NodeJS App Base Director', 'BETA NodeJS App Name', 'BETA OS', 'BETA Process Group Name', 'BETA SpringBootAppName', 'BETA SpringBootProfileName', 'BETA SpringBootStartupClass', 'BETA Technology', 'BETA VMWare Data Center Name', 'BETA VMWare VM Name', 'BETA Web Application ID', 'BETA Web Context Root', 'BETA Web Server Name', 'BETA Web Service Name', 'BETA Web Service Namespace', 'BETA WebLogic Cluster', 'BETA WebLogic Domain', 'BETA WebLogic Home', 'BETA WebLogic Name', 'BETA WebSphere Cell', 'BETA WebSphere Cluster', 'BETA WebSphere Node', 'BETA WebSphere Server']
# KUBERNETES_TAGS = ['Kubernetes Base Pod Name', 'Kubernetes Cluster', 'Kubernetes Container Name', 'Kubernetes Namespace']
# IIS_TAGS = ['IIS App Pool']

# Customer1-Specific Tags with no prefix
# WEB_APPLICATION_TAGS = ['Application', 'Company', 'Environment', 'Web Application Name']
# SERVICE_TAGS = ['Application', 'Company', 'Environment', 'Service Name', 'AWS Availability Zone', 'Apache Config Path', 'Asp Dot Net Core Application Path', 'Catalina Base', 'Catalina Home', 'Cloud Provider', 'Command Line Args', 'Data Center', 'Dot Net Command', 'Dot Net Command Path', 'Exe Name', 'Exe Path', 'Geolocation', 'Host CPU Cores', 'Host Group', 'Host Name', 'IBM Integration Node Name', 'IBM Integration Server Name', 'IIS App Pool', 'IP Address', 'Java Jar File', 'Java Jar Path', 'Kubernetes Base Pod Name', 'Kubernetes Cluster', 'Kubernetes Container Name', 'Kubernetes Full Pod Name', 'Kubernetes Namespace', 'Kubernetes Pod UID', 'Node JS Script Name', 'NodeJS App Base Director', 'NodeJS App Name', 'OS', 'Process Group Name', 'SpringBootAppName', 'SpringBootProfileName', 'SpringBootStartupClass', 'Technology', 'VMWare Data Center Name', 'VMWare VM Name', 'Web Application ID', 'Web Context Root', 'Web Server Name', 'Web Service Name', 'Web Service Namespace', 'WebLogic Cluster', 'WebLogic Domain', 'WebLogic Home', 'WebLogic Name', 'WebSphere Cell', 'WebSphere Cluster', 'WebSphere Node', 'WebSphere Server']
# DATABASE_SERVICE_TAGS = ['DATABASE_VENDOR', 'SERVICE_TYPE', 'Application', 'Company', 'Environment', 'Service Name', 'Database Vendor']
# PROCESS_GROUP_TAGS = ['Application', 'Company', 'Environment', 'Process Group Name', 'AWS Availability Zone', 'Apache Config Path', 'Asp Dot Net Core Application Path', 'Catalina Base', 'Catalina Home', 'Cloud Provider', 'Command Line Args', 'Data Center', 'Dot Net Command', 'Dot Net Command Path', 'Exe Name', 'Exe Path', 'Geolocation', 'Host CPU Cores', 'Host Group', 'Host Name', 'IBM Integration Node Name', 'IBM Integration Server Name', 'IIS App Pool', 'IP Address', 'Java Jar File', 'Java Jar Path', 'Kubernetes Base Pod Name', 'Kubernetes Cluster', 'Kubernetes Container Name', 'Kubernetes Full Pod Name', 'Kubernetes Namespace', 'Kubernetes Pod UID', 'Node JS Script Name', 'NodeJS App Base Director', 'NodeJS App Name', 'OS', 'Process Group Name', 'SpringBootAppName', 'SpringBootProfileName', 'SpringBootStartupClass', 'Technology', 'VMWare Data Center Name', 'VMWare VM Name', 'Web Application ID', 'Web Context Root', 'Web Server Name', 'Web Service Name', 'Web Service Namespace', 'WebLogic Cluster', 'WebLogic Domain', 'WebLogic Home', 'WebLogic Name', 'WebSphere Cell', 'WebSphere Cluster', 'WebSphere Node', 'WebSphere Server']
# HOST_TAGS = ['HOST_MONITORING_MODE', 'HOST_VIRTUALIZATION_TYPE', 'OS_TYPE', 'Application', 'Company', 'Environment', 'AWS Availability Zone', 'Apache Config Path', 'Asp Dot Net Core Application Path', 'Catalina Base', 'Catalina Home', 'Cloud Provider', 'Command Line Args', 'Data Center', 'Dot Net Command', 'Dot Net Command Path', 'Exe Name', 'Exe Path', 'Geolocation', 'Host CPU Cores', 'Host Group', 'Host Name', 'IBM Integration Node Name', 'IBM Integration Server Name', 'IIS App Pool', 'IP Address', 'Java Jar File', 'Java Jar Path', 'Kubernetes Base Pod Name', 'Kubernetes Cluster', 'Kubernetes Container Name', 'Kubernetes Full Pod Name', 'Kubernetes Namespace', 'Kubernetes Pod UID', 'Node JS Script Name', 'NodeJS App Base Director', 'NodeJS App Name', 'OS', 'Process Group Name', 'SpringBootAppName', 'SpringBootProfileName', 'SpringBootStartupClass', 'Technology', 'VMWare Data Center Name', 'VMWare VM Name', 'Web Application ID', 'Web Context Root', 'Web Server Name', 'Web Service Name', 'Web Service Namespace', 'WebLogic Cluster', 'WebLogic Domain', 'WebLogic Home', 'WebLogic Name', 'WebSphere Cell', 'WebSphere Cluster', 'WebSphere Node', 'WebSphere Server']
# KUBERNETES_TAGS = ['Kubernetes Base Pod Name', 'Kubernetes Cluster', 'Kubernetes Container Name', 'Kubernetes Namespace']
# IIS_TAGS = ['IIS App Pool']

# Demo-specific Tags with no prefix
# WEB_APPLICATION_TAGS = ['CloudAutomation Application', 'ET Angular', 'EasyTravel', 'ServiceNow']
# SERVICE_TAGS = ['[Environment]DT_RELEASE_BUILD_VERSION', '[Environment]DT_RELEASE_PRODUCT', '[Environment]DT_RELEASE_STAGE', '[Environment]DT_RELEASE_VERSION', '[Environment]easyTravel', '[Environment]MikesStuff', '[Kubernetes]apiserver', '[Kubernetes]app', '[Kubernetes]app.kubernetes.io/instance', '[Kubernetes]app.kubernetes.io/managed-by', '[Kubernetes]app.kubernetes.io/name', '[Kubernetes]app.kubernetes.io/part-of', '[Kubernetes]app.kubernetes.io/version', '[Kubernetes]component', '[Kubernetes]controller-manager', '[Kubernetes]controller-revision-hash', '[Kubernetes]k8s-app', '[Kubernetes]name', '[Kubernetes]namespace', '[Kubernetes]oauth-apiserver-anti-affinity', '[Kubernetes]oauth-openshift-anti-affinity', '[Kubernetes]openshift.io/component', '[Kubernetes]pod-template-generation', '[Kubernetes]revision', '[Kubernetes]security.istio.io/tlsMode', '[Kubernetes]service.istio.io/canonical-name', '[Kubernetes]service.istio.io/canonical-revision', '[Kubernetes]skaffold.dev/run-id', '[Kubernetes]type', 'Azure', 'classic-eval', 'CloudAutomation Application', 'CloudAutomation EasyTravel', 'CloudAutomation Stage', 'easytravel', 'easytravel-app', 'k8s-namespace', 'keptn_deployment', 'keptn_managed', 'keptn_project', 'keptn_service', 'keptn_stage', 'mainframe', 'OpenShift', 'OpenTelemetry', 'slo_authenticationservice', 'slo_bookingservice', 'slo_checkdestinationservice', 'slo_creditcardservice', 'slo_easytravelwebserver:9079', 'slo_journeyservice']
# DATABASE_SERVICE_TAGS = ['[Kubernetes]namespace', 'CloudAutomation EasyTravel', 'CloudAutomation Stage', 'k8s-namespace', 'keptn_managed', 'mainframe', 'OpenShift']
# PROCESS_GROUP_TAGS = ['[Environment]DT_RELEASE_BUILD_VERSION', '[Environment]DT_RELEASE_PRODUCT', '[Environment]DT_RELEASE_STAGE', '[Environment]DT_RELEASE_VERSION', '[Kubernetes]apiserver', '[Kubernetes]app', '[Kubernetes]app.kubernetes.io/component', '[Kubernetes]app.kubernetes.io/instance', '[Kubernetes]app.kubernetes.io/managed-by', '[Kubernetes]app.kubernetes.io/name', '[Kubernetes]app.kubernetes.io/part-of', '[Kubernetes]app.kubernetes.io/version', '[Kubernetes]component', '[Kubernetes]controller-manager', '[Kubernetes]controller-revision-hash', '[Kubernetes]internal.dynatrace.com/app', '[Kubernetes]internal.dynatrace.com/component', '[Kubernetes]k8s-app', '[Kubernetes]name', '[Kubernetes]namespace', '[Kubernetes]oauth-apiserver-anti-affinity', '[Kubernetes]oauth-openshift-anti-affinity', '[Kubernetes]openshift.io/component', '[Kubernetes]pod-template-generation', '[Kubernetes]revision', '[Kubernetes]security.istio.io/tlsMode', '[Kubernetes]service.istio.io/canonical-name', '[Kubernetes]service.istio.io/canonical-revision', '[Kubernetes]skaffold.dev/run-id', '[Kubernetes]type', 'AppSec', 'at-pg-tag', 'BOSH-managed VM', 'CFAppID', 'Citrix', 'CloudAutomation Application', 'CloudAutomation EasyTravel', 'CloudAutomation Stage', 'k8s-namespace', 'keptn_deployment', 'keptn_managed', 'keptn_project', 'keptn_service', 'keptn_stage', 'mainframe']
# HOST_TAGS = ['[AWS]ACE:CREATED-BY', '[AWS]APL.Deployment', '[AWS]APL.Deployment  ', '[AWS]APL.Environment', '[AWS]APL.Environment    ', '[AWS]APL.Status', '[AWS]aws:autoscaling:groupName', '[AWS]aws:ec2:fleet-id', '[AWS]aws:ec2launchtemplate:id', '[AWS]aws:ec2launchtemplate:version', '[AWS]aws:eks:cluster-name', '[AWS]Capability', '[AWS]Category', '[AWS]created_at', '[AWS]deployment', '[AWS]detail_usage', '[AWS]DetailUsage', '[AWS]director', '[AWS]eks:cluster-name', '[AWS]eks:nodegroup-name', '[AWS]Email', '[AWS]id', '[AWS]index', '[AWS]instance_group', '[AWS]job', '[AWS]k8s.io/cluster-autoscaler/aws-eks-1', '[AWS]k8s.io/cluster-autoscaler/enabled', '[AWS]kubernetes.io/cluster/aws-eks-1', '[AWS]monitor_demo1', '[AWS]monitor_demo2', '[AWS]MonitoredBy', '[AWS]Name', '[AWS]ShouldBeReserved', '[AWS]Usage', '[Azure]ACE', '[Azure]ACE:CREATED-BY', '[Azure]ACE:UPDATED-BY', '[Azure]Category', '[Azure]etRole', '[Azure]ipRole', '[Azure]Owner', '[Azure]ShouldBeReserved', '[Azure]System.Collections.Hashtable', '[Azure]tenant:CustomerA', '[Azure]testEnvRole', '[Environment]cf', '[Environment]team', '[GoogleCloud]demo1-prometheus', '[GoogleCloud]gke-alfa-3a67ff15-node', '[GoogleCloud]gke-beta-7b734083-node', '[GoogleCloud]gke-ext-demo1-505a225a-node', '[GoogleCloud]gke-keptn-demo1-b3a0cade-node', '[GoogleCloud]web', '[GoogleCloud]weblauncher', 'AppSec', 'at-host-group', 'Avengers', 'Azure', 'BOSH-managed VM', 'CF Tag', 'Citrix', 'CloudAutomation Application', 'CloudAutomation EasyTravel', 'CloudAutomation Stage', 'HostName', 'keptn_managed', 'mainframe', 'owner', 'ServiceNow']
# KUBERNETES_TAGS = ['Kubernetes', 'k8s-namespace']
# IIS_TAGS = []

# Customer2-Prod-specific Tags with no prefix
WEB_APPLICATION_TAGS = []
SERVICE_TAGS = [
    'Kubernetes Cluster',
    'Kubernetes Base Pod Name',
    'Kubernetes Container Name',
    'Kubernetes Full Pod Name',
    'Kubernetes Namespace',
    'Kubernetes Pod UID',
    '[Kubernetes]app',
    '[Kubernetes]appCode',
    '[Kubernetes]aspnetcoreEnvironment',
    '[Kubernetes]buildbranchName',
    '[Kubernetes]buildbuildNumber',
    '[Kubernetes]buildgitCommit',
    '[Kubernetes]buildRepository',
    '[Kubernetes]controller-revision-hash',
    '[Kubernetes]helm-revision',
    '[Kubernetes]imageName',
    '[Kubernetes]imageRegistry',
    '[Kubernetes]imageRepository',
    '[Kubernetes]imageTag',
    '[Kubernetes]k8s-app',
    '[Kubernetes]pod-template-generation',
    '[Kubernetes]releasebranchName',
    '[Kubernetes]releasebuildNumber',
    '[Kubernetes]releasegitCommit',
    '[Kubernetes]releaseName',
    '[Kubernetes]releaseRepository',
    '[Kubernetes]security.istio.io/tlsMode',
    '[Kubernetes]service.istio.io/canonical-name',
    '[Kubernetes]service.istio.io/canonical-revision',
    '[Kubernetes]topology.istio.io/network',
    'ALINK_TYPE',
    'API',
    'Application',
    'Datacenter',
    'Environment',
    'qo',
    'WebSphere Cluster',
]
DATABASE_SERVICE_TAGS = [
    'Application',
    'Datacenter',
    'Environment',
]
PROCESS_GROUP_TAGS = [
    'Kubernetes Cluster',
    'Kubernetes Base Pod Name',
    'Kubernetes Container Name',
    'Kubernetes Full Pod Name',
    'Kubernetes Namespace',
    'Kubernetes Pod UID',
    '[Kubernetes]app',
    '[Kubernetes]app.kubernetes.io/component',
    '[Kubernetes]app.kubernetes.io/managed-by',
    '[Kubernetes]app.kubernetes.io/name',
    '[Kubernetes]app.kubernetes.io/version',
    '[Kubernetes]appCode',
    '[Kubernetes]aspnetcoreEnvironment',
    '[Kubernetes]buildbranchName',
    '[Kubernetes]buildbuildNumber',
    '[Kubernetes]buildgitCommit',
    '[Kubernetes]buildRepository',
    '[Kubernetes]component',
    '[Kubernetes]controller-revision-hash',
    '[Kubernetes]helm-revision',
    '[Kubernetes]helm.sh/chart',
    '[Kubernetes]imageName',
    '[Kubernetes]imageRegistry',
    '[Kubernetes]imageRepository',
    '[Kubernetes]imageTag',
    '[Kubernetes]internal.dynatrace.com/app',
    '[Kubernetes]internal.dynatrace.com/component',
    '[Kubernetes]k8s-app',
    '[Kubernetes]kubernetes.azure.com/managedby',
    '[Kubernetes]name',
    '[Kubernetes]pod-template-generation',
    '[Kubernetes]releasebranchName',
    '[Kubernetes]releasebuildNumber',
    '[Kubernetes]releasegitCommit',
    '[Kubernetes]releaseName',
    '[Kubernetes]releaseRepository',
    '[Kubernetes]rsName',
    '[Kubernetes]security.istio.io/tlsMode',
    '[Kubernetes]service.istio.io/canonical-name',
    '[Kubernetes]service.istio.io/canonical-revision',
    '[Kubernetes]tier',
    '[Kubernetes]topology.istio.io/network',
    'API',
    'Application',
    'cno-k8s-prod',
    'Datacenter',
    'Environment',
    'qo',
    'WebSphere Cluster',
]
HOST_TAGS = [
    'Kubernetes Cluster',
    'Kubernetes Base Pod Name',
    'Kubernetes Container Name',
    'Kubernetes Full Pod Name',
    'Kubernetes Namespace',
    'Kubernetes Pod UID',
    '[Azure]aks-managed-createOperationID',
    '[Azure]aks-managed-creationSource',
    '[Azure]aks-managed-kubeletIdentityClientID',
    '[Azure]aks-managed-operationID',
    '[Azure]aks-managed-orchestrator',
    '[Azure]aks-managed-poolName',
    '[Azure]aks-managed-resourceNameSuffix',
    '[Azure]appcode',
    '[Azure]appname',
    '[Azure]cost_center',
    '[Azure]domain',
    '[Azure]env',
    '[Azure]loc',
    '[Azure]orchestrator',
    '[Azure]owner',
    '[Azure]poolName',
    '[Azure]role',
    '[Azure]sku_osversion',
    '[Azure]tshirt_size',
    '[Azure]workspace',
    '[Azure]Zerto',
    '[Azure]zone',
    '[Environment]EDMDC-PROD',
    '[Environment]EDMDG-PROD',
    '[Environment]IBOFX',
    '[Environment]MTSWR-PROD',
    '[Environment]WRFRD-PROD',
    'API',
    'Application',
    'Chef',
    'cno-k8s-prod',
    'Datacenter',
    'Digital',
    'Environment',
    'Host group',
    'qo',
    'Server_Type',
]
KUBERNETES_TAGS = [
    'Kubernetes Cluster',
    'Kubernetes Base Pod Name',
    'Kubernetes Container Name',
    'Kubernetes Full Pod Name',
    'Kubernetes Namespace',
    'Kubernetes Pod UID',
    'Application',
    'cno-k8s-prod',
    'Datacenter',
    'Environment',
]

IIS_TAGS = []

WEB_APPLICATION_FILTERS = ['APPLICATION_INJECTION_TYPE']
SERVICE_FILTERS = ['SERVICE_TYPE']
DATABASE_SERVICE_FILTERS = ['DATABASE_VENDOR']
PROCESS_GROUP_FILTERS = []
HOST_FILTERS = ['HOST_MONITORING_MODE', 'HOST_VIRTUALIZATION_TYPE', 'OS_TYPE']
CUSTOM_DEVICE_FILTERS = ['CUSTOM_DIMENSION:Custom Device']

# For Demo/Customer2 True
# For Customer1 False
hasMobile = True

hasManagementZoneMarkdown = True

confirmation_required = True
remove_directory_at_startup = True

use_yaml_for_dynamic_tag_filters = True


def customize_dashboards():
    print(f'owner: {OWNER}')
    print(f'prefix: "{PREFIX}"')
    print(f'shared: {SHARED}')
    print(f'preset: {PRESET}')
    print(f'menu preset: {MENU_PRESET}')

    confirm('Customize dashboards from ' + DASHBOARD_TEMPLATE_PATH + ' to ' + DASHBOARD_CUSTOM_PATH)
    initialize()

    if use_yaml_for_dynamic_tag_filters:
        load_tag_filters_from_yaml()

    for filename in glob.glob(DASHBOARD_TEMPLATE_PATH + '/00000000-*'):
        base_name = os.path.basename(filename)
        # print(filename)
        if base_name not in skip_file_name_list:
            with open(filename, 'r', encoding='utf-8') as f:
                dashboard = f.read()
                new_dashboard = customize_dashboard(dashboard)
                pretty_new_dashboard = json.dumps(new_dashboard, indent=4, sort_keys=False)
                name = new_dashboard.get('dashboardMetadata').get('name')
                if hasMobile or (not hasMobile and 'Mobile' not in name):
                    output_filename = DASHBOARD_CUSTOM_PATH + '/' + base_name
                    with open(output_filename, 'w', encoding='utf-8') as outfile:
                        outfile.write(pretty_new_dashboard)


def customize_dashboard(dashboard):
    # print(dashboard)
    dashboard_json = json.loads(dashboard)
    new_dashboard_json = copy.deepcopy(dashboard_json)
    dashboard_id = dashboard_json.get('id')
    name = dashboard_json.get('dashboardMetadata').get('name')
    print(dashboard_id, name)

    filters = []
    if ': Overview' in name:
        # print(f'Overview in {name}')
        if not hasMobile:
            tiles = dashboard_json.get('tiles')
            app_markdown = tiles[0].get('markdown').replace('Web Apps', 'Web Applications').replace(' / [Mobile Apps](#dashboard;id=00000000-dddd-bbbb-ffff-000000000003)', '')
            new_dashboard_json['tiles'][0]['markdown'] = app_markdown
        if hasManagementZoneMarkdown:
            tiles = dashboard_json.get('tiles')
            for tile in tiles:
                if tile.get('name') == 'Management Zone Overview Links Markdown':
                    print('Modified the mz markdown tile!')
                    tile['markdown'] = generate_management_zone_markdown()
                    new_dashboard_json['tiles'] = tiles
    else:
        if ': Hosts' in name:
            # print(f'Hosts in {name}')
            for value in HOST_TAGS:
                filters.append('HOST_TAG_KEY:' + value)
            filters.extend(HOST_FILTERS)
        else:
            # if ': Processes' in name or ': Java' in name or ': .NET' in name or ': Tomcat' in name or ': WebLogic' in name or ': WebSphere' in name:
            if ': Processes' in name or ': Java' in name or ': .NET' in name or ': Tomcat' in name:
                # print(f'Processes or Process Technology in {name}')
                for value in PROCESS_GROUP_TAGS:
                    filters.append('PROCESS_GROUP_INSTANCE_TAG_KEY:' + value)
                filters.extend(PROCESS_GROUP_FILTERS)
                if not (': Processes' in name or ': .NET' in name):
                    try:
                        filters.remove('PROCESS_GROUP_INSTANCE_TAG_KEY:IIS App Pool')
                    except:
                        pass
            else:
                if ': Web Applications' in name:
                    # print(f'Web Applications in {name}')
                    for value in WEB_APPLICATION_TAGS:
                        filters.append('APPLICATION_TAG_KEY:' + value)
                    filters.extend(WEB_APPLICATION_FILTERS)
                else:
                    if ': Service' in name:
                        # print(f'Service in {name}')
                        for value in SERVICE_TAGS:
                            filters.append('SERVICE_TAG_KEY:' + value)
                        filters.extend(SERVICE_FILTERS)
                    else:
                        if ': Databases' in name:
                            # print(f'Databases in {name}')
                            for value in DATABASE_SERVICE_TAGS:
                                filters.append('SERVICE_TAG_KEY:' + value)
                            filters.extend(DATABASE_SERVICE_FILTERS)
                        else:
                            if ': Network' in name:
                                # print(f'Network in {name}')
                                if 'Host' in name:
                                    # print('Host in name')
                                    for value in HOST_TAGS:
                                        filters.append('HOST_TAG_KEY:' + value)
                                    filters.extend(HOST_FILTERS)
                                else:
                                    if 'Process' in name:
                                        # print(f'Process in *{name}')
                                        for value in PROCESS_GROUP_TAGS:
                                            filters.append('PROCESS_GROUP_INSTANCE_TAG_KEY:' + value)
                                        filters.extend(PROCESS_GROUP_FILTERS)
                            else:
                                # if 'DataPower' in name or 'F5' in name or 'IBM MQ' in name or 'SAP Hana' in name:
                                if 'DataPower' in name or 'F5' in name or 'SAP Hana' in name:
                                    # print(f'Extension in *{name}')
                                    # print('Adding custom device filter...')
                                    filters.extend(CUSTOM_DEVICE_FILTERS)

    if filters:
        new_dashboard_json['dashboardMetadata']['dynamicFilters'] = {}
        new_dashboard_json['dashboardMetadata']['dynamicFilters']['filters'] = filters
    if PREFIX == '':
        name = name.replace('TEMPLATE: ', '')
    else:
        name = name.replace('TEMPLATE:', PREFIX)
    new_dashboard_json['dashboardMetadata']['name'] = name
    new_dashboard_json['dashboardMetadata']['owner'] = OWNER
    new_dashboard_json['dashboardMetadata']['shared'] = SHARED

    if '00000000-dddd-bbbb-ffff-000000000001' in new_dashboard_json['id']:
        new_dashboard_json['dashboardMetadata']['preset'] = MENU_PRESET
    else:
        new_dashboard_json['dashboardMetadata']['preset'] = PRESET

    return new_dashboard_json


def initialize():
    if remove_directory_at_startup:
        confirm('The ' + DASHBOARD_CUSTOM_PATH + ' directory will now be removed to prepare for the conversion.')
        remove_directory(DASHBOARD_CUSTOM_PATH)

    if not os.path.isdir(DASHBOARD_CUSTOM_PATH):
        make_directory(DASHBOARD_CUSTOM_PATH)


def remove_directory(path):
    # print('remove_directory(' + path + ')')

    try:
        shutil.rmtree(path, ignore_errors=False)

    except OSError:
        print('Directory %s does not exist' % path)
    else:
        print('Removed the directory %s ' % path)


def make_directory(path):
    # print('make_directory(' + path + ')')
    try:
        os.makedirs(path)
    except OSError:
        print('Creation of the directory %s failed' % path)
        exit()
    else:
        print('Successfully created the directory %s ' % path)


def confirm(message):
    # print('confirm(' + message + ')')
    if confirmation_required:
        proceed = input('%s (Y/n) ' % message).upper() == 'Y'
        if not proceed:
            exit(get_linenumber())


def get_linenumber():
    # print('get_linenumber()')
    cf = currentframe()
    return cf.f_back.f_lineno


def load_tag_filters_from_yaml():
    global WEB_APPLICATION_TAGS
    global SERVICE_TAGS
    global PROCESS_GROUP_TAGS
    global HOST_TAGS
    global KUBERNETES_TAGS
    global DATABASE_SERVICE_TAGS
    global IIS_TAGS

    input_filename = f'dynamic_tag_filters_{env_name}.yaml'

    try:
        yaml_dict = read_yaml(input_filename)
    except FileNotFoundError as e:
        print(f'YAML configuration file {input_filename} was not found...aborting')
        exit(1)

    WEB_APPLICATION_TAGS = yaml_dict.get('APPLICATION', [])
    SERVICE_TAGS = yaml_dict.get('SERVICE', [])
    PROCESS_GROUP_TAGS = yaml_dict.get('PROCESS_GROUP', [])
    HOST_TAGS = yaml_dict.get('HOST', [])
    kubernetes_cluster_tags = yaml_dict.get('KUBERNETES_CLUSTER', [])
    kubernetes_node_tags = yaml_dict.get('KUBERNETES_NODE', [])
    kubernetes_service_tags = yaml_dict.get('KUBERNETES_SERVICE', [])
    # print(kubernetes_service_tags, kubernetes_cluster_tags, kubernetes_node_tags)
    KUBERNETES_TAGS = kubernetes_cluster_tags
    if kubernetes_node_tags:
        KUBERNETES_TAGS.extend(kubernetes_cluster_tags)
    if kubernetes_service_tags:
        KUBERNETES_TAGS.extend(kubernetes_service_tags)
    DATABASE_SERVICE_TAGS = yaml_dict.get('DATABASE_SERVICE', [])

    # Hardcode for now...include if needed...
    IIS_TAGS = ['IIS App Pool']


def read_yaml(input_file_name):
    with open(input_file_name, 'r') as file:
        document = file.read()
        yaml_data = yaml.load(document, Loader=yaml.FullLoader)
    return yaml_data


def generate_management_zone_markdown():
    endpoint = '/api/config/v1/managementZones'
    management_zone_json_list = dynatrace_api.get_json_list_with_pagination(f'{env}{endpoint}', token)

    markdown = 'Management Zone Overview Links\n\n'

    mz_markdown_dict = {}
    for management_zone_json in management_zone_json_list:
        inner_management_zone_json_list = management_zone_json.get('values')
        for inner_management_zone_json in inner_management_zone_json_list:
            mz_id = inner_management_zone_json.get('id')
            mz_name = inner_management_zone_json.get('name')
            dashboard_id = convert_mz_id_to_db_id(mz_id)
            mz_markdown_dict[mz_name] = {'mz_id': mz_id, 'dashboard_id': dashboard_id}

    for mz_name in sorted(mz_markdown_dict.keys()):
        dashboard_id = mz_markdown_dict[mz_name]['dashboard_id']
        mz_id = mz_markdown_dict[mz_name]['mz_id']
        markdown += f'[{mz_name}](#dashboard;id={dashboard_id};gf={mz_id})  \n'

    return markdown


def convert_mz_id_to_db_id(mz_id):
    # drop the negative sign, if present and start number with 1 instead.
    # start positive numbers with 2 so that positive and negative numbers are both of the same length (20) and remain unique.
    if mz_id.startswith('-'):
        mz_id = '1' + mz_id.replace('-', '')
    else:
        mz_id = '2' + mz_id

    mz_id_string = str(mz_id)
    dashboard_id = f'00000000-dddd-{mz_id_string[0:4]}-{mz_id_string[4:8]}-{mz_id_string[8:20]}'

    return dashboard_id


def main():
    customize_dashboards()


if __name__ == '__main__':
    main()
