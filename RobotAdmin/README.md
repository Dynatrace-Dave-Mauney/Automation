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

See "README.txt" for more details.