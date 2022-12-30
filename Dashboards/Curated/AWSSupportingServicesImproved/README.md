# AWSSupportingServicesImproved

The dashboards generated when AWS Supporting Services are monitored still use custom charts.

These dashboards have been converted with [dynatrace_aws_supporting_services_conversion.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Dashboards/dynatrace_aws_supporting_services_conversion.py) so that they use Data Explorer tiles.

The owner is changed to "nobody@example.com".  Change it when you PUT the dashboards on the tenant with [put_dashboards.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Dashboards/put_dashboards.py).

The [menu dashboard](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Dashboards/Curated/AWSSupportingServicesImproved/aaaaaaaa-bbbb-cccc-eeee-f00000000000.json) was generated using [generate_menu.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Dashboards/generate_menu.py).

The Dynatrace-owned dashboards can be hidden (not deleted) after the conversion.



