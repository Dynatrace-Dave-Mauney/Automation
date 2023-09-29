#
# Summarize how to deal with each technology listed by the hub API and/or the hub page at https://www.dynatrace.com/hub/.
# Output is written to the console in pipe-delimited format, to an Excel spreadsheet and to an HTML page.
#

import requests
from bs4 import BeautifulSoup

from Reuse import dynatrace_api
from Reuse import environment
from Reuse import report_writer


def process_hub_items(env, token):
    api_results = process_hub_items_from_api(env, token)
    web_results = process_hub_items_from_web()
    merged_results = merge_results_into_dictionary(api_results, web_results)
    process_merged_results(merged_results)


def process_hub_items_from_api(env, token):
    results = []

    endpoint = '/api/v2/hub/items'
    params = ''
    hub_items_json_list = dynatrace_api.get(env, token, endpoint, params)
    for hub_items_json in hub_items_json_list:
        inner_hub_items_json_list = hub_items_json.get('items')
        for inner_hub_items_json in inner_hub_items_json_list:
            hub_item_name = inner_hub_items_json.get('name')
            hub_item_description = inner_hub_items_json.get('description')
            hub_item_documentation_link = inner_hub_items_json.get('documentationLink')
            hub_item_marketing_link = inner_hub_items_json.get('marketingLink')
            comment = get_comment(hub_item_name)
            results.append((hub_item_name, hub_item_description, comment, hub_item_documentation_link, hub_item_marketing_link))

    return sorted(results)


def process_hub_items_from_web():
    page = requests.get('https://www.dynatrace.com/hub/')
    soup = BeautifulSoup(page.text, 'html.parser')

    results = []

    # Most technologies are found in an "a" tag and have links
    for link in soup.find_all('a'):
        title = link.get('title')
        href = link.get('href')
        description = link.find('p', class_='store-logowall__description-body')
        if description:
            description = description.text
        if href and href.startswith('/'):
            href = f'https://dynatrace.com{href}'
        if title:
            comment = get_comment(title)
            results.append((title, description, comment, href))

    # Some technologies are found in a "div" tag and lack links
    # These add little real value other than adding "Web" to the "Source" currently as the "href" is missing
    for link in soup.find_all('div'):
        title = link.get('title')
        if title:
            href = link.get('href')
            description = link.find('p', class_='store-logowall__description-body')
            if description:
                description = description.text
            if href and href.startswith('/'):
                href = f'https://dynatrace.com{href}'
            if description:
                comment = get_comment(title)
                results.append((title, description, comment, href))

    return sorted(results)


def merge_results_into_dictionary(api_results, web_results):
    merged_results_dictionary = {}

    for api_result in api_results:
        hub_item_name, hub_item_description, comment, doc_link, mkt_link = api_result
        merged_results_dictionary[hub_item_name] = {'api_desc': hub_item_description, 'comment': comment, 'doc_link': doc_link, 'mkt_link': mkt_link}

    for web_result in web_results:
        hub_item_name, hub_item_description, comment, link = web_result
        merged_results_dictionary_item = merged_results_dictionary.get(hub_item_name)
        if merged_results_dictionary.get(hub_item_name):
            merged_results_dictionary_item['web_desc'] = hub_item_description
            merged_results_dictionary_item['web_link'] = link
            merged_results_dictionary_item[hub_item_name] = merged_results_dictionary_item
        else:
            merged_results_dictionary[hub_item_name] = {'web_desc': hub_item_description, 'comment': comment, 'web_link': link}

    return merged_results_dictionary


