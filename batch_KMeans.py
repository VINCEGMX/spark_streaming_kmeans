from pyspark import SparkConf, SparkContext
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.clustering import KMeans,KMeansModel
from math import sqrt
from itertools import permutations

if __name__ == "__main__":
    spark_conf = SparkConf()\
        .setAppName("batch_KMeans")
    sc=SparkContext.getOrCreate(spark_conf)

    s3_folder = "s3://vince-streaming-kmeans/"
    s3_subfolder = "Kmeans_features_k3_f4_1GB/"

    feature_paths = [s3_folder + s3_subfolder + "Kmeans_features_k3_f4_1GB"]*10
    initCenters_path = s3_folder + s3_subfolder + "Kmeans_initCenters_k3_f4_1GB.csv"
    trueCenters_path = s3_folder + s3_subfolder + "Kmeans_centers_k3_f4_1GB.csv"

    trainingData = sc.textFile(feature_paths[0]+"_1.csv")\
        .map(lambda line: Vectors.dense([float(x) for x in line.strip().split(',')])).persist()

    rawInitCenters = sc.textFile(initCenters_path)\
        .map(lambda line: [float(x) for x in line.strip().split(',')])

    num_centers = 3
    centerWeights = [1.0]*num_centers
    initialCenters = rawInitCenters.collect()

    split_nums = 10

    KM = KMeans.train(trainingData,3,initialModel=KMeansModel(initialCenters))
    center = KM.clusterCenters

    trainingData.unpersist()

    for i in range(1,split_nums):
        delta_data = sc.textFile(feature_paths[i]+"_"+str(i+1)+".csv")\
            .map(lambda line: Vectors.dense([float(x) for x in line.strip().split(',')])).persist()
        KM_updated = KMeans.train(delta_data,3,initialModel=KMeansModel(center))
        center = KM_updated.clusterCenters
        delta_data.unpersist()

    rawTrueCenters = sc.textFile(trueCenters_path)\
        .map(lambda line: [float(x) for x in line.strip().split(',')])
    trueCenters = rawTrueCenters.collect()

    permutations_trueCenters = list(permutations(trueCenters,3))
    WSSSEs = [0] * len(permutations_trueCenters)
    for m in range(len(permutations_trueCenters)):
        temp_trueCenters = permutations_trueCenters[m]
        for n in range(len(trueCenters)):
            WSSSEs[m] += sqrt(sum([x**2 for x in (center[n] - temp_trueCenters[n])]))
    WSSSE = min(WSSSEs)

    print(WSSSE)