# Getting Started

- Install Python 
  - Download Python [here](https://www.python.org/downloads/)
  - Open a command prompt or terminal and execute the "py" command
  - Verify the version mentioned is the one you installed
  - Verify there is a ">>>" prompt indicating you are interacting with the Python terminal 
  - Enter "help()" and verify it works
  - Enter "quit" to exit help
  - Enter "quit()" to exit the Python terminal
  
- Download the "Automation" repository
  - This can be done using "git clone" if you are familiar with git
  - Otherwise, simply download a zip of the repository and expand it in a directory of your choice
  - Either way, you will need to click the green "Code" button on [this page](https://github.com/Dynatrace-Dave-Mauney/Automation)

- Configure a virtual environment
  - Open a command prompt/terminal
  - In the root of your Automation directory, run the "py -m venv venv" command
  - Verify there is now a "venv" subdirectory in your Automation directory
  - Run the virtual environment "activate"" command
    - Windows example: "venv\Scripts\activate.bat"
    - Linux example: "source venv/bin/activate"
    - You should see a "(venv)" appear in your prompt when it is successfully activated

- Run MultiTool to test your configuration
  - Change into the MultiTool directory (for example: "cd Tools\MultiTool on Windows")
  - Run the MultiTool module (Execute "py multi_tool.py")
  - You will likely get a message like "ModuleNotFoundError: No module named 'requests'".  If so, follow the steps for resolving requirements below.  
  - If you get a message like the following, follow the "Set Required Environment Variables" steps below
  - Once you can run "MultiTool" and get a ">" prompt, your "Automation" installation is complete

- Resolve Requirements
  - Your Python Virtual Environment will need various dependencies installed
  - Change directory to the root Automation directory, where the "requirements.txt" file resides
  - Run the "pip install -r requirements.txt" from the OS command prompt (not Python terminal)

- Set Required Environment Variables
  - There are two key environment variables needed for almost all modules: Tenant and Token
  - These can be seen in the example Python code below:
  - env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
  - Here the friendly environment name of "Prod" is associated with two environment variables ("PROD_TENANT" and "ROBOT_ADMIN_PROD_TOKEN").
  - This naming standard is only a suggestion, but it does simplify things to include the environment (PROD), function (ROBOT_ADMIN) and variable type (TENANT or TOKEN).
  - You will need to set up your own environment variables and name them to suit your needs.
  - You will need to modify each module to reference the appropriate set of values.
  - Use [TokenManagement](https://github.com/Dynatrace-Dave-Mauney/Automation/tree/main/TokenManagement) to create your Token or do it manually
  - If you do it manually, see "Robot Admin Token Permissions" below for permissions needed 
  - For managed installs, you will need to modify the code to pass the "environment" required rather than "tenant" (out of scope for this document).
  - See "Windows setEnv.bat Example" below for an example script for Windows.

- Windows setEnv.bat Example

```
@echo off

rem Be sure to restart your PyCharm IDE after this script runs to use the new environment variable settings

setx PROD_TENANT prd12345
setx PREP_TENANT prp12345
setx DEV_TENANT dev12345

setx ROBOT_ADMIN_PROD_TOKEN dt0c01.*
setx ROBOT_ADMIN_PREP_TOKEN dt0c01.*
setx ROBOT_ADMIN_DEV_TOKEN dt0c01.*

setx TOKEN_MANAGEMENT_PROD_TOKEN dt0c01.*
setx TOKEN_MANAGEMENT_PREP_TOKEN dt0c01.*
setx TOKEN_MANAGEMENT_DEV_TOKEN dt0c01.*

setx DASHBOARD_OWNER_EMAIL somebody.important@example.com
```

- Robot Admin Permissions

```
CaptureRequestData
DTAQLAccess
DataExport
DataImport
DssFileManagement
ExternalSyntheticIntegration
LogExport
ReadConfig
ReadSyntheticData
WriteConfig
activeGateTokenManagement.read
activeGates.read
apiTokens.read
auditLogs.read
credentialVault.read
entities.read
entities.write
events.ingest
events.read
extensionConfigurations.read
extensionEnvironment.read
extensions.read
geographicRegions.read
hub.read
metrics.read
networkZones.read
problems.read
releases.read
settings.read
settings.write
slo.read
syntheticExecutions.read
syntheticLocations.read```
