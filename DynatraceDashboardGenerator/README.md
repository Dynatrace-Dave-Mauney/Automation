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

