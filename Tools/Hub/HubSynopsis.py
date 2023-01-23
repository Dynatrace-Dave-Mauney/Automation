#
# Scrape dynatrace.com/Hub and summarize how to deal with each technology.
# Output is written to the console in pipe-delimited format, to an Excel spreadsheet and to an HTML page.
#

import requests
import xlsxwriter
from bs4 import BeautifulSoup

exclude_list = [
    'OneAgent',
    'Active Directory services',
    'ActiveGate',
    'ActiveMQ',
    'ActiveMQ Artemis',
    'Adobe Analytics',
    'Adobe PhoneGap',
    'aDSS avodaq Data Snapshot Service',
    'Advanced SSL Certificate Check for Dynatrace',
    'Akamas',
    'Akamas for Cloud Automation',
    'Akka',
    'aMC Synthetic App',
    'AMP',
    'Android',
    'Android Webkit',
    'Ansible',
    'Ansible Tower',
    'Apache Axis2',
    'Apache Camel',
    'Apache Cordova',
    'Apache CouchDB',
    'Apache CXF',
    'Apache JMeter',
    'Apache OpenEJB',
    'Apache Spark',
    'Apache Storm',
    'Apache TomEE',
    'Apigee Edge',
    'Apple Safari',
    'Atlassian Bamboo',
    'Atlassian JIRA',
    'Azul Platform Core (Zulu)',
    'Azul Platform Prime (Zing)',
    'BellSoft Liberica',
    'Bitbucket',
    'BizTalk Plugin 2.0',
    'Blazemeter',
    'BOSH bpm',
    'Business events',
    'C',
    'CakePHP',
    'CentOS',
    'Chef',
    'Citrix NetScaler ADC',
    'Citrix Virtual Apps and Desktops',
    'Cloud Automation Control Plane',
    'Cloud Foundry',
    'Composer',
    'Concourse',
    'Confluent Cloud (Kafka)',
    'Connection Pools: WebSphere Liberty',
    'Consul Service Mesh (StatsD)',
    'containerd',
    'Control-M Jobs',
    'Couchbase',
    'cri-o',
    'Custom database queries',
    'Custom Data ingest via API',
    'Databricks',
    'Davis Assistant',
    'DC/OS',
    'Debian',
    'Disk Analytics',
    'Drupal',
    'Dynatrace API Gateway by ESA',
    'Dynatrace ETL Service by ESA',
    'Dynatrace Integration for Jira',
    'Dynatrace mobile app for Android',
    'Dynatrace mobile app for iOS',
    'Dynatrace Self-Monitoring (Managed)',
    'Dynatrace Solution Server by ESA',
    'Eclipse Jetty',
    'Eclipse OpenJ9',
    'Eclipse Temurin (Adoptium)',
    'Erlang',
    'Express',
    'Extensions Health',
    'Fedora',
    'Filesystem monitoring',
    'Flagsmith JavaScript Integration',
    'Fluentd',
    'Flutter',
    'Fortinet Fortigate',
    'Fujitsu Interstage',
    'Fujitsu Interstage IHS',
    'Fujitsu JVM',
    'Garden-RunC',
    'Gatling',
    'Generic Cisco Device',
    'Generic Linux Commands',
    'Generic network device',
    'Gigamon HAWK Deep Observability Pipeline',
    'GlassFish',
    'GraalVM',
    'Grail',
    'GraphQL',
    'Gremlin for Cloud Automation',
    'Gremlin for Dynatrace',
    'Hadoop HDFS',
    'Hadoop YARN',
    'HAProxy (Prometheus)',
    'HashiCorp Terraform',
    'Hazelcast',
    'Heroku',
    'Hitachi JVM',
    'How fast is your app?',
    'Huawei JVM',
    'IBM App Connect Enterprise',
    'IBM Bluemix',
    'IBM CICS Transaction Gateway for z/OS',
    'IBM CICS Transaction Server',
    'IBM Cloud Foundry',
    'IBM Cloud Kubernetes Service',
    'IBM DB2 LUW',
    'IBM Event Streams',
    'IBM HTTP Server',
    'IBM i',
    'IBM IMS',
    'IBM IMS SOAP Gateway',
    'IBM Informix',
    'IBM Semeru',
    'IBM WebSphere Application Server for z/OS',
    'IBM WebSphere Liberty for z/OS',
    'IBM WebSphere Message Broker',
    'IBM z/OS',
    'IBM z/OS Connect Enterprise Edition',
    'InterSystems IRIS (Remote)',
    'Ionic',
    'iOS',
    'iOS Safari',
    'ISAM',
    'Istio',
    'Istio and Envoy Service Mesh (Prometheus)',
    'Joomla',
    'Juniper Networks (SNMP)',
    'Jython',
    'Keptn',
    'Kestrel for ASP.NET Core',
    'Kong Gateway',
    'KVM',
    'Laravel',
    'LaunchDarkly for Cloud Automation',
    'LaunchDarkly Integration for Dynatrace',
    'LDAP',
    'LDAP Synthetic',
    'Lightrun Developer Observability Platform',
    'LinkerdD',
    'Linkerd Service Mesh (Prometheus)',
    'Linux on IBM Z mainframe',
    'Log Management and Analytics powered by Grail',
    'Logstash',
    'Magento',
    'MariaDB',
    'Maven',
    'Memcached',
    'Micrometer',
    'Microsoft Active Directory replication',
    'Microsoft Azure',
    'Microsoft Edge',
    'Microsoft Exchange Server',
    'Microsoft Hyper-V',
    'Microsoft Hyper-V (WMI)',
    'Microsoft Message Queuing (MSMQ)',
    'Microsoft Teams',
    'Microsoft Visual Studio',
    'MongoDB (Prometheus)',
    'Mulesoft Cloudhub (Extension v2)',
    'Nagios Integration',
    'Neo4j',
    'NeoLoad',
    'NetApp on Google Cloud',
    'NetApp OnTap (Remote)',
    'Netbackup Jobs',
    'NGINX',
    'NGINX Plus',
    'Nobl9 SLO Platform',
    'Nutanix AHV',
    'NVIDIA GPUs',
    'Omniscopy',
    'OpenJDK',
    'openSUSE',
    'OpenTelemetry Metrics',
    'OpenTelemetry Tracing',
    'OpenTracing',
    'Opera',
    'Opsgenie',
    'Oracle Cloud',
    'Oracle Hotspot VM',
    'Oracle HTTP Server',
    'Oracle JRockit',
    'Oracle Solaris',
    'OutSystems Cloud Metrics',
    'PagerDuty',
    'Palo Alto firewalls',
    'Payara',
    'Perl',
    'PHP',
    'PHPUnit',
    'Ping Every Second',
    'Pivotal Platform',
    'Play Framework',
    'Prometheus',
    'Prometheus Alertmanager',
    'Prometheus in Kubernetes',
    'QEMU',
    'RabbitMQ (Prometheus)',
    'React.js',
    'React Native',
    'Reactor Core',
    'Red Hat Fuse',
    'Red Hat OpenStack',
    'Red Hat Quarkus',
    'Redis',
    'Redis Enterprise',
    'Redis Enterprise - Prometheus',
    'Redis Open Source',
    'Remote Desktop Protocol',
    'Remote Unix Monitoring',
    'Remote Windows Host Monitoring',
    'Riak',
    'Rookout Live Debugger',
    'Ruby',
    'Ruby on Rails Agent',
    'Runtime Application Protection',
    'Runtime vulnerability detection',
    'Salesforce Streaming API',
    'SAP Business Technology Platform',
    'SAP Commerce Cloud',
    'SAP GUI and ABAP platform',
    'SAP JVM',
    'Scala',
    'Selenium WebDriver',
    'Sencha Touch',
    'servicetrace',
    'Session Replay',
    'Siebel',
    'SIGNL4 – Critical Mobile Alerting',
    'Slack',
    'SNMP Traps',
    'Snyk',
    'Solarwinds',
    'Spring',
    'SSL Checker',
    'StatsD',
    'SUSE Linux Enterprise Server',
    'Symfony',
    'TeamCity',
    'Telegraf',
    'TIBCO EMS',
    'Timeseries Streamer',
    'Trello',
    'Tricentis NeoLoad for Cloud Automation',
    'T-Systems / Jenkins',
    'tvOS',
    'Varnish',
    'Varnish Cache',
    'versio.io',
    'Vert.x',
    'VictorOps',
    'VMware Cloud on AWS',
    'VMware Horizon',
    'VMware Tanzu',
    'VMware Unified Access Gateway',
    'WebHooks',
    'WeChat Mini-Program Monitoring',
    'Wildfly',
    'WIPRO Holmes',
    'WordPress',
    'Xamarin',
    'Xcode',
    'Xen',
    'Yii',
    'Zabbix hosts',
    'Zabbix Integration',
    'Zenduty',
    'ZigiOps - Integration Platform',
]