def process_merged_results(merged_results):
    xlsx_file_name = '../../docs/HubSummary.xlsx'
    html_file_name = '../../docs/HubSummary.html'

    console_rows = []
    html_rows = []
    xlsx_rows = []

    merged_result_keys = merged_results.keys()
    for merged_result_key in merged_result_keys:
        merged_result = merged_results.get(merged_result_key)
        api_description = merged_result.get('api_desc')
        web_description = merged_result.get('web_desc')
        description = api_description
        if not description:
            description = web_description
        doc_link = merged_result.get('doc_link')
        mkt_link = merged_result.get('mkt_link')
        web_link = merged_result.get('web_link')
        best_link = web_link
        if not best_link:
            best_link = doc_link
            if not best_link:
                best_link = mkt_link
                if not best_link:
                    best_link = 'https://www.dynatrace.com/hub/'
        source = 'API and Web'
        if web_description:
            if not api_description:
                source = 'Web'
        else:
            if api_description:
                source = 'API'
        comment = merged_result.get('comment')

        console_rows.append((merged_result_key, description, comment, best_link, web_link, doc_link, mkt_link, source))

        html_merged_result_key_link = f'<a href="{best_link.lower()}">{merged_result_key}</a>'
        if best_link:
            html_best_link = f'<a href="{best_link.lower()}">{best_link}</a>'
        else:
            html_best_link = ''
        if web_link:
            html_web_link = f'<a href="{web_link.lower()}">{web_link}</a>'
        else:
            html_web_link = ''
        if doc_link:
            html_doc_link = f'<a href="{doc_link.lower()}">{doc_link}</a>'
        else:
            html_doc_link = ''
        if mkt_link:
            html_mkt_link = f'<a href="{mkt_link.lower()}">{mkt_link}</a>'
        else:
            html_mkt_link = ''
        html_rows.append((html_merged_result_key_link, description, comment, html_best_link, html_web_link, html_doc_link, html_mkt_link, source))

        xlsx_merged_result_key_link = {'link': {'url': best_link, 'text': merged_result_key}}
        xlsx_rows.append((xlsx_merged_result_key_link, description, comment, best_link, web_link, doc_link, mkt_link, source))

    # write_console(sorted(results, key=lambda result: result[0].lower()))
    # write_html(sorted(results, key=lambda result: result[0].lower()))
    # write_xlsx(sorted(results, key=lambda result: result[0].lower()))

    write_console(sorted(console_rows, key=lambda row: row[0].lower()))
    write_xlsx(xlsx_file_name, sorted(xlsx_rows, key=lambda row: row[0].get('text', '').lower()))
    write_html(html_file_name, sorted(html_rows, key=lambda row: extract_href_text(row[0]).lower()))


def extract_href_text(html):
    # Extract just the text from an HTML href (used for sorting when a link is in the column)
    soup = BeautifulSoup(html, 'html.parser')
    link = soup.find('a')
    text = link.get_text()
    return text


def check_hub_for_new_items(env, token):
    print('New to the Hub:')

    api_results = process_hub_items_from_api(env, token)
    web_results = process_hub_items_from_web()
    merged_results = merge_results_into_dictionary(api_results, web_results)

    merged_result_keys = merged_results.keys()
    for merged_result_key in merged_result_keys:
        merged_result = merged_results.get(merged_result_key)
        api_description = merged_result.get('api_desc')
        web_description = merged_result.get('web_desc')
        description = api_description
        if not description:
            description = web_description
        doc_link = merged_result.get('doc_link')
        mkt_link = merged_result.get('mkt_link')
        web_link = merged_result.get('web_link')
        best_link = web_link
        if not best_link:
            best_link = doc_link
            if not best_link:
                best_link = mkt_link
                if not best_link:
                    best_link = 'https://www.dynatrace.com/hub/'
        source = 'API and Web'
        if web_description:
            if not api_description:
                source = 'Web'
        else:
            if api_description:
                source = 'API'
        comment = merged_result.get('comment')
        if comment == '':
            print(f'{merged_result_key} | {description} | {best_link} | {source}')


