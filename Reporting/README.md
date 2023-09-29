## Reporting

This subproject facilitates summary and detail reporting, as well as providing a framework for "auditing" a tenant for adherence to standards.

A full report can be run, or individual reports can be run for specific settings.

To create an HTML "audit" report, run [perform_summarize_environment_html.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Reporting/perform_summarize_environment_html.py).

Be sure to set up the required environment variables before you run it.

```commandline
env_name, tenant_key, token_key = ('Demo', 'DEMO_TENANT', 'ROBOT_ADMIN_DEMO_TOKEN')
```
An example HTML audit report can be viewed [here](https://dynatrace-dave-mauney.github.io/Automation/Example_Environment_Summary.html).

You can optionally add "findings" by creating a text file with your comments under each "heading" that matches one in the audit report ("Cluster Summary", "ActiveGate Summary", etc.).

You can see the default findings file name, and modify it if you wish, in the [findings_loader.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Reporting/findings_loader.py).



