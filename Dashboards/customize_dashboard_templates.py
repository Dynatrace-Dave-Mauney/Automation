import copy
import glob
import json
import os
import shutil
from inspect import currentframe

PREFIX = ''
# OWNER = 'nobody@example.com'
# OWNER = os.environ.get('DASHBOARD_OWNER_EMAIL', 'nobody@example.com')
OWNER = 'nobody@example.com'
SHARED = True
PRESET = True

DASHBOARD_TEMPLATE_PATH = 'Templates/Overview'
DASHBOARD_CUSTOM_PATH = 'Custom/Overview'

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

# Customer Specific Tags with no prefix
WEB_APPLICATION_TAGS = ['Application', 'Company', 'Environment', 'Web Application Name']
SERVICE_TAGS = ['Application', 'Company', 'Environment', 'Service Name', 'AWS Availability Zone', 'Apache Config Path', 'Asp Dot Net Core Application Path', 'Catalina Base', 'Catalina Home', 'Cloud Provider', 'Command Line Args', 'Data Center', 'Dot Net Command', 'Dot Net Command Path', 'Exe Name', 'Exe Path', 'Geolocation', 'Host CPU Cores', 'Host Group', 'Host Name', 'IBM Integration Node Name', 'IBM Integration Server Name', 'IIS App Pool', 'IP Address', 'Java Jar File', 'Java Jar Path', 'Kubernetes Base Pod Name', 'Kubernetes Cluster', 'Kubernetes Container Name', 'Kubernetes Full Pod Name', 'Kubernetes Namespace', 'Kubernetes Pod UID', 'Node JS Script Name', 'NodeJS App Base Director', 'NodeJS App Name', 'OS', 'Process Group Name', 'SpringBootAppName', 'SpringBootProfileName', 'SpringBootStartupClass', 'Technology', 'VMWare Data Center Name', 'VMWare VM Name', 'Web Application ID', 'Web Context Root', 'Web Server Name', 'Web Service Name', 'Web Service Namespace', 'WebLogic Cluster', 'WebLogic Domain', 'WebLogic Home', 'WebLogic Name', 'WebSphere Cell', 'WebSphere Cluster', 'WebSphere Node', 'WebSphere Server']
DATABASE_SERVICE_TAGS = ['DATABASE_VENDOR', 'SERVICE_TYPE', 'Application', 'Company', 'Environment', 'Service Name', 'Database Vendor']
PROCESS_GROUP_TAGS = ['Application', 'Company', 'Environment', 'Process Group Name', 'AWS Availability Zone', 'Apache Config Path', 'Asp Dot Net Core Application Path', 'Catalina Base', 'Catalina Home', 'Cloud Provider', 'Command Line Args', 'Data Center', 'Dot Net Command', 'Dot Net Command Path', 'Exe Name', 'Exe Path', 'Geolocation', 'Host CPU Cores', 'Host Group', 'Host Name', 'IBM Integration Node Name', 'IBM Integration Server Name', 'IIS App Pool', 'IP Address', 'Java Jar File', 'Java Jar Path', 'Kubernetes Base Pod Name', 'Kubernetes Cluster', 'Kubernetes Container Name', 'Kubernetes Full Pod Name', 'Kubernetes Namespace', 'Kubernetes Pod UID', 'Node JS Script Name', 'NodeJS App Base Director', 'NodeJS App Name', 'OS', 'Process Group Name', 'SpringBootAppName', 'SpringBootProfileName', 'SpringBootStartupClass', 'Technology', 'VMWare Data Center Name', 'VMWare VM Name', 'Web Application ID', 'Web Context Root', 'Web Server Name', 'Web Service Name', 'Web Service Namespace', 'WebLogic Cluster', 'WebLogic Domain', 'WebLogic Home', 'WebLogic Name', 'WebSphere Cell', 'WebSphere Cluster', 'WebSphere Node', 'WebSphere Server']
HOST_TAGS = ['HOST_MONITORING_MODE', 'HOST_VIRTUALIZATION_TYPE', 'OS_TYPE', 'Application', 'Company', 'Environment', 'AWS Availability Zone', 'Apache Config Path', 'Asp Dot Net Core Application Path', 'Catalina Base', 'Catalina Home', 'Cloud Provider', 'Command Line Args', 'Data Center', 'Dot Net Command', 'Dot Net Command Path', 'Exe Name', 'Exe Path', 'Geolocation', 'Host CPU Cores', 'Host Group', 'Host Name', 'IBM Integration Node Name', 'IBM Integration Server Name', 'IIS App Pool', 'IP Address', 'Java Jar File', 'Java Jar Path', 'Kubernetes Base Pod Name', 'Kubernetes Cluster', 'Kubernetes Container Name', 'Kubernetes Full Pod Name', 'Kubernetes Namespace', 'Kubernetes Pod UID', 'Node JS Script Name', 'NodeJS App Base Director', 'NodeJS App Name', 'OS', 'Process Group Name', 'SpringBootAppName', 'SpringBootProfileName', 'SpringBootStartupClass', 'Technology', 'VMWare Data Center Name', 'VMWare VM Name', 'Web Application ID', 'Web Context Root', 'Web Server Name', 'Web Service Name', 'Web Service Namespace', 'WebLogic Cluster', 'WebLogic Domain', 'WebLogic Home', 'WebLogic Name', 'WebSphere Cell', 'WebSphere Cluster', 'WebSphere Node', 'WebSphere Server']
KUBERNETES_TAGS = ['Kubernetes Base Pod Name', 'Kubernetes Cluster', 'Kubernetes Container Name', 'Kubernetes Namespace']
IIS_TAGS = ['IIS App Pool']

