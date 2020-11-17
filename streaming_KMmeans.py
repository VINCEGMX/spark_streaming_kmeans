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

    initCenters_path = "s3://comp5349-vince/Kmeans_initCenters_k3_f4_10000.csv"

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

    ssc.start()
    ssc.stop(stopSparkContext=True, stopGraceFully=True)
    # $example off$

    print("Final centers: " + str(model.latestModel().clusterCenters))