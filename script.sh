#!/bin/sh

for entry in *.csv
do
	hdfs dfs -put $entry $entry
done

spark-submit streaming_KMeans.py
