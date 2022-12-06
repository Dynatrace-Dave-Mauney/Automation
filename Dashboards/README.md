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

