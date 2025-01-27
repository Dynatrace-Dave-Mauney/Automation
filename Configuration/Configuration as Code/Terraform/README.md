# Overview
The purpose of this project is to simplify the adoption of Dynatrace Configuration as Code via the use of templates, examples, and so forth.

This project covers Dynatrace Configuration as Code facilitated via Terraform.

# Documentation
[Dynatrace Configuration as Code via Terraform](https://docs.dynatrace.com/docs/shortlink/configuration-as-code-terraform) 

## Current Installation Notes

Note: This summarizes/extends the official Dynatrace Documentation page:
[Install CLI and Terraform Provider](https://docs.dynatrace.com/docs/shortlink/terraform-cli).

1)  Download the [Terraform Binary](https://developer.hashicorp.com/terraform/install)

2)  Extract "terraform.exe" from the zip and copy to a directory of your choice.

3)  Add the "terraform path" to your system or user path on Windows.

4)  Copy the "providers.tf" file to your Terraform Project Directory.

5)  Run the "terraform init" command

6) Create a Dynatrace Access Token with at least the following permissions:
    Read configuration (ReadConfig)  
    Write configuration (WriteConfig)  
    Read settings (settings.read)  
    Write settings (settings.write)  

7)  To create a token that works for all configurations, also include the following permissions.
    Create and read synthetic monitors, locations, and nodes (ExternalSyntheticIntegration)  
    Capture request data (CaptureRequestData)  
    Read credential vault entries (credentialVault.read)  
    Write credential vault entries (credentialVault.write)  
    Read network zones (networkZones.read)  
    Write network zones (networkZones.write)  

8)  Copy the Dynatrace Provider executable into the Terraform Project Directory for easier access (or make a symlink or add the path to your Windows path).

    The directory will be named something like:  
    terraform_1.10.5_windows_386\.terraform\providers\registry.terraform.io\dynatrace-oss\dynatrace\1.72.6\windows_386

    The exe will be named something like:  
    terraform-provider-dynatrace_v1.72.6.exe  

    Example:
    copy terraform-provider-dynatrace_v1.72.6.exe ..\..\..\..\..\..\..  
    cd ..\..\..\..\..\..\..  
    rename terraform-provider-dynatrace_v1.72.6.exe terraform-provider-dynatrace.exe  

9)  Copy the "export.bat" file to your Terraform Project Directory.

10)  Modify the environment variables in "export.bat".

11)  Run the "export.bat" command to download all configurations supported by the Dynatrace Terraform Provider.

12)  Review the "configuration\modules" directory.  This is where you can now start changing configurations.

## OLD Installation Notes (For Reference Only!)
1)  Download zip
	https://www.terraform.io/downloads
2)  Extract zip into a folder
3)  Add the terraform executable to your user path
	Windows button
	Search "Advanced"
	Click "View advanced system settings"
	Click "Environment Variables" button
	Edit the "Path" user variable and add the path to the terraform executable 
4)  Run terraform -help to verify execution works
5)  Create "main.tf" file
6)  Copy dynatrace provider information into "main.cf" file
	Visit https://registry.terraform.io/providers/dynatrace-oss/dynatrace/latest
	Click "USE PROVIDER" button  
	Copy the configuration code  
	Paste into main.cf and save  
7)  Run terraform init  
8)  Find the dynatrace export exe deep in .terraform directory created by init
	.terraform\providers\registry.terraform.io\dynatrace-oss\dynatrace\1.12.1\windows_386\terraform-provider-dynatrace_v1.12.1.exe
9)  Generate an access token with the necessary permissions
	Token Permissions (for read-only/export):  
	Read configuration  
	Capture request data  
	Read SLO  
	Read settings  
	Read synthetic monitors, locations, and nodes  
  
	For read/write:  
	Write configuration  
	Write SLO  
	Write settings  
	Write synthetic monitors, locations, and nodes  
10) Create an "export script" to run an export of all terraform-enabled configurations
	Example:  
	set DYNATRACE_ENV_URL=https://********.live.dynatrace.com  
	set DYNATRACE_API_TOKEN=dt0c01.*.*  
	set DYNATRACE_TARGET_FOLDER=terraform_configuration  
	C:\Dynatrace\Terraform\.terraform\providers\registry.terraform.io\dynatrace-oss\dynatrace\1.12.1\windows_386\terraform-provider-dynatrace_v1.12.1.exe export  
11) Run the "export script"  
12) Verify the folder pointed to by DYNATRACE_TARGET_FOLDER is populated with configurations

## To make adds/changes/deletes:
1)  Copy a resource from the exports directory file into main.tf
2)  Modify accordingly
3)  run terraform apply
    Type "yes" if you agree with it's proposed plan
    I recommend using "exports" and "applies" for your working directories

## Easy/Safe way to destroy:
1)  terraform destroy Destroy previously-created infrastructure (ALL resources managed)
2)  terraform destroy --target dynatrace_autotag.Test (specific resource)

Another is to remove/comment out (with /* */ syntax) the resource in the tf file.
https://spacelift.io/blog/how-to-destroy-terraform-resources

## Commands
terraform -help
terraform -version
terraform init     Prepare your working directory for other commands
terraform validate Check whether the configuration is valid
terraform plan     Show changes required by the current configuration
terraform apply    Create or update infrastructure
terraform destroy  Destroy previously-created infrastructure
terraform refresh  Update the state to match remote systems
terraform show     Show the current state or a saved plan

## Token Permissions (for read-only/export):
Read configuration
Capture request data
Read SLO
Read settings
Read synthetic monitors, locations, and nodes

## To add write:
Write configuration
Write SLO
Write settings
Write synthetic monitors, locations, and nodes
