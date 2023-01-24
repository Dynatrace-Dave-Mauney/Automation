## Reporting

This subproject facilitates summary and detail reporting, as well as providing a framework for "auditing" a tenant for adherence to standards.

A full report can be run, or individual reports can be run for specific settings.

To create an HTML "audit" report, run [perform_summarize_environment_html.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Reporting/perform_summarize_environment_html.py).

Be sure to set up the required environment variables before you run it.

```commandline
env_name, tenant_key, token_key = ('FreeTrial1', 'FREETRIAL1_TENANT', 'ROBOT_ADMIN_FREETRIAL1_TOKEN')
```
An example HTML audit report can be viewed [here](https://dynatrace-dave-mauney.github.io/Automation/Example_Environment_Summary.html).



