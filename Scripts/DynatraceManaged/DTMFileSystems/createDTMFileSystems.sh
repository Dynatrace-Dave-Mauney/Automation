#!/bin/sh

#createDTMFileSystems.sh

#Safety Section
echo WARNING:  Any existing data in the "dtm1" logical volume will be destroyed...
echo Remove this "Safety Section" to and rerun the script to invoke the extremely dangerous commands that follow...
echo Exiting for safety reasons...
exit

#
#Create File Systems
#

#Create Logical Volumes
yes|lvcreate -n opt+managed -L 7g dtm1
yes|lvcreate -n data -L 25g dtm1
yes|lvcreate -n data+log -L 2g dtm1
yes|lvcreate -n data+cassandra -L 10g dtm1
yes|lvcreate -n data+elasticsearch -L 3g dtm1
yes|lvcreate -n data+server -L 10g dtm1
yes|lvcreate -n data+agents -L 1g dtm1
yes|lvcreate -n data+installer -L 2g dtm1
yes|lvcreate -n opt+dynatrace -L 2g dtm1

#Format File Systems
yes|mkfs.ext4 /dev/dtm1/opt+managed
yes|mkfs.ext4 /dev/dtm1/data
yes|mkfs.ext4 /dev/dtm1/data+log
yes|mkfs.ext4 /dev/dtm1/data+cassandra
yes|mkfs.ext4 /dev/dtm1/data+elasticsearch
yes|mkfs.ext4 /dev/dtm1/data+server
yes|mkfs.ext4 /dev/dtm1/data+agents
yes|mkfs.ext4 /dev/dtm1/data+installer
yes|mkfs.ext4 /dev/dtm1/opt+dynatrace

#Make parent directories
mkdir -p /opt/dynatrace-managed
mkdir -p /var/opt/dynatrace-managed
mkdir -p /opt/dynatrace

#Mount parent directories
mount /dev/dtm1/opt+managed /opt/dynatrace-managed
mount /dev/dtm1/data /var/opt/dynatrace-managed
mount /dev/dtm1/opt+dynatrace /opt/dynatrace

#Make child directories
mkdir -p /var/opt/dynatrace-managed/log
mkdir -p /var/opt/dynatrace-managed/cassandra
mkdir -p /var/opt/dynatrace-managed/elasticsearch
mkdir -p /var/opt/dynatrace-managed/server
mkdir -p /var/opt/dynatrace-managed/agents
mkdir -p /var/opt/dynatrace-managed/installer

#Mount child directories
mount /dev/dtm1/data+log /var/opt/dynatrace-managed/log
mount /dev/dtm1/data+cassandra /var/opt/dynatrace-managed/cassandra
mount /dev/dtm1/data+elasticsearch /var/opt/dynatrace-managed/elasticsearch
mount /dev/dtm1/data+server /var/opt/dynatrace-managed/server
mount /dev/dtm1/data+agents /var/opt/dynatrace-managed/agents
mount /dev/dtm1/data+installer /var/opt/dynatrace-managed/installer
