#!/bin/sh

#deleteDTMFileSystems.sh

#Safety Section
echo WARNING:  Any existing data in the "dtm1" logical volume will be destroyed...
echo Remove this "Safety Section" to and rerun the script to invoke the extremely dangerous commands that follow...
echo Exiting for safety reasons...
exit

#
#Delete File Systems
#

#Remove Directories
rm -rf /opt/dynatrace-managed
rm -rf /var/opt/dynatrace-managed
rm -rf /opt/dynatrace

#Unmount Directories 
umount /var/opt/dynatrace-managed/log
umount /var/opt/dynatrace-managed/cassandra
umount /var/opt/dynatrace-managed/elasticsearch
umount /var/opt/dynatrace-managed/server
umount /var/opt/dynatrace-managed/agents
umount /var/opt/dynatrace-managed/installer
umount /var/opt/dynatrace-managed
umount /opt/dynatrace-managed
umount /opt/dynatrace

#Remove Logical Volumes
yes|lvremove dtm1/data+log
yes|lvremove dtm1/data+cassandra
yes|lvremove dtm1/data+elasticsearch
yes|lvremove dtm1/data+server
yes|lvremove dtm1/data+agents
yes|lvremove dtm1/data+installer
yes|lvremove dtm1/data
yes|lvremove dtm1/opt+managed
yes|lvremove dtm1/opt+dynatrace
