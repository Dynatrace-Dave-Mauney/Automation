#!/bin/bash
echo "Writing up to 10 files to the /tmp/ingest/ directory"

rm -rf /tmp/ingest/*.txt

max=$(( ( RANDOM % 10 )  + 1 ))

echo max: $max

for i in {1..10}
do
 if (("$i" <= "$max"))
 then
  echo $i $max
  echo $i > /tmp/ingest/$i.txt
 else
  break
 fi
done