how_to_monitor = {'xMatters': {'comment': 'Install the xMatters workflow', 'link': 'https://help.xmatters.com/integrations/monitoring/dynatrace.htm?cshid=Dynatrace'}}

include_list = [
    'Active Directory services',
    'ActiveGate',
    'ActiveMQ',
    'ActiveMQ Artemis',
    'Adobe Analytics',
    'Adobe PhoneGap',
    'ADO.NET',
    'aDSS avodaq Data Snapshot Service',
    'Advanced SSL Certificate Check for Dynatrace',
    'Akamas',
    'Akamas for Cloud Automation',
    'Akka',
    'Amazon API Gateway',
    'Amazon AppStream 2.0',
    'Amazon Athena',
    'Amazon Aurora',
    'Amazon CloudFront',
    'Amazon CloudSearch',
    'Amazon Cloudwatch',
    'Amazon CloudWatch Logs',
    'Amazon Cognito',
    'Amazon Corretto',
    'Amazon DocumentDB',
    'Amazon DynamoDB',
    'Amazon EC2',
    'Amazon EC2 Auto Scaling',
    'Amazon EC2 Spot Fleet',
    'Amazon ElastiCache',
    'Amazon Elastic Block Store (EBS)',
    'Amazon Elastic Container Service (ECS)',
    'Amazon Elastic File Service (EFS)',
    'Amazon Elastic Inference',
    'Amazon Elastic Kubernetes Service (EKS)',
    'Amazon Elasticsearch Service',
    'Amazon EMR',
    'Amazon FSx for Lustre',
    'Amazon FSx for Windows File Server',
    'Amazon GameLift',
    'Amazon Inspector',
    'Amazon Keyspaces for Apache Cassandra',
    'Amazon Kinesis Data Analytics',
    'Amazon Kinesis Data Firehose',
    'Amazon Kinesis Data Streams',
    'Amazon Kinesis Video Streams',
    'Amazon Lex',
    'Amazon Linux 2',
    'Amazon Managed Service for Prometheus',
    'Amazon MSK',
    'Amazon Neptune',
    'Amazon Redshift',
    'Amazon Rekognition',
    'Amazon Relational Database Service (RDS)',
    'Amazon Route 53',
    'Amazon S3',
    'Amazon SageMaker',
    'Amazon Simple Email Service (SES)',
    'Amazon Simple Notification Service (SNS)',
    'Amazon Simple Queue Service (SQS)',
    'Amazon Simple Workflow Service (SWF)',
    'Amazon Textract',
    'Amazon Transfer Family',
    'Amazon Translate',
    'Amazon VPC (NAT Gateway)',
    'Amazon WorkMail',
    'Amazon WorkSpaces',
    'Amazon MQ',
    'aMC Synthetic App',
    'AMP',
    'Android',
    'Android Webkit',
    'Angular',
    'AngularJS',
    'Ansible',
    'Ansible Tower',
    'Apache Axis2',
    'Apache Camel',
    'Apache Cassandra',
    'Apache Cassandra (Remote)',
    'Apache Cordova',
    'Apache CouchDB',
    'Apache CXF',
    'Apache HTTP Server',
    'Apache JMeter',
    'Apache Kafka',
    'Apache OpenEJB',
    'Apache Solr',
    'Apache Spark',
    'Apache Storm',
    'Apache Tomcat',
    'Apache TomEE',
    'Apigee Edge',
    'Apple Safari',
    'ASP.NET / ASP.NET Core',
    'ASP.NET Owin/Katana',
    'Atlassian Bamboo',
    'Atlassian JIRA',
    'AWS',
    'AWS AppSync',
    'AWS Billing and Cost Management',
    'AWS Chatbot',
    'AWS CloudHSM',
    'AWS CodeDeploy',
    'AWS CodePipeline',
    'AWS Database Migration Service',
    'AWS DataSync',
    'AWS Direct Connect',
    'AWS Elastic Beanstalk',
    'AWS Elastic Load Balancing',
    'AWS Elemental MediaConnect',
    'AWS Elemental MediaConvert',
    'AWS Elemental MediaPackage',
    'AWS Elemental MediaTailor',
    'AWS Fargate',
    'AWS Glue',
    'AWS IoT',
    'AWS IoT Analytics',
    'AWS IoT Things Graph',
    'AWS Lambda',
    'AWS OpsWorks',
    'AWS Outposts',
    'AWS PrivateLink',
    'AWS Service Catalog',
    'AWS Step Functions',
    'AWS Storage Gateway',
    'AWS Systems Manager',
    'AWS Transit Gateway',
    'AWS Trusted Advisor',
    'AWS Web Application Firewall (WAF)',
    'Azul Platform Core (Zulu)',
    'Azul Platform Prime (Zing)',
    'BellSoft Liberica',
    'Bitbucket',
    'BizTalk Plugin 2.0',
    'Blazemeter',
    'BOSH bpm',
    'Business events',
    'C',
    'CakePHP',
    'CentOS',
    'Chef',
    'Citrix NetScaler ADC',
    'Citrix Virtual Apps and Desktops',
    'Cloud Automation Control Plane',
    'Cloud Foundry',
    'Composer',
    'Concourse',
    'Confluent Cloud (Kafka)',
    'Connection Pools: JBoss',
    'Connection Pools: Tomcat',
    'Connection Pools: WebLogic',
    'Connection Pools: WebSphere Liberty',
    'Consul Service Mesh (StatsD)',
    'containerd',
    'Control-M Jobs',
    'CoreDNS',
    'Couchbase',
    'cri-o',
    'Custom database queries',
    'Custom Data ingest via API',
    'Databricks',
    'Davis Assistant',
    'DC/OS',
    'Debian',
    'Disk Analytics',
    'Docker',
    'Drupal',
    'Dynatrace API Gateway by ESA',
    'Dynatrace ETL Service by ESA',
    'Dynatrace Integration for Jira',
    'Dynatrace mobile app for Android',
    'Dynatrace mobile app for iOS',
    'Dynatrace Self-Monitoring (Managed)',
    'Dynatrace Solution Server by ESA',
    'Eclipse Jetty',
    'Eclipse OpenJ9',
    'Eclipse Temurin (Adoptium)',
    'Elasticsearch',
    'Erlang',
    'etcd for OpenShift',
    'Express',
    'Extensions Health',
    'F5 BIG-IP LTM',
    'Fedora',
    'Filesystem monitoring',
    'Flagsmith JavaScript Integration',
    'Fluentd',
    'Flutter',
    'Fortinet Fortigate',
    'Fujitsu Interstage',
    'Fujitsu Interstage IHS',
    'Fujitsu JVM',
    'Garden-RunC',
    'Gatling',
    'Generic Cisco Device',
    'Generic Linux Commands',
    'Generic network device',
    'Gigamon HAWK Deep Observability Pipeline',
    'GlassFish',
    'Go',
    'GraalVM',
    'Grail',
    'GraphQL',
    'Gremlin for Cloud Automation',
    'Gremlin for Dynatrace',
    'gRPC',
    'Hadoop HDFS',
    'Hadoop YARN',
    'HAProxy',
    'HAProxy (Prometheus)',
    'HashiCorp Terraform',
    'Hazelcast',
    'Heroku',
    'Hitachi JVM',
    'How fast is your app?',
    'Huawei JVM',
    'IBM AIX',
    'IBM App Connect Enterprise',
    'IBM Bluemix',
    'IBM CICS Transaction Gateway for z/OS',
    'IBM CICS Transaction Server',
    'IBM Cloud Foundry',
    'IBM Cloud Kubernetes Service',
    'IBM DataPower',
    'IBM DB2',
    'IBM DB2 LUW',
    'IBM Event Streams',
    'IBM HTTP Server',
    'IBM i',
    'IBM IMS',
    'IBM IMS SOAP Gateway',
    'IBM Informix',
    'IBM Integration Bus',
    'IBM JVM',
    'IBM MQ',
    'IBM MQ - ActiveGate',
    'IBM Semeru',
    'IBM WebSphere Application Server',
    'IBM WebSphere Application Server for z/OS',
    'IBM WebSphere Liberty',
    'IBM WebSphere Liberty for z/OS',
    'IBM WebSphere Message Broker',
    'IBM z/OS',
    'IBM z/OS Connect Enterprise Edition',
    'InterSystems IRIS (Remote)',
    'Ionic',
    'iOS',
    'iOS Safari',
    'ISAM',
    'Istio',
    'Istio and Envoy Service Mesh (Prometheus)',
    'Java',
    'Java JDBC',
    'Java JMS',
    'JBoss Enterprise Application Platform',
    'Joomla',
    'jQuery',
    'Juniper Networks (SNMP)',
    'Jython',
    'Keptn',
    'Kestrel for ASP.NET Core',
    'Kong Gateway',
    'Kubernetes',
    'Kubernetes Monitoring Statistics',
    'Kubernetes persistent volume claims',
    'KVM',
    'Laravel',
    'LaunchDarkly for Cloud Automation',
    'LaunchDarkly Integration for Dynatrace',
    'LDAP',
    'LDAP Synthetic',
    'Lightrun Developer Observability Platform',
    'LinkerdD',
    'Linkerd Service Mesh (Prometheus)',
    'Linux',
    'Linux on IBM Z mainframe',
    'LoadRunner',
    'Log Management and Analytics powered by Grail',
    'Logstash',
    'Magento',
    'MariaDB',
    'Maven',
    'Memcached',
    'Micrometer',
    'Microsoft Active Directory replication',
    'Microsoft Azure',
    'Microsoft Edge',
    'Microsoft Exchange Server',
    'Microsoft Hyper-V',
    'Microsoft Hyper-V (WMI)',
    'Microsoft IIS',
    'Microsoft Internet Explorer',
    'Microsoft Message Queuing (MSMQ)',
    'Microsoft SQL Server',
    'Microsoft Teams',
    'Microsoft Visual Studio',
    'MongoDB',
    'Mongo DB Atlas',
    'MongoDB (Prometheus)',
    'Mozilla Firefox',
    'Mulesoft Cloudhub (Extension v2)',
    'MySQL',
    'MySQL (remote monitoring)',
    'Nagios Integration',
    'Neo4j',
    'NeoLoad',
    'NetApp on Google Cloud',
    'NetApp OnTap (Remote)',
    'Netbackup Jobs',
    '.NET Framework',
    '.NET / .NET Core',
    'Netty',
    'NGINX',
    'NGINX Plus',
    'Nobl9 SLO Platform',
    'Node.js',
    'NTP sync check',
    'Nutanix AHV',
    'NVIDIA GPUs',
    'Omniscopy',
    'OpenJDK',
    'OpenShift Control Plane',
    'openSUSE',
    'OpenTelemetry Metrics',
    'OpenTelemetry Tracing',
    'OpenTracing',
    'Opera',
    'Opsgenie',
    'Oracle Cloud',
    'Oracle Database',
    'Oracle Hotspot VM',
    'Oracle HTTP Server',
    'Oracle JRockit',
    'Oracle Solaris',
    'Oracle WebLogic',
    'OutSystems Cloud Metrics',
    'PagerDuty',
    'Palo Alto firewalls',
    'Payara',
    'Perl',
    'PHP',
    'PHPUnit',
    'Ping Every Second',
    'Pivotal Platform',
    'Play Framework',
    'PostgreSQL',
    'Prometheus',
    'Prometheus Alertmanager',
    'Prometheus in Kubernetes',
    'Python',
    'QEMU',
    'RabbitMQ',
    'RabbitMQ (Prometheus)',
    'React.js',
    'React Native',
    'Reactor Core',
    'Red Hat Enterprise Linux',
    'Red Hat Enterprise Linux CoreOS',
    'Red Hat Fuse',
    'Red Hat OpenShift',
    'Red Hat OpenStack',
    'Red Hat Quarkus',
    'Redis',
    'Redis Enterprise',
    'Redis Enterprise - Prometheus',
    'Redis Open Source',
    'Remote Desktop Protocol',
    'Remote Unix Monitoring',
    'Remote Windows Host Monitoring',
    'Riak',
    'Rookout Live Debugger',
    'Ruby',
    'Ruby on Rails Agent',
    'Runtime Application Protection',
    'Runtime vulnerability detection',
    'Salesforce Streaming API',
    'SAP Business Technology Platform',
    'SAP Commerce Cloud',
    'SAP GUI and ABAP platform',
    'SAP HANA Database',
    'SAP JVM',
    'Scala',
    'Selenium WebDriver',
    'Sencha Touch',
    'ServiceNow',
    'servicetrace',
    'Session Replay',
    'Siebel',
    'SIGNL4 – Critical Mobile Alerting',
    'Slack',
    'SNMP Traps',
    'Snyk',
    'Solarwinds',
    'Spring',
    'SSL Checker',
    'StatsD',
    'SUSE Linux Enterprise Server',
    'Symfony',
    'Synthetic monitor DNS',
    'Synthetic monitor Ping',
    'Synthetic monitor Ports',
    'Synthetic Monitor SSH',
    'Synthetic SFTP monitor',
    'TeamCity',
    'Telegraf',
    'TIBCO EMS',
    'Timeseries Streamer',
    'Trello',
    'Tricentis NeoLoad for Cloud Automation',
    'T-Systems / Jenkins',
    'tvOS',
    'Ubuntu',
    'Varnish',
    'Varnish Cache',
    'versio.io',
    'Vert.x',
    'VictorOps',
    'VMware',
    'VMware Cloud on AWS',
    'VMware ESXi Host',
    'VMware Horizon',
    'VMware Tanzu',
    'VMware Unified Access Gateway',
    'VMware VCenter Alarms',
    'VMware vCenter Server',
    'VMware vSAN',
    'WebHooks',
    'WeChat Mini-Program Monitoring',
    'Wildfly',
    'Windows',
    'Windows Communication Foundation (WCF)',
    'Windows Scheduled Tasks',
    'Windows Server File System Quotas',
    'WIPRO Holmes',
    'WordPress',
    'WSO2 API Manager',
    'Xamarin',
    'Xcode',
    'Xen',
    'xMatters',
    'Yii',
    'Zabbix hosts',
    'Zabbix Integration',
    'Zenduty',
    'ZigiOps - Integration Platform',
]


