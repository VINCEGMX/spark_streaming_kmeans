import os
import csv
from math import sqrt
from itertools import permutations
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.clustering import StreamingKMeans

if __name__ == "__main__":
    sc = SparkContext(appName="StreamingKMeansExample")
    ssc = StreamingContext(sc, 1)
    lines = ssc.socketTextStream("localhost", 9999)


    s3_folder = "s3://vince-streaming-kmeans/"
    s3_subfolder = "Kmeans_k3_f4_1GB"

    initCenters_path = s3_folder + s3_subfolder + "_initCenters.csv"
    trueCenters_path = s3_subfolder + "_centers.csv"

    trainingStream = lines.map(lambda line: Vectors.dense([float(x) for x in line.strip().split(',')]))


    rawInitCenters = sc.textFile(initCenters_path)\
        .map(lambda line: [float(x) for x in line.strip().split(',')])

    num_centers = 3
    centerWeights = [1.0]*num_centers
    initialCenters = rawInitCenters.collect()

    model = StreamingKMeans(k=3, decayFactor=1.0).setInitialCenters(initialCenters, centerWeights)

    model.trainOn(trainingStream)

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
    SDs = [0] * len(permutations_trueCenters)
    for m in range(len(permutations_trueCenters)):
        temp_trueCenters = permutations_trueCenters[m]
        for n in range(len(trueCenters)):
            SDs[m] += sqrt(sum([x**2 for x in (center[n] - temp_trueCenters[n])]))
    SD = min(SDs)

    print("SD: " + str(SD))
    print("Final centers: " + str(center))