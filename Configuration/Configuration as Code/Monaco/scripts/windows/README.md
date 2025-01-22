# Overview
The purpose of this project is to simplify the adoption of Dynatrace Configuration as Code via the use of templates, examples, and so forth.

This project covers Dynatrace Configuration as Code facilitated via Monaco on Windows.

# How To Use This Project

## Basic Process:

1)  Download/copy the "windows" directory to a Windows machine.
2)  Rename the directory as you wish.
3)  Run the download_monaco.ps1 file from Powershell.
4)  Modify the monaco-download\manifest.yaml file:
    Change the URL (https://xxxxxxxxx.live.dynatrace.com/) to your tenant URL.
5)  Modify the monaco-download\monaco-download.bat file:
    Change the monaco-token to a valid token with the permissions you need.
    The token permissions required are covered in the "Monaco" folder README. 
6)  Modify the monaco-download\monaco-download-management-zones.bat file in the same manner.
7)  Modify the manifest and batch file under monaco-upload in the same manner.
8)  Run the monaco-download\monaco-download.bat script to perform a download
9)  Copy a sub-folder of interest from "download_{YYYY-MM-MM-HHMMSS}\project_customer-environment" to the monaco-upload\customer-environment directory to perform an update.
10) After you are comfortable with the scripts, make a backup and optionally change all references to "customer-environment" to something that makes sense for your use case.
    This includes the manifest.yaml files, the *.bat files and the sub-directory under "monaco-upload".
    