def list_selected_links(filtering):
    page = requests.get('https://www.dynatrace.com/hub/')
    soup = BeautifulSoup(page.text, 'html.parser')

    lines = []

    for link in soup.find_all('a'):
        title = link.get('title')
        href = link.get('href')
        description = link.find('p', class_='store-logowall__description-body')
        if description:
            description = description.text
        if href.startswith('/'):
            href = f'https://dynatrace.com{href}'
        if title:
            if filtering and (title.startswith('Azure') or title.startswith('Google') or title in exclude_list):
                pass
            else:
                comment = get_comment(title)
                line = f'{title}|{description}|{comment}|{href}'
                lines.append(line)

    for line in sorted(lines, key=str.lower):
        print(line)

    write_xlsx(sorted(lines, key=str.lower))
    write_html(sorted(lines, key=str.lower))


def build_how_to_monitor_dict():
    how_to_monitor_dict = {}
    page = requests.get('https://www.dynatrace.com/hub/')
    soup = BeautifulSoup(page.text, 'html.parser')

    for link in soup.find_all('a'):
        title = link.get('title')
        if title:
            if title.startswith('Azure') or \
                    title.startswith('Google') or \
                    title in exclude_list:
                pass
            else:
                comment = get_comment(title)
                how_to_monitor_dict[title] = {'comment': comment, 'link': ''}

    return how_to_monitor_dict


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
        'NetApp on Google Cloud',    ]

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
        'Logstash',
        'Micrometer',
        'Neo4j',
        'OpenTelemetry Metrics',
        'OpenTelemetry Tracing',
        'OpenTracing',
        'Perl',
        'PHP',
        'StatsD',
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
        'Google Analytics': 'Configure Session and User Action properties in RUM settings for the web application.',
        'Session Replay': 'Configure Session Replay in RUM settings for the web application.',
        'Davis Assistant': 'Deprecated: do not use.',
        'Dynatrace Solution Server by ESA': 'Install to leverage the Dynatrace API Gateway by ESA and/or the Dynatrace ETL Service by ESA.',
        'Python': 'Install OneAgent for process monitoring, and optionally use OpenTelemetry, SDK or Python Auto-Instrumenation from Github for tracing.',
        'gRPC': 'Install OneAgent and turn on gRPC OneAgent feature for language.',
        'LoadRunner': 'Configure request attributes, etc.  See blog posts, RobotAdmin, etc.',
        'Business events': 'If GRAIL is active, see link for details on configuring business events.',
        'DC/OS': 'Install the Dynatrace package via the DC/OS user interface.',
        'C': 'Use the Dynatrace SDK.',
        'LDAP': 'The link explains how to use manage users and groups via LDAP. To monitor LDAP, install a OneAgent for Host/Process monitoring and/or install the LDAP Synthetic Extension.',
        'Microsoft Active Directory replication': 'Install extension both on a OneAgent and on the Dynatrace Cluster.  See hub link for more details.',
        'Runtime Application Protection': 'Activate the Application Security module.  Just contact us via in-product chat or directly via your account team.',
        'Runtime vulnerability detection': 'Activate the Application Security module.  Just follow instructions in the hub link.',
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

