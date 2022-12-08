## DynatraceSettingsBackup

This subproject facilitates taking a backup of all Dynatrace Settings (1.0 and 2.0), as well as offering the possibility to "restore" from a backup YAML file.

Backups can be taken in two formats:  individual JSON files in subdirectories or by creating a single monolithic YAML file.

If the YAML file is created, it can later be used for restores or updates either in mass or for individual entities.

The restore process is intrinsically dangerous, so I am not committing it to the public repo.

If you have an urgent need for a restore process, please contact me at Dynatrace (dave.mauney at dynatrace dot com).
