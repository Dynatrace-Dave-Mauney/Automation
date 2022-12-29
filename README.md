# Automation
The goal of this project is to facilitate Dynatrace automation with various subprojects that deal with specific automation tasks.

## Dashboards
This subproject contains many dashboard utilities and two sets of dashboard templates.

The "Overview Framework" dashboard templates are generic enough to use as a starting point with any customer.  

They are not limited to specific entities and work well with Management Zones.  

Where possible, the dashboards leverage dynamic dashboards filters to provide many fine-grained filtering options.

The dynamic filters are customizable and can include any of the many tags that can be generated with the RobotAdmin subproject.  

Use [dashboard_template_customizer.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Dashboards/dashboard_template_customizer.py) to use the desired tags for dynamic filtering, set the desired email address, modify the "TEMPLATE: " prefix, control the sharing options, and so forth.  

The "Curated" dashboard templates consist of various dashboards that are not (yet?) incorporated into the "Overview" templates.

These can be modified and PUT on the target tenant with [put_dashboards.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Dashboards/put_dashboards.py).  Modification of the dashboard name and owner email address are included, but additional modifications can be coded here as needed.

Notes:  
The Overview dashboard provides drill down capability to many child dashboards via markdown tiles.  

Always use PUT rather than POST as the IDs are designed to remain static and PUT allows that.

## DynatraceDashboardGenerator
The intent of this subproject is to allow creation of Dynatrace Dashboards based on a YAML file that can be generated initially and then modified, if desired, to produce a variety of simple dashboards based on the full set of metrics available in the environment.

The focus is on generating a dashboard for each "category" of metrics, such as all
Host metrics, or all AWS metrics, for example.

Data Explorer line charts are used now for all metrics, by default.

One diminsion is used for each chart.

The idea is to generate dashboards that allow visualization of the data and allow curation into more organized and permanent versions as desired.

To get started, simply run the "perform_entire_process.py" module from your IDE (I like PyCharm, personally) or from a command line.

Use "perform_entire_process.py" to run the whole generation process.
And refer to it for ways to modify the automation.  

Always use PUT rather than POST for uploading the dashboards as the IDs are designed to remain static and PUT allows that.  This is handled automatically, if you use the supplied "put_all_dashboards_util.py" module to upload dashboards.  

## DynatraceSettingsBackup

This subproject facilitates taking a backup of all Dynatrace Settings (1.0 and 2.0), as well as offering the possibility to "restore" from a backup YAML file.

Backups can be taken in two formats:  individual JSON files in subdirectories or by creating a single monolithic YAML file.

If the YAML file is created, it can later be used for restores or updates either in mass or for individual entities.

The restore process has not been fully tested, so caution is advised when using it.

## Go

This subproject contains a few go modules that might be useful if Python is not an option.

## Reporting

This subproject facilitates summary and detail reporting, as well as providing a framework for "auditing" a tenant for adherernce to standards.

A full report can be run, or individual reports can be run for specific settings.

## RobotAdmin

- Supports Best Practice++™ implementation of Auto Tags, Request Attributes, Request Naming Rules, Conditional Naming Rules and Management Zones


- Currently, there are 115 Auto Tags, 25 Request Attributes, 3 Request Naming Rules and 8 Conditional Naming Rules supported


- Handles regex extraction of any number of host group elements to create auto tags


- Fixed IDs are used so that references can be consistent across multiple tenants


- Also supports creating web applications, web application routing rules, listing objects, deleting objects, updating objects and more.


To get started, edit the process() method of [robot_admin.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/RobotAdmin/robot_admin.py) by copying one or more of the usage examples under the environment print statements.

For example, to create all supported automatic tags:

```  
  print('Environment:     ' + env_name)
  print('Environment URL: ' + env)

  process_all_auto_tags()
  exit(123)
```

## Scripts

This subproject contains some scripts for reference:

- An example of ingesting directory file counts into Dynatrace.

 
- An example of configuring nested (not recommended) file systems for Dynatrace Managed.


- The more difficult nested scenario can be referenced for the more simple recommended way of not nesting.

## Snippets

This subproject contains various code snippets and notes for quick reference.

## TokenManagement

This subproject facilitates Dynatrace token management.

It supports various actions such as:

- Create Token
- Delete Token
- Rotate Token
- List Tokens

To get started, create a "Token Management" API token in the Dyntrace UI with the following permissions:

- Read API tokens
- Write API tokens

Set your environment variables to allow access to your tenant and token.

Use one of the predefined methods or clone one to customize the name and permissions.

Examples of some predefined create token methods:

- post_robot_admin()
- post_monaco()
- post_reporting()
- post_test_token()
- post_dashboard_generator()

By default, the process method should run the following methods to simply create a test token and immediately delete it:

```
test_token = post_test_token()
delete(test_token)
```

## Tools

This subproject facilitates running various simple tools.

The "MultiTool" interactive module allows for easy interaction with the Dynatrace API, covering:

- Configuration V1
- Entities (V1 and V2)
- Events
- Metrics
- Settings 2.0

Switch between environments easily using a friendly name with no token copy/pasting needed!

List items, view JSON for a specific item and save the JSON all from an easy command line interface!

There are also standalone tools covering: 

- APISpecs
- Certificates
- Configuration APIs
- Entities
- Events
- Files
- Metrics
- Settings 2.0