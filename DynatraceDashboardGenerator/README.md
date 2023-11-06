## DynatraceDashboardGenerator

### Overview
The intent of this subproject is to allow creation of Dynatrace Dashboards based on a YAML file that can be generated initially and then modified, if desired, to produce a variety of simple dashboards based on the full set of metrics available in the environment.

The focus is on generating a dashboard for each "category" of metrics, such as all Host metrics, or all AWS metrics, for example.

Data Explorer line charts are used for all metrics, by default.

One dimension is used for each chart.

The idea is to generate dashboards that allow visualization of the data and allow curation into more organized and permanent versions as desired.

### The easy way to get started

The easiest way to get started is to simply leverage the dashboards already generated.  

Just open one of the indexes to find dashboards you want to try:
[dashboard_index.txt](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/dashboard_index.txt) 
[dashboard_index_by_id.txt](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/dashboard_index_by_id.txt) 
[dashboard_index_by_name.txt](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/dashboard_index_by_name.txt) 

Then use [put_dashboards.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Dashboards/put_dashboards.py) or other means (import, copy/paste, the API "swagger" page, etc.) to put them in your environment.

I recommend using [put_dashboards.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Dashboards/put_dashboards.py) because the "fixed id" for each dashboard will be retained.  Using "put" on the API "swagger" page will also retain the "fixed id". 

If you have metrics in your environment not covered by an already generated dashboard, read on about how to run the process to generate dashboards.

### Running the process

To get started, simply modify the tenant and token information in [perform_entire_process.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/perform_entire_process.py) module and run it from your IDE (I like PyCharm, personally) or from a command line.

Use the [perform_entire_process.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/perform_entire_process.py) module to run the complete generation process, and refer to it for ways to modify the automation.

Use the [perform_restart_of_process.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/perform_restart_of_process.py) module to re-run part of the generation process.

After generating dashboards:
Use the [create_dashboard_index.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Dashboards/create_dashboard_index.py) to create indexes by name and id, and use the [create_menu_dashboard.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Dashboards/create_menu_dashboard.py) to create a "menu" to easily access the dashboards.

Always use PUT rather than POST for uploading the dashboards as the IDs are designed to remain static and PUT allows that.  This is handled automatically, when you use the [put_dashboards.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Dashboards/put_dashboards.py) module to upload dashboards.  
Alternatively, you can run [put_all_dashboards_util.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/put_all_dashboards_util.py) from within [perform_entire_process.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/perform_entire_process.py) (where it is normally commented out to allow for manual post-processing).

The [dashboard_blueprint.yaml](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/dashboard_blueprint.yaml) configuration file is used to control which metrics are placed on each dashboard.
Use the [analyze_metric_coverage.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/analyze_metric_coverage.py) module to find gaps in the coverage.