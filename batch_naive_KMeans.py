from pyspark import SparkConf, SparkContext
from pyspark.mllib.linalg import Vectors
from pyspark.mllib.clustering import KMeans,KMeansModel
from math import sqrt
from itertools import permutations

if __name__ == "__main__":
    spark_conf = SparkConf()\
        .setAppName("batch_naiveKMeans")
    sc=SparkContext.getOrCreate(spark_conf)

    num_partitions = 8

    file_size = "1GB"

    s3_folder = "s3://vince-streaming-kmeans/"
    s3_subfolder = "Kmeans_features_k3_f4_"+file_size+"/"

    feature_paths = [s3_folder + s3_subfolder + "Kmeans_k3_f4_"+file_size+"_features"]*10
    initCenters_path = s3_folder + s3_subfolder + "Kmeans_k3_f4_"+file_size+"_initCenters.csv"
    trueCenters_path = s3_folder + s3_subfolder + "Kmeans_k3_f4_"+file_size+"_centers.csv"

    trainingData = sc.textFile(feature_paths[0]+"_1.csv", num_partitions)\
        .map(lambda line: Vectors.dense([float(x) for x in line.strip().split(',')])).persist()

    rawInitCenters = sc.textFile(initCenters_path)\
        .map(lambda line: [float(x) for x in line.strip().split(',')])

    num_centers = 3
    centerWeights = [1.0]*num_centers
    initialCenters = rawInitCenters.collect()

    split_nums = 10

    entire_dataset = trainingData
    KM_naive = KMeans.train(entire_dataset,3,initialModel=KMeansModel(initialCenters))

    for i in range(1,split_nums):
        delta_data = sc.textFile(feature_paths[i]+"_"+str(i+1)+".csv", num_partitions)\
            .map(lambda line: Vectors.dense([float(x) for x in line.strip().split(',')])).persist()
        entire_dataset = entire_dataset + delta_data
        KM_naive = KMeans.train(entire_dataset,3,initialModel=KMeansModel(initialCenters))
    
    center = KM_naive.clusterCenters

    rawTrueCenters = sc.textFile(trueCenters_path)\
        .map(lambda line: [float(x) for x in line.strip().split(',')])
    trueCenters = rawTrueCenters.collect()

    permutations_trueCenters = list(permutations(trueCenters,3))
    SDs = [0] * len(permutations_trueCenters)
    for m in range(len(permutations_trueCenters)):
        temp_trueCenters = permutations_trueCenters[m]
        for n in range(len(trueCenters)):
            SDs[m] += sqrt(sum([x**2 for x in (center[n] - temp_trueCenters[n])]))
    SD = min(SDs)

    print(SD)