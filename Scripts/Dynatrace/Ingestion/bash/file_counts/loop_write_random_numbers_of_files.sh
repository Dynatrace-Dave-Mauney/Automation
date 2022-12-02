#!/bin/bash
echo "Writing files to the /tmp/ingest/ directory every 45 seconds"
echo "Press CTRL+C to exit"
echo "Press CTRL+Z to send process to background"
while :
do
 ./write_random_numbers_of_files.sh
 sleep 45 
done


