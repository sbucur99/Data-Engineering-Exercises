import pyspark 
from pyspark.sql import SparkSession 
spark = SparkSession.builder \
    .appName("AdvancedSparkTraining") \
    .master("local[*]") \
    .getOrCreate()


df = spark.read.csv("dates.csv", header=True, inferSchema=True)