def write_xlsx(lines):
    workbook = xlsxwriter.Workbook('../../docs/HubSynopsis.xlsx')
    header_format = workbook.add_format({'bold': True, 'bg_color': '#B7C9E2'})

    worksheet = workbook.add_worksheet('Hub Synopsis')

    row_index = 0
    # column_index = 0

    headers = ['Technology', 'Hub Description', 'Monitoring Synopsis']
    worksheet.write(row_index, 0, headers[0], header_format)
    worksheet.write(row_index, 1, headers[1], header_format)
    worksheet.write(row_index, 2, headers[2], header_format)
    row_index += 1


    for line in lines:
        columns = line.split('|')
        worksheet.write_url(row_index, 0, columns[3], string=columns[0])
        worksheet.write(row_index, 1, columns[1])
        worksheet.write(row_index, 2, columns[2])
        row_index += 1

    # worksheet.autofilter(0, 0, row_index, len(headers)) # add filter to all columns not needed here...
    worksheet.autofilter(0, 2, row_index, 2) # add filter to only the third column
    worksheet.autofit()
    workbook.close()


def write_html(lines):
    filename = '../../docs/HubSynopsis.html'

    html_top = '''<html>
      <body>
        <head>
          <style>
            table, th, td {
              border: 1px solid black;
              border-collapse: collapse;
            }
            th, td {
              padding: 5px;
            }
            th {
              text-align: left;
            }
          </style>
        </head>'''

    table_header = '''    <table>
          <tr>
            <th>Technology</th>
            <th>Hub Description</th>
            <th>Monitoring Synopsis</th>
          </tr>'''

    html_bottom = '''    </table>
      </body>
    </html>'''

    row_start = '<tr>'
    row_end = '</tr>'
    col_start = '<td>'
    col_end = '</td>'

    with open(filename, 'w', encoding='utf8') as file:
        # Begin HTML formatting
        write_line(file, html_top)

        # Write the tag summary header
        write_h1_heading(file, f'Dynatrace Hub Synopsis')

        # Write Table Header
        write_line(file, table_header)

        # Write Table Rows
        for line in lines:
            columns = line.split('|')
            tech_link = f'<a href="{columns[3]}">{columns[0]}</a>'
            write_line(file, f'{row_start}{col_start}{tech_link}{col_end}{col_start}{columns[1]}{col_end}{col_start}{columns[2]}{col_end}{row_end}')

        # Finish the HTML formatting
        write_line(file, html_bottom)


def write_h1_heading(outfile, heading):
    outfile.write('    <h1>' + heading + '</h1>')
    outfile.write('\n')


def write_line(outfile, content):
    outfile.write(content)
    outfile.write('\n')


if __name__ == '__main__':
    filter_output = False
    list_selected_links(filter_output)

    # how_to_monitor_dict = build_how_to_monitor_dict()
    # for how_to_monitor in how_to_monitor_dict.items():
    #     print(f"    '{how_to_monitor[0]}': {how_to_monitor[1]},")


