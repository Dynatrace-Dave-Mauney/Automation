## DynatraceDashboardGenerator
The intent of this subproject is to allow creation of Dynatrace Dashboards based on a YAML file that can be generated initially and then modified, if desired, to produce a variety of simple dashboards based on the full set of metrics available in the environment.

The focus is on generating a dashboard for each "category" of metrics, such as all Host metrics, or all AWS metrics, for example.

Data Explorer line charts are used for all metrics, by default.

One dimension is used for each chart.

The idea is to generate dashboards that allow visualization of the data and allow curation into more organized and permanent versions as desired.

To get started, simply modify the tenant and token information in [perform_entire_process.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/perform_entire_process.py) module and run it from your IDE (I like PyCharm, personally) or from a command line.

Use the [perform_entire_process.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/perform_entire_process.py) module to run the complete generation process, and refer to it for ways to modify the automation.

Use the [perform_restart_of_process.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/perform_restart_of_process.py) module to re-run part of the generation process.

After generating dashboards, use the [generate_menu_from_dashboard_index.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Dashboards/generate_menu_from_dashboard_index.py) module if you want to create a "menu" to easily access the dashboards.

Always use PUT rather than POST for uploading the dashboards as the IDs are designed to remain static and PUT allows that.  This is handled automatically, when you use the [put_dashboards.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Dashboards/put_dashboards.py) module to upload dashboards.  
Alternatively, you can run [put_all_dashboards_util.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/put_all_dashboards_util.py) from within [perform_entire_process.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/perform_entire_process.py) (where it is normally commented out to allow for manual post-processing).

The [dashboard_blueprint.yaml](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/dashboard_blueprint.yaml) is used to control which metrics are placed on each dashboard.
Use the [analyze_metric_coverage.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/DynatraceDashboardGenerator/analyze_metric_coverage.py) module to find gaps in the coverage.