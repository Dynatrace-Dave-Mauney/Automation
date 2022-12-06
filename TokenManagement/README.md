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

