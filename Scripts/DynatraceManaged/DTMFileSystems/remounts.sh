#!/bin/sh

#remounts.sh

mount /dev/dtm1/opt+managed /opt/dynatrace-managed
mount /dev/dtm1/data /var/opt/dynatrace-managed
mount /dev/dtm1/opt+dynatrace /opt/dynatrace
mount /dev/dtm1/data+log /var/opt/dynatrace-managed/log
mount /dev/dtm1/data+cassandra /var/opt/dynatrace-managed/cassandra
mount /dev/dtm1/data+elasticsearch /var/opt/dynatrace-managed/elasticsearch
mount /dev/dtm1/data+server /var/opt/dynatrace-managed/server
mount /dev/dtm1/data+agents /var/opt/dynatrace-managed/agents
mount /dev/dtm1/data+installer /var/opt/dynatrace-managed/installer
