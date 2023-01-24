## MultiTool

Use MultiTool to make API calls to the config, environment v1/v2, events, metrics and settings 2.0 endpoints easily from a Python IDE or command line.

### Getting Started
Modify the supported environments as needed: 

```  
supported_environments = {
    'Prod': ('PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN'),
    'Prep': ('PREP_TENANT', 'ROBOT_ADMIN_PREP_TOKEN'),
    'Dev': ('DEV_TENANT', 'ROBOT_ADMIN_DEV_TOKEN'),
    'Personal': ('PERSONAL_TENANT', 'ROBOT_ADMIN_PERSONAL_TOKEN'),
    'FreeTrial1': ('FREETRIAL1_TENANT', 'ROBOT_ADMIN_FREETRIAL1_TOKEN'),
}
```

Modify the default environments as needed: 

```
    # Set Environment
    env_name, env, token = get_environment('Prod')
    # env_name, env, token = get_environment('Prep')
    # env_name, env, token = get_environment('Dev')
    # env_name, env, token = get_environment('Personal')
    # env_name, env, token = get_environment('FreeTrial1')
```

Next, invoke [multi_tool.py](https://github.com/Dynatrace-Dave-Mauney/Automation/blob/main/Tools/MultiTool/multi_tool.py) and read the help text to get an overview of what's possible:

```
Environment Name: FreeTrial1
Environment:      https://lqo53405.live.dynatrace.com
Token:            dt0c01.*.* (Masked)

Enter "e Prod|Prep|Dev|Personal|FreeTrial1" to change the environment. "e" without a parameter shows the current environment.
Enter "m configs|entities|entities_v1|events|metrics|settings20" to change the mode. "m" without a parameter shows the current mode.
Enter "a <api>" to set/change an api (in configs mode). "a" without a parameter shows the current api.
Enter "l to list items
Enter "la" to list apis (in configs mode)
Enter "lf <filter string>" to list items and filter for content (supports a single string with no spaces as the filter)
Enter "mq" to query a metric selector (in metrics mode)
Enter "post" to post JSON from a file path specified to a config endpoint (in configs mode)
Enter just an ID to get the JSON
Enter "s" to save JSON just viewed
Enter "q" to quit
Enter "h" to view this help message

> 
```
Enter commands like "h" for help at the ">" prompt.  
Enter "q" when you want to quit.

By default, you will be in the configs endpoint with no API set, so you will either want to use the "e" command to switch environments, or the "m" command to switch the "mode" to another endpoint before proceeding.

If you want to use the "configs" endpoint, you will typically use the "la" command to list the available APIs and then copy one to paste after the "a" command to set an API.

At this point, you can then use the "l" command to list entities, and optionally copy/paste an entity ID to "get" the object.

After you get an object, you can use the "s" command if you wish to save the JSON.

See the "help" message above (or better, in the multitool terminal) for more details.

