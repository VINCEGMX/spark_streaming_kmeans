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

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
# $example on$
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.clustering import StreamingKMeans
# $example off$

if __name__ == "__main__":
    sc = SparkContext(appName="StreamingKMeansExample")  # SparkContext
    ssc = StreamingContext(sc, 1)

    # $example on$
    # we make an input stream of vectors for training,
    # as well as a stream of vectors for testing

    trainingData = sc.textFile("./Kmeans_features_k3_f4_1000.csv")\
        .map(lambda line: Vectors.dense([float(x) for x in line.strip().split(',')]))

    # testingData = sc.textFile("./Kmeans_centers_k3_f4_1000").map(parse)

    trainingQueue = [trainingData]

    trainingStream = ssc.queueStream(trainingQueue)

    # We create a model with random clusters and specify the number of clusters to find
    model = StreamingKMeans(k=3, decayFactor=1.0).setRandomCenters(4, 1.0, 0)

    # Now register the streams for training and testing and start the job,
    # printing the predicted cluster assignments on new data points as they arrive.
    model.trainOn(trainingStream)

    ssc.start()
    ssc.stop(stopSparkContext=True, stopGraceFully=True)
    # $example off$

    print("Final centers: " + str(model.latestModel().centers))
