# Overview
The purpose of this project is to simplify the adoption of Dynatrace Configuration as Code via the use of templates, examples, and so forth.

This project covers Dynatrace Configuration as Code facilitated via Monaco.

# Documentation
[Dynatrace Configuration as Code via Monaco](https://docs.dynatrace.com/docs/shortlink/configuration-as-code-monaco) 

# Random Notes (caveat: they may be out of date)
## Required Token Permissions:
### Typical Permissions
Access problem and event feed, metrics, and topology (DataExport)
Read configuration (ReadConfig)
Write configuration (WriteConfig)
Read settings (settings.read) (API v2)
Write settings (settings.write)

### More Advanced Permissions
ReadSyntheticData (Read synthetic monitors, locations, and nodes)  
slo.read (Read SLO)  
credentialVault.read (Read credential vault entries)  