def get_comment(title):
    aws_built_in_list = [
        'Amazon DynamoDB',
        'Amazon EBS',
        'Amazon EC2',
        'Amazon EC2 Auto Scaling',
        'Amazon RDS',
        'Amazon S3',
        'AWS Application and Network Load Balancer',
        'AWS Elastic Load Balancing(ELB)',
        'AWS Lambda',
    ]

    azure_built_in_list = [
        'Azure API Management Services',
        'Azure Application Gateways',
        'Azure Application Service',
        'Azure Cosmos Database',
        'Azure Events Hub',
        'Azure Iot Hub',
        'Azure Load Balancers',
        'Azure Redis Cache',
        'Azure Service Bus',
        'Azure Sql Servers',
        'Azure Virtual Machines',
    ]

    google_cloud_supported_services_list = [
        'Google AI Platform',
        'Google Apigee',
        'Google App Engine',
        'Google App Engine. Monitor with GCP integration',
        'Google Assistant Smart Home',
        'Google Big Query',
        'Google Cloud APIs',
        'Google Cloud Bigtable',
        'Google Cloud Composer',
        'Google Cloud DNS',
        'Google Cloud Data Loss Prevention',
        'Google Cloud Filestore',
        'Google Cloud Firestore',
        'Google Cloud Functions',
        'Google Cloud IoT Core',
        'Google Cloud Load Balancing',
        'Google Cloud Operations suite',
        'Google Cloud Platform',
        'Google Cloud Router',
        'Google Cloud Run',
        'Google Cloud Run. Monitor with GCP integration',
        'Google Cloud SQL',
        'Google Cloud Spanner',
        'Google Cloud Storage Transfer',
        'Google Cloud Storage',
        'Google Cloud Tasks',
        'Google Cloud Tensor Processing Unit (TPU)',
        'Google CloudTrace',
        "Google Cloud's operations suite",
        'Google Compute Engine',
        'Google Compute Engine. Monitor with GCP integration',
        'Google Dataflow',
        'Google Dataproc',
        'Google Firebase',
        'Google Firestore in Datastore mode',
        'Google Hybrid Connectivity',
        'Google Kubernetes Engine (GKE). Monitor with GCP integration',
        'Google Kubernetes Engine',
        'Google Managed Microsoft AD',
        'Google Memorystore',
        'Google Network Security',
        'Google Network Topology',
        'Google Pub/Sub Lite',
        'Google Pub/Sub',
        'Google VPC access',
        'Google Virtual Private Cloud',
        'Google Virtual Private Cloud',
        'Google reCAPTCHA Enterprise',
        'NetApp on Google Cloud',
    ]

    install_extension_list = [
        'Advanced SSL Certificate Check for Dynatrace',
        'Apache Cassandra (Remote)',
        'Apache Storm',
        'Apigee Edge',
        'Citrix NetScaler ADC',
        'Citrix Virtual Apps and Desktops',
        'Confluent Cloud (Kafka)',
        'Consul Service Mesh (StatsD)',
        'Control-M Jobs',
        'Custom database queries',
        'Databricks',
        'Disk Analytics',
        'Dynatrace Self-Monitoring (Managed)',
        'Extensions Health',
        'F5 BIG-IP LTM',
        'Filesystem monitoring',
        'Fortinet Fortigate',
        'IBM DataPower',
        'IBM DB2 LUW',
        'IBM Event Streams',
        'IBM Informix',
        'IBM i',
        'IBM MQ - ActiveGate',
        'InterSystems IRIS (Remote)',
        'ISAM',
        'Juniper Networks (SNMP)',
        'LDAP Synthetic',
        'Microsoft Exchange Server',
        'Microsoft Hyper-V (WMI)',
        'Mulesoft Cloudhub (Extension v2)',
        'MySQL (remote monitoring)',
        'MySQL (remote monitoring v2)',
        'NetApp OnTap (Remote)',
        'Netbackup Jobs',
        'OpenShift Control Plane',
        'Palo Alto firewalls',
        'Prometheus Alertmanager',
        'SAP HANA Database',
        'Elasticsearch',
        'etcd for OpenShift',
        'Generic Cisco Device',
        'Generic Linux Commands',
        'Generic network device',
        'IBM MQ',
        'Kubernetes Monitoring Statistics',
        'Kubernetes persistent volume claims',
        'NVIDIA GPUs',
        'Remote Desktop Protocol',
        'Remote Unix Monitoring',
        'Remote Windows Host Monitoring',
        'Salesforce Streaming API',
        'SAP GUI and ABAP platform',
        'Siebel',
        'SNMP Traps',
        'Snowflake',
        'Solarwinds',
        'SSL Checker',
        'Synthetic monitor DNS',
        'Synthetic monitor Ping',
        'Synthetic monitor Ports',
        'Synthetic Monitor SSH',
        'Synthetic SFTP monitor',
        'VMware Horizon',
        'VMware Unified Access Gateway',
        'VMware VCenter Alarms',
        'VMware vSAN',
        'Windows Scheduled Tasks',
        'Windows Server File System Quotas',

    ]

    install_rum_list = [
        'AMP',
        'Angular',
        'AngularJS',
        'jQuery',
        'React.js',
        'Sencha Touch',
        'Apache HTTP Server',
        'IBM HTTP Server',
        'Microsoft IIS',
        'Oracle HTTP Server',
        'Netty',
        'Android Browser',
        'Apple Safari',
        'Google Chrome',
        'iOS Safari',
        'Microsoft Edge',
        'Microsoft Internet Explorer',
        'Mozilla Firefox',
        'Opera',
        'Safari',
    ]

    install_mobile_list = [
        'Adobe PhoneGap',
        'Android',
        'Android Webkit',
        'Apache Cordova',
        'Dynatrace mobile app for Android',
        'Dynatrace mobile app for iOS',
        'Flutter',
        'Ionic',
        'iOS',
        'React Native',
        'tvOS',
        'Xamarin',
        'Xcode',
    ]

    configure_extension_list = [
        'Active Directory services',
        'Connection Pools: JBoss',
        'Connection Pools: Tomcat',
        'Connection Pools: WebLogic',
        'Connection Pools: WebSphere Liberty',
        'CoreDNS',
        'HAProxy',
        'Memcached',
        'PagerDuty',
        'RabbitMQ',
        'Slack',
    ]

    configure_integration_list = [
        'AWS',
        'ServiceNow',
        'VMware',
        'xMatters',
    ]

    install_oneagent_list = [
        '.NET Framework',
        '.NET / .NET Core',
        'ADO.NET',
        'Akka',
        'Amazon Linux 2',
        'Apache Axis2',
        'Apache Camel',
        'Apache CXF',
        'Apache OpenEJB',
        'Apache Kafka',
        'Apache Solr',
        'Apache Tomcat',
        'Apache TomEE',
        'ActiveMQ Artemis',
        'ActiveMQ',
        'ASP.NET / ASP.NET Core',
        'ASP.NET Owin/Katana',
        'Azul Platform Core (Zulu)',
        'Azul Platform Prime (Zing)',
        'BellSoft Liberica',
        'CakePHP',
        'CentOS',
        'Debian',
        'Drupal',
        'Eclipse Jetty',
        'Eclipse OpenJ9',
        'Eclipse Temurin (Adoptium)',
        'Erlang',
        'Express',
        'Fedora',
        'Fujitsu Interstage IHS',
        'Fujitsu Interstage',
        'Fujitsu JVM',
        'GlassFish',
        'Go',
        'GraalVM',
        'GraphQL',
        'Hitachi JVM',
        'Huawei JVM',
        'IBM AIX',
        'IBM App Connect Enterprise',
        'IBM Integration Bus',
        'IBM JVM',
        'IBM Semeru',
        'IBM WebSphere Application Server',
        'IBM WebSphere Liberty',
        'IBM WebSphere Message Broker',
        'Java',
        'Java JDBC',
        'Java JMS',
        'JBoss Enterprise Application Platform',
        'Joomla',
        'Jython',
        'Kestrel for ASP.NET Core',
        'Kong Gateway',
        'KVM',
        'Laravel',
        'Linux',
        'Linux on IBM Z mainframe',
        'Magento',
        'Microsoft Hyper-V',
        'Microsoft Message Queuing (MSMQ)',
        'NGINX Plus',
        'NGINX',
        'Node.js',
        'NTP sync check',
        'Nutanix AHV',
        'OneAgent',
        'OpenJDK',
        'openSUSE',
        'Oracle Cloud',
        'Oracle Hotspot VM',
        'Oracle JRockit',
        'Oracle Solaris',
        'Oracle WebLogic',
        'Payara',
        'Play Framework',
        'QEMU',
        'Reactor Core',
        'Red Hat Enterprise Linux',
        'Red Hat Enterprise Linux CoreOS',
        'Red Hat Fuse',
        'Red Hat OpenStack',
        'Red Hat Quarkus',
        'Riak',
        'Ruby',
        'SAP Business Technology Platform',
        'SAP Commerce Cloud',
        'SAP JVM',
        'Scala',
        'SUSE Linux Enterprise Server',
        'Spring',
        'Symfony',
        'Ubuntu',
        'Varnish Cache',
        'Varnish',
        'VMware Cloud on AWS',
        'VMware ESXi Host',
        'VMware vCenter Server',
        'Wildfly',
        'Windows',
        'Windows Communication Foundation (WCF)',
        'WordPress',
        'WSO2 API Manager',
        'Xen',
        'Yii',
    ]

    install_oneagent_infrastructure_only_list = [
        'Redis'
    ]

    install_oneagent_kubernetes_list = [
        'containerd',
        'cri-o',
        'Docker',
        'IBM Cloud Kubernetes Service',
        'Istio',
        'Kubernetes',
        'LinkerdD',
        'Red Hat OpenShift',
        'Google Container-optimized OS',
    ]

    install_oneagent_on_database_list = [
        'Apache Cassandra',
        'Apache CouchDB',
        'Couchbase',
        'IBM DB2',
        'MariaDB',
        'Microsoft SQL Server',
        'MongoDB',
        'Mongo DB Atlas',
        'MySQL',
        'Oracle Database',
        'PostgreSQL',
    ]

    install_oneagent_mainframe_list = [
        'IBM CICS Transaction Gateway for z/OS',
        'IBM CICS Transaction Server',
        'IBM IMS SOAP Gateway',
        'IBM IMS',
        'IBM WebSphere Application Server for z/OS',
        'IBM WebSphere Liberty for z/OS',
        'IBM z/OS Connect Enterprise Edition',
        'IBM z/OS',
    ]

    install_esa_solution_list = [
        'Dynatrace API Gateway by ESA',
        'Dynatrace ETL Service by ESA',
    ]

    supported_by_partners_list = [
        'aDSS avodaq Data Snapshot Service',
        'Akamas',
        'Akamas for Cloud Automation',
        'aMC Synthetic App',
        'BizTalk Plugin 2.0',
        'Composer',
        'Dynatrace Integration for Jira',
        'Flagsmith JavaScript Integration',
        'Gigamon HAWK Deep Observability Pipeline',
        'Google Analytics Real-Time',
        'Gremlin for Cloud Automation',
        'Gremlin for Dynatrace',
        'How fast is your app?',
        'LaunchDarkly for Cloud Automation',
        'LaunchDarkly Integration for Dynatrace',
        'Lightrun Developer Observability Platform',
        'Nagios Integration',
        'NeoLoad',
        'Nobl9 SLO Platform',
        'Omniscopy',
        'OutSystems Cloud Metrics',
        'Ping Every Second',
        'Redis Enterprise',
        'Redis Open Source',
        'Rookout Live Debugger',
        'Ruby on Rails Agent',
        'servicetrace',
        'SIGNL4 – Critical Mobile Alerting',
        'Timeseries Streamer',
        'Tricentis NeoLoad for Cloud Automation',
        'T-Systems / Jenkins',
        'versio.io',
        'WeChat Mini-Program Monitoring',
        'WIPRO Holmes',
        'Zabbix hosts',
        'Zabbix Integration',
        'Zenduty',
        'ZigiOps - Integration Platform',
    ]

    configure_problem_notification_integration_list = [
        'Ansible Tower',
        'Atlassian JIRA',
        'Microsoft Teams',
        'Opsgenie',
        'Trello',
        'VictorOps',
        'WebHooks',
    ]

    see_link_for_details_list = [
        'Ansible',
        'Apache Spark',
        'Custom Data ingest via API',
        'Fluentd',
        'Fluent Bit',
        'Garden-RunC',
        'Hadoop HDFS',
        'Hadoop YARN',
        'HashiCorp Terraform',
        'Hazelcast',
        'Heroku',
        'IBM Bluemix',
        'Cloud Automation Control Plane',
        'Grail',
        'Log Management and Analytics powered by Grail',
        'Log Monitoring for AWS',
        'Logstash',
        'Micrometer',
        'Neo4j',
        'OpenTelemetry Metrics',
        'OpenTelemetry Tracing',
        'OpenTracing',
        'Perl',
        'PHP',
        'StatsD',
        'Syslog (via Fluentd)',
        'Telegraf',
        'TIBCO EMS',
        'Vert.x',
    ]

    prometheus_extension_list = [
        'HAProxy (Prometheus)',
        'Istio and Envoy Service Mesh (Prometheus)',
        'Linkerd Service Mesh (Prometheus)',
        'MongoDB (Prometheus)',
        'Prometheus in Kubernetes',
        'Prometheus',
        'RabbitMQ (Prometheus)',
        'Redis Enterprise - Prometheus',
    ]

    configure_dev_ops_list = [
        'Apache JMeter',
        'Atlassian Bamboo',
        'Bitbucket',
        'Blazemeter',
        'Chef',
        'Concourse',
        'Gatling',
        'Keptn',
        'Maven',
        'Microsoft Visual Studio',
        'PHPUnit',
        'Selenium WebDriver',
        'TeamCity',
    ]

    cloud_foundry_list = [
        'BOSH bpm',
        'Cloud Foundry',
        'IBM Cloud Foundry',
        'Pivotal Platform',
        'VMware Tanzu',
    ]

    special_instructions = {
        'ActiveGate': 'Install ActiveGate(s) for specific use cases: executing synthetics on the local network, running ActiveGate extensions or routing agent traffic more effectively.',
        'Adobe Analytics': 'Configure Session and User Action properties in RUM settings for the web application.',
        'Amazon EC2': 'Perform AWS Integration and install a OneAgent on the EC2 instance, typically with "User Data".',
        'Amazon EC2 Auto Scaling': 'Perform AWS Integration and add this service to monitoring. Install a OneAgent on the EC2 instance, typically with "User Data".',
        'Amazon EC2 Spot Fleet': 'Perform AWS Integration and add this service to monitoring. Install a OneAgent on the EC2 instance, typically with "User Data".',
        'Business events': 'If GRAIL is active, see link for details on configuring business events.',
        'C': 'Use the Dynatrace SDK.',
        'DC/OS': 'Install the Dynatrace package via the DC/OS user interface.',
        'Davis Assistant': 'Deprecated: do not use.',
        'Dynatrace Solution Server by ESA': 'Install to leverage the Dynatrace API Gateway by ESA and/or the Dynatrace ETL Service by ESA.',
        'Google Analytics': 'Configure Session and User Action properties in RUM settings for the web application.',
        'gRPC': 'Install OneAgent and turn on gRPC OneAgent feature for language.',
        'LDAP': 'The link explains how to use manage users and groups via LDAP. To monitor LDAP, install a OneAgent for Host/Process monitoring and/or install the LDAP Synthetic Extension.',
        'LoadRunner': 'Configure request attributes, etc.  See blog posts, RobotAdmin, etc.',
        'Microsoft Active Directory replication': 'Install extension both on a OneAgent and on the Dynatrace Cluster.  See hub link for more details.',
        'Python': 'Install OneAgent for process monitoring, and optionally use OpenTelemetry, SDK or Python Auto-Instrumentation from Github for tracing.',
        'Runtime Application Protection': 'Activate the Application Security module.  Just contact us via in-product chat or directly via your account team.',
        'Runtime vulnerability detection': 'Activate the Application Security module.  Just follow instructions in the hub link.',
        'Runtime Vulnerability Analytics': 'Activate the Application Security module.  Just follow instructions in the hub link.',
        'Session Replay': 'Configure Session Replay in RUM settings for the web application.',
        'Snyk': 'Snyk is integrated with Dynatrace runtime vulnerability detection. Activate the Application Security module.  Just follow instructions in the hub link.',
    }

    # Special instructions override any others below
    comment = special_instructions.get(title)
    if comment:
        return comment

    if title in install_oneagent_list:
        comment = 'Install the OneAgent.'
        return comment

    if title in install_oneagent_infrastructure_only_list:
        comment = 'Install the OneAgent in infrastructure-only mode.'
        return comment

    if title in install_oneagent_kubernetes_list:
        comment = 'Install OneAgent Operator on Kubernetes.'
        return comment

    if title in install_oneagent_mainframe_list:
        comment = 'Install OneAgent on mainframe per instructions in the hub link.'
        return comment

    if title in install_rum_list:
        comment = 'Install OneAgent on web/application servers and configure RUM.'
        return comment

    if title in install_mobile_list:
        comment = 'Install OneAgent on web/application servers and configure mobile RUM.'
        return comment

    if title in install_oneagent_on_database_list:
        comment = 'Install OneAgent in Infrastructure only mode and configure built-in extension, if applicable.'
        return comment

    if title in install_extension_list:
        comment = 'Install extension.'
        return comment

    if title in configure_extension_list:
        comment = 'Configure the extension under Settings > Monitoring > Monitored technologies.'
        return comment

    if title in configure_integration_list:
        comment = 'Configure integration.'
        return comment

    if title.startswith('AWS') or title.startswith('Amazon'):
        if title in aws_built_in_list:
            comment = 'Perform AWS Integration.'
        else:
            comment = 'Perform AWS Integration and add this service to monitoring.'
        return comment

    if 'Azure' in title:
        if title in azure_built_in_list:
            comment = 'Perform Azure Integration.'
        else:
            comment = 'Perform Azure Integration and add this service to monitoring.'
        return comment

    if title in google_cloud_supported_services_list:
        comment = 'Deploy Google Cloud Platform integration and select services to be monitored.'
        return comment

    if title in install_esa_solution_list:
        comment = 'Deploy with the ESA Solution Server.'
        return comment

    if title in supported_by_partners_list:
        comment = 'Supported by a partner.  See Hub link for more details.'
        return comment

    if title in configure_problem_notification_integration_list:
        comment = 'Configure problem notification integration under Settings > Integration > Problem notifications.'
        return comment

    if title in see_link_for_details_list:
        comment = 'See Hub link for more details.'
        return comment

    if title in configure_dev_ops_list:
        comment = 'Requires DevOps integration. See Hub link for more details.'
        return comment

    if title in prometheus_extension_list:
        comment = 'See Hub link for more details about configuring prometheus metric ingestion.'
        return comment

    if title in cloud_foundry_list:
        comment = 'Set up Dynatrace on Cloud Foundry. See Hub link for more details.'
        return comment

    # Default comment can be empty or custom as desired
    # comment = 'No instructions needed.  Monitoring this technology is not applicable.'
    comment = ''

    return comment