SERVICE_FILTERS = ['SERVICE_TYPE']
DATABASE_SERVICE_FILTERS = ['DATABASE_VENDOR', 'SERVICE_TYPE']
PROCESS_GROUP_FILTERS = []
HOST_FILTERS = ['HOST_MONITORING_MODE', 'HOST_VIRTUALIZATION_TYPE', 'OS_TYPE']

CUSTOM_DEVICE_FILTERS = ['CUSTOM_DIMENSION:Custom Device']

hasMobile = False

confirmation_required = True
remove_directory_at_startup = True


def customize_dashboards():
    print(f'owner: {OWNER}')
    print(f'prefix: "{PREFIX}"')
    print(f'shared: {SHARED}')
    print(f'preset: {PRESET}')

    confirm('Customize dashboards from ' + DASHBOARD_TEMPLATE_PATH + ' to ' + DASHBOARD_CUSTOM_PATH)
    initialize()

    for filename in glob.glob(DASHBOARD_TEMPLATE_PATH + '/00000000-*'):
        # print(filename)
        with open(filename, 'r', encoding='utf-8') as f:
            dashboard = f.read()
            new_dashboard = customize_dashboard(dashboard)
            pretty_new_dashboard = json.dumps(new_dashboard, indent=4, sort_keys=False)
            name = new_dashboard.get('dashboardMetadata').get('name')
            if hasMobile or (not hasMobile and 'Mobile' not in name):
                output_filename = DASHBOARD_CUSTOM_PATH + '/' + os.path.basename(filename)
                with open(output_filename, 'w', encoding='utf-8') as outfile:
                    outfile.write(pretty_new_dashboard)


def customize_dashboard(dashboard):
    dashboard_json = json.loads(dashboard)
    new_dashboard_json = copy.deepcopy(dashboard_json)
    name = dashboard_json.get('dashboardMetadata').get('name')
    # print(name)

    filters = []
    if ': Overview' in name:
        # print(f'Overview in {name}')
        if not hasMobile:
            tiles = dashboard_json.get('tiles')
            app_markdown = tiles[0].get('markdown').replace('Web Apps', 'Web Applications').replace(' / [Mobile Apps](#dashboard;id=00000000-dddd-bbbb-ffff-000000000003)', '')
            new_dashboard_json['tiles'][0]['markdown'] = app_markdown
    else:
        if ': Hosts' in name:
            # print(f'Hosts in {name}')
            for value in HOST_TAGS:
                filters.append('HOST_TAG_KEY:' + value)
            filters.extend(HOST_FILTERS)
        else:
            if ': Processes' in name or ': Java' in name or ': .NET' in name or ': Tomcat' in name or ': WebLogic' in name or ': WebSphere' in name:
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
                                if 'DataPower' in name or 'F5' in name or 'IBM MQ' in name or 'SAP Hana' in name:
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


def main():
    customize_dashboards()


if __name__ == '__main__':
    main()
