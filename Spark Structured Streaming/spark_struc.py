from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# 1. Create Spark session
spark = (
    SparkSession.builder
    .appName("KafkaStructuredStreaming")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# 2. Read streaming data from Kafka
kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "orders")
    .option("startingOffsets", "earliest")
    .load()
)

# 3. Kafka values are binary, so convert them to strings
orders_df = kafka_df.select(
    col("key").cast("string").alias("key"),
    col("value").cast("string").alias("message"),
    col("topic"),
    col("partition"),
    col("offset"),
    col("timestamp")
)

# 4. Write each micro-batch to the console
query = (
    orders_df.writeStream
    .format("console")
    .outputMode("append")
    .option("truncate", "false")
    .option("checkpointLocation", "/tmp/spark-checkpoints/orders")
    .start()
)

# 5. Keep the streaming query running
query.awaitTermination()

"""
readStream: Creates a streaming DataFrame instead of a static DataFrame.

format("kafka"): Uses Spark's Kafka connector.

subscribe = orders: Subscribes to the orders topic.

startingOffsets = earliest: For a new query, starts from the earliest available offsets.
 With checkpoint recovery, Spark uses its checkpointed progress instead.

value.cast("string"): Kafka's key and value columns are binary, so this converts the message 
payload into readable text.

writeStream: Starts writing the stream to a sink.

checkpointLocation: Stores streaming progress and recovery information.

awaitTermination(): Keeps the application running until the streaming query stops.
"""