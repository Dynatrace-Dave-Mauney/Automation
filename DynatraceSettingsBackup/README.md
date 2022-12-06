## DynatraceSettingsBackup

This subproject facilitates taking a backup of all Dynatrace Settings (1.0 and 2.0), as well as offering the possibility to "restore" from a backup YAML file.

Backups can be taken in two formats:  individual JSON files in subdirectories or by creating a single monolithic YAML file.

If the YAML file is created, it can later be used for restores or updates either in mass or for individual entities.

The restore process has not been fully tested, so caution is advised when using it.
