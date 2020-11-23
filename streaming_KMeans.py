#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import csv
from math import sqrt
from itertools import permutations
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
# $example on$
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.clustering import StreamingKMeans
# $example off$

if __name__ == "__main__":
    sc = SparkContext(appName="StreamingKMeansExample")  # SparkContext
    ssc = StreamingContext(sc, 1)
    lines = ssc.socketTextStream("localhost", 9999)

    # $example on$
    # we make an input stream of vectors for training,
    # as well as a stream of vectors for testing

    # feature_path = "./"
    # initCenters_path = "./"

    # for f in os.listdir('.'):
    #     if os.path.isfile(f) and f.endswith(".csv"):
    #         if "Kmeans_features" in f:
    #             feature_path += f
    #         if "Kmeans_initCenters" in f:
    #             initCenters_path += f

    s3_folder = "s3://vince-streaming-kmeans/"
    s3_subfolder = "Kmeans_k3_f4_1GB"

    initCenters_path = s3_folder + s3_subfolder + "_initCenters.csv"
    trueCenters_path = s3_subfolder + "_centers.csv"

    trainingStream = lines.map(lambda line: Vectors.dense([float(x) for x in line.strip().split(',')]))

    # testingData = sc.textFile("./Kmeans_centers_k3_f4_1000").map(parse)

    rawInitCenters = sc.textFile(initCenters_path)\
        .map(lambda line: [float(x) for x in line.strip().split(',')])

    num_centers = 3
    centerWeights = [1.0]*num_centers
    initialCenters = rawInitCenters.collect()

    # We create a model with random clusters and specify the number of clusters to find
    model = StreamingKMeans(k=3, decayFactor=1.0).setInitialCenters(initialCenters, centerWeights)

    # Now register the streams for training and testing and start the job,
    # printing the predicted cluster assignments on new data points as they arrive.
    model.trainOn(trainingStream)

    # ssc.start()
    # checkIntervalMillis = 10
    # isStopped = False
    # stopFlag = False

    # while (~isStopped):
    #     isStopped = ssc.awaitTerminationOrTimeout(checkIntervalMillis)
    #     if (isStopped):
    #         print("confirmed! The streaming context is stopped. Exiting application...")
    #     else:
    #         print("Streaming App is still running. Timeout...")

    #     if (~stopFlag):
    #         conf = sc.hadoopConfiguration
    #         fs = org.apache.hadoop.fs.FileSystem.get(conf)
    #         stopFlag = fs.exists(org.apache.hadoop.fs.Path("script.sh"))

    #     if (~isStopped & stopFlag):
    #         print("stopping ssc right now")
    #         ssc.stop(stopSparkContext=True, stopGraceFully=True)
    #         print("Final centers: " + str(model.latestModel().clusterCenters))

    ssc.start()
    ssc.awaitTerminationOrTimeout(200)

    center = model.latestModel().clusterCenters
    trueCenters = []
    with open(trueCenters_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            point = []
            for e in row:
                point.append(float(e))
            trueCenters.append(point)

    permutations_trueCenters = list(permutations(trueCenters,3))
    WSSSEs = [0] * len(permutations_trueCenters)
    for m in range(len(permutations_trueCenters)):
        temp_trueCenters = permutations_trueCenters[m]
        for n in range(len(trueCenters)):
            WSSSEs[m] += sqrt(sum([x**2 for x in (center[n] - temp_trueCenters[n])]))
    WSSSE = min(WSSSEs)

    print("WSSSE: " + str(WSSSE))
    print("Final centers: " + str(center))