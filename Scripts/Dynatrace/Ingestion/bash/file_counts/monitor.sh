#!/bin/bash
echo "Monitoring the /tmp/ingest/ directory file count every minute"
echo "Press CTRL+C to exit"
echo "Press CTRL+Z to send process to background"
while :
do
	echo tmp.ingest.file.count `ls /tmp/ingest/ | wc -l` | /opt/dynatrace/oneagent/agent/tools/dynatrace_ingest
	sleep 60
done