def write_console(rows):
    title = 'Hub Summary'
    headers = ('Technology', 'Description', 'Monitoring Instructions', 'Best Link', 'Hub Link', 'Documentation Link', 'Marketing Link', 'Source')
    delimiter = ' | '
    report_writer.write_console(title, headers, rows, delimiter)


def write_xlsx(xlsx_file_name, rows):
    worksheet_name = 'Hub Summary'
    headers = ('Technology', 'Description', 'Monitoring Instructions', 'Best Link', 'Hub Link', 'Documentation Link', 'Marketing Link', 'Source')
    header_format = None
    auto_filter = (0, len(headers))
    report_writer.write_xlsx(xlsx_file_name, worksheet_name, headers, rows, header_format, auto_filter)


def write_html(html_file_name, rows):
    page_heading = 'Hub Summary'
    table_headers = ('Technology', 'Description', 'Monitoring Instructions', 'Best Link', 'Hub Link', 'Documentation Link', 'Marketing Link', 'Source')
    report_writer.write_html(html_file_name, page_heading, table_headers, rows)


def main():
    friendly_function_name = 'Dynatrace Automation Tools'
    env_name_supplied = environment.get_env_name(friendly_function_name)
    # For easy control from IDE
    # env_name_supplied = 'Prod'
    # env_name_supplied = 'NonProd'
    # env_name_supplied = 'Prep'
    # env_name_supplied = 'Dev'
    # env_name_supplied = 'Personal'
    # env_name_supplied = 'Demo'
    env_name, env, token = environment.get_environment_for_function(env_name_supplied, friendly_function_name)

    print('Hub Summary')

    process_hub_items(env, token)
    check_hub_for_new_items(env, token)


if __name__ == '__main__':
    main()

