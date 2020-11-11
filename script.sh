#!/bin/sh

hdfs dfs -put Kmeans_features_k3_f4_1000.csv Kmeans_features_k3_f4_1000.csv
hdfs dfs -put Kmeans_centers_k3_f4_1000.csv Kmeans_centers_k3_f4_1000.csv

spark-submit streaming_k_means.py