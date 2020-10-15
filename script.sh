#!/bin/sh

hdfs dfs -put kmeans_data.txt kmeans_data.txt
hdfs dfs -put streaming_kmeans_data_test.txt streaming_kmeans_data_test.txt

spark-submit streaming_k_means.py