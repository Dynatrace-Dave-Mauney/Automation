# Getting Started

By far, the easiest way to get started is to continue to "PyCharm Configuration (with git integration)".

If you plan to work primarily in the PyCharm IDE, continue by following the steps under "PyCharm Configuration (with git integration)" or "PyCharm Configuration (without git integration)".

If you plan to work primarily in the command line/terminal, continue by following the steps under "Command Line Configuration".

## Common Configuration

- Install Python 
  - Download Python [here](https://www.python.org/downloads/)
  - It is recommended to add the python folder to the path for Windows
  - Open a command prompt or terminal and execute the "py" command
  - Verify the version mentioned is the one you installed
  - Verify there is a ">>>" prompt indicating you are interacting with the Python terminal 
  - Enter "help()" and verify it works
  - Enter "quit" to exit help
  - Enter "quit()" to exit the Python terminal
  
- Download the "Automation" repository
  - This can be done using "git clone", if you are familiar with git
  - Otherwise, simply download a zip of the repository and expand it in a directory of your choice
  - Either way, you will need to click the green "Code" button on [this page](https://github.com/Dynatrace-Dave-Mauney/Automation) to start the process

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

Unless you also plan to use PyCharm, continue to the "Configure Automation Project" section.

## PyCharm Configuration (with git integration)

  - If you need to, [download](https://www.jetbrains.com/pycharm/download) and install PyCharm.  Be sure to select the "Community" edition, unless you need Professional.
  - Start PyCharm
  - Click the "Get from VCS" button
  - If Git is not installed, click "Download and Install"
  - Enter "https://github.com/Dynatrace-Dave-Mauney/Automation.git" in the URL dropdown
  - Click the "Clone" button
  - Open Tools\MultiTool\multi_tool.py
  - At the top right, click "Create a virtual environment using requirements.txt"
  - Run "multi_tool.py" using Ctrl-Shift-F10 (or the run button)
  - When prompted, select the Python executable under the "venv" folder
  - You will not be able to actually run "multi_tool.py" until you complete the "Configure Automation Project" section below.

## PyCharm Configuration (without git integration)

  - Delete the ".idea\vcs.xml" file
  - If you need to, [download](https://www.jetbrains.com/pycharm/download) and install PyCharm.  Be sure to select the "Community" edition, unless you need Professional.
  - Start PyCharm
  - Open the project by selecting the root Automation directory
  - Open Tools\MultiTool\multi_tool.py
  - At the top right, click "Create a virtual environment using requirements.txt"
  - Run "multi_tool.py" using Ctrl-Shift-F10 (or the run button)
  - When prompted, select the Python executable under the "venv" folder
  - You will not be able to actually run "multi_tool.py" until you complete the "Configure Automation Project" section below.

## Configure Automation Project

- Set Required Environment Variables
  - There are two key environment variables needed for almost all modules: Tenant and Token, as shown the example Python code below:

  ```
  env_name, tenant_key, token_key = ('Prod', 'PROD_TENANT', 'ROBOT_ADMIN_PROD_TOKEN')
  ```
  - Here the friendly environment name of "Prod" is associated with two environment variables ("PROD_TENANT" and "ROBOT_ADMIN_PROD_TOKEN").
  - This naming standard is only a suggestion, but it does simplify things to include the environment (PROD), function (ROBOT_ADMIN) and variable type (TENANT or TOKEN) in the names.
  - You will need to set up your own environment variables and name them to suit your needs.
  - You will need to modify each module to reference the appropriate set of values.
  - Use [TokenManagement](https://github.com/Dynatrace-Dave-Mauney/Automation/tree/main/TokenManagement) to create your Token, or do it manually using the "Access tokens" menu item in the Dynatrace UI.
  - If you do it manually, see the "Robot Admin Token Permissions" section below for permissions needed 
  - For managed installs, you will need to modify the code to pass the "environment" required rather than "tenant" (out of scope for this document).
  - See "Windows setEnv.bat Example" below for an example script for setting environment variables on Windows.
  - After setting the environment variables using  [TokenManagement](https://github.com/Dynatrace-Dave-Mauney/Automation/tree/main/TokenManagement) or manually, be sure to restart your terminal or PyCharm in order to pick up the newly added environment variables.
  - If you get SSL certificate issues see the "Troubleshooting" section


- Windows setEnv.bat Example

```
@echo off

rem Be sure to restart your PyCharm IDE after this script runs to use the new environment variable settings

setx DYNATRACE_PROD_TENANT prd12345
setx DYNATRACE_PREP_TENANT prp12345
setx DYNATRACE_DEV_TENANT dev12345

setx ROBOT_ADMIN_PROD_TOKEN dt0c01.*
setx ROBOT_ADMIN_PREP_TOKEN dt0c01.*
setx ROBOT_ADMIN_DEV_TOKEN dt0c01.*

setx TOKEN_MANAGEMENT_PROD_TOKEN dt0c01.*
setx TOKEN_MANAGEMENT_PREP_TOKEN dt0c01.*
setx TOKEN_MANAGEMENT_DEV_TOKEN dt0c01.*

setx DYNATRACE_DASHBOARD_OWNER somebody.important@example.com
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
syntheticLocations.read
```

## Command Line Configuration

1. Set up a virtual environment

Adjust path as needed.

cd \Dynatrace\github\Automation
py -m venv .venv
.venv\Scripts\activate.bat
Watch for prompt to change to "(.venv)"

Each time going forward you will need to run "activate.bat" to get back into the virtual environment.

2. Install requirements

pip install -r requirements.txt

3. Allow imports from the "Reuse" directory

From the Automation root directory:

pip install --editable .

4.  Try running MultiTool per instructions above

Edit the "Tools\MultiTool\mult_tool.py" module to default to one of your tenants.

From the Automation root directory:

py Tools\MultiTool\mult_tool.py

## Troubleshooting

## Self-signed certificate in certificate chain  

If you get a message like "self signed certificate in certificate chain" (Example: "requests.exceptions.SSLError: HTTPSConnectionPool(host='SOMETENANT.live.dynatrace.com', port=443): Max retries exceeded with url: /api/some/api (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain (_ssl.c:1129)')))"):

Use either "Tools/certificate/certificate_chain_pem_file.py" to create a "crt" file with the certificate chain, or access the tenant in your browser and use the "lock" icon to export the chain to a file. 

Then set the following environment variables to allow trust:
 
Windows   
setx SSL_CERT_FILE \path\to\cert\file.crt
setx REQUESTS_CA_BUNDLE \path\to\cert\file.crt

Linux  
export SSL_CERT_FILE /path/to/cert/file.crt
export REQUESTS_CA_BUNDLE /path/to/cert/file.crt

Reference  
https://stackoverflow.com/questions/30405867/how-to-get-python-requests-to-trust-a-self-signed-ssl-certificate

# "Unable to get local issuer certificate" errors

This issue may occur on some Windows installs of Python when using "requests" (which is used for all API calls).

This [fix](https://stackoverflow.com/questions/51925384/unable-to-get-local-issuer-certificate-when-using-requests-in-python) should solve it: 

In the PyCharm terminal, run these commands:

pip install --upgrade certifi
pip install python-certifi-win32

Then try rerunning the module that failed.
