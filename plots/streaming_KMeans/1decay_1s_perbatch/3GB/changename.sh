#!/bin/bash
node=$1
mv 'ganglia-metrics (1).csv' node$1-cpu.csv
mv 'ganglia-metrics (2).csv' node$1-mem.csv
mv 'ganglia-metrics (3).csv' node$1-load.csv
mv 'ganglia-metrics (4).csv' node$1-network.csv
